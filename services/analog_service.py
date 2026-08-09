import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from core.database import get_db_connection

NIFTY50_SYMBOLS = ['TCS', 'INFY', 'RELIANCE', 'HDFCBANK', 'ICICIBANK', 'LT', 'AXISBANK', 'SBIN', 'ITC', 'BHARTIARTL']
BANKING_SYMBOLS = ['HDFCBANK', 'ICICIBANK', 'AXISBANK', 'SBIN']
OUTCOME_OFFSETS = [1, 5, 10, 30]

class AnalogService:
    def __init__(self, conn=None):
        self._external_conn = conn

    def _get_connection(self):
        if self._external_conn:
            return self._external_conn
        return get_db_connection()

    def find_analogs(self, event_type: str = "RBI", current_features: dict = None, top_n: int = 5) -> Dict[str, Any]:
        if not current_features:
            current_features = {
                "action": "PAUSE",
                "bps": 0.0,
                "cpi": 4.5,
                "regime": "SIDEWAYS",
                "tone": "NEUTRAL"
            }

        conn = self._get_connection()
        try:
            # 1. Fetch historical cases from Oracle
            cur = conn.cursor()
            cur.execute("""
            SELECT EVENT_DATE, FEATURES_JSON 
            FROM ANALYSIS.EVENT_ANALOG_CASES 
            WHERE EVENT_TYPE = :1
            ORDER BY EVENT_DATE ASC
            """, [event_type.upper()])
            
            rows = cur.fetchall()
            cur.close()

            if not rows:
                return {"status": "SUCCESS", "event_type": event_type, "top_analogs": []}

            # 2. Score similarity for each case
            scored_cases = []
            for dt_str, feat_json_str in rows:
                feat = json.loads(feat_json_str)
                score, breakdown, diffs = self._calculate_similarity(current_features, feat)
                scored_cases.append({
                    "event_date": dt_str,
                    "similarity_pct": round(score * 100.0, 1),
                    "features": feat,
                    "match_breakdown": breakdown,
                    "key_differences": diffs
                })

            # Sort by similarity_pct descending
            scored_cases = sorted(scored_cases, key=lambda x: x["similarity_pct"], reverse=True)
            top_matches = scored_cases[:top_n]

            # 3. Dynamically fetch outcomes from STAGING.STOCK_HIST_DATA for top matches
            top_dates = [m["event_date"] for m in top_matches]
            outcomes_map = self._fetch_dynamic_outcomes(conn, top_dates)

            for match in top_matches:
                dt = match["event_date"]
                match["outcomes"] = outcomes_map.get(dt, {})

            return {
                "status": "SUCCESS",
                "event_type": event_type,
                "query_features": current_features,
                "evaluated_count": len(rows),
                "top_analogs": top_matches
            }
        finally:
            if not self._external_conn:
                conn.close()

    def _calculate_similarity(self, curr: dict, hist: dict):
        # Frozen Weights Specification
        # Action (35%), BPS (20%), Regime (20%), CPI (15%), Tone (10%)
        
        # 1. Action (35%)
        curr_action = str(curr.get("action", "PAUSE")).upper()
        hist_action = str(hist.get("action", "PAUSE")).upper()
        if curr_action == hist_action:
            action_score = 1.0
            action_badge = "✅ Match"
        else:
            action_score = 0.0
            action_badge = "❌ Mismatch"

        # 2. BPS Change (20%)
        curr_bps = float(curr.get("bps", 0.0))
        hist_bps = float(hist.get("bps", 0.0))
        bps_diff = abs(curr_bps - hist_bps)
        bps_score = max(0.0, 1.0 - (bps_diff / 100.0))
        bps_badge = "✅ Match" if bps_diff == 0 else ("⚠️ Similar" if bps_diff <= 25 else "❌ Divergent")

        # 3. Market Regime (20%)
        curr_regime = str(curr.get("regime", "SIDEWAYS")).upper()
        hist_regime = str(hist.get("regime", "SIDEWAYS")).upper()
        if curr_regime == hist_regime:
            regime_score = 1.0
            regime_badge = "✅ Match"
        elif "SIDEWAYS" in (curr_regime, hist_regime):
            regime_score = 0.5
            regime_badge = "⚠️ Similar"
        else:
            regime_score = 0.0
            regime_badge = "❌ Mismatch"

        # 4. CPI Inflation (15%)
        curr_cpi = float(curr.get("cpi", 4.5))
        hist_cpi = float(hist.get("cpi", 4.5))
        cpi_diff = abs(curr_cpi - hist_cpi)
        cpi_score = max(0.0, 1.0 - (cpi_diff / 5.0))
        cpi_badge = "✅ Match" if cpi_diff <= 0.5 else ("⚠️ Similar" if cpi_diff <= 2.0 else "❌ Divergent")

        # 5. Statement Tone (10%)
        curr_tone = str(curr.get("tone", "NEUTRAL")).upper()
        hist_tone = str(hist.get("tone", "NEUTRAL")).upper()
        if curr_tone == hist_tone:
            tone_score = 1.0
            tone_badge = "✅ Match"
        else:
            tone_score = 0.0
            tone_badge = "❌ Mismatch"

        # Total Weighted Distance
        total_score = (
            0.35 * action_score +
            0.20 * bps_score +
            0.20 * regime_score +
            0.15 * cpi_score +
            0.10 * tone_score
        )

        breakdown = {
            "action": action_badge,
            "bps": bps_badge,
            "regime": regime_badge,
            "cpi": cpi_badge,
            "tone": tone_badge
        }

        diffs = []
        if curr_action != hist_action:
            diffs.append(f"Action: {curr_action} vs {hist_action}")
        if bps_diff > 0:
            diffs.append(f"BPS: {curr_bps:+.0f} vs {hist_bps:+.0f}")
        if cpi_diff > 0.5:
            diffs.append(f"CPI: {curr_cpi:.1f}% vs {hist_cpi:.1f}%")
        if curr_regime != hist_regime:
            diffs.append(f"Regime: {curr_regime} vs {hist_regime}")

        return total_score, breakdown, diffs

    def _fetch_dynamic_outcomes(self, conn, target_dates_str: List[str]) -> Dict[str, Any]:
        """Dynamically calculates T+1, T+5, T+10, T+30 outcomes from STAGING.STOCK_HIST_DATA."""
        if not target_dates_str:
            return {}

        # Fetch trading date index
        sql_dates = """
        SELECT DISTINCT TO_CHAR(DATETIME, 'YYYY-MM-DD') AS DT
        FROM STAGING.STOCK_HIST_DATA
        WHERE SYMBOL = 'SBIN'
        ORDER BY DT ASC
        """
        df_all_dates = pd.read_sql(sql_dates, conn)
        trading_dates = pd.to_datetime(df_all_dates['DT']).tolist()

        # Build needed date strings
        needed_dates = set()
        for dt_str in target_dates_str:
            event_dt = pd.to_datetime(dt_str)
            valid_idx = [i for i, d in enumerate(trading_dates) if d <= event_dt]
            if not valid_idx:
                continue
            t0_idx = valid_idx[-1]
            needed_dates.add(trading_dates[t0_idx].strftime('%Y-%m-%d'))
            for offset in OUTCOME_OFFSETS:
                target_idx = t0_idx + offset
                if target_idx < len(trading_dates):
                    needed_dates.add(trading_dates[target_idx].strftime('%Y-%m-%d'))

        dates_str = ",".join(f"TO_DATE('{d}', 'YYYY-MM-DD')" for d in list(needed_dates))
        nifty_syms_str = ",".join(f"'{s}'" for s in NIFTY50_SYMBOLS)
        bank_syms_str = ",".join(f"'{s}'" for s in BANKING_SYMBOLS)

        # Fetch Nifty prices
        sql_nifty = f"""
        SELECT TO_CHAR(DATETIME, 'YYYY-MM-DD') AS DT, CLOSE
        FROM STAGING.STOCK_HIST_DATA
        WHERE SYMBOL IN ({nifty_syms_str}) AND DATETIME IN ({dates_str})
        """
        df_n = pd.read_sql(sql_nifty, conn)
        df_n['DT'] = pd.to_datetime(df_n['DT'])
        df_nifty = df_n.groupby('DT')['CLOSE'].mean().reset_index().sort_values('DT').reset_index(drop=True)
        n_dates = df_nifty['DT'].tolist()
        n_prices = df_nifty['CLOSE'].tolist()

        # Fetch Bank Nifty prices
        sql_bank = f"""
        SELECT TO_CHAR(DATETIME, 'YYYY-MM-DD') AS DT, CLOSE
        FROM STAGING.STOCK_HIST_DATA
        WHERE SYMBOL IN ({bank_syms_str}) AND DATETIME IN ({dates_str})
        """
        df_b = pd.read_sql(sql_bank, conn)
        df_b['DT'] = pd.to_datetime(df_b['DT'])
        df_bank = df_b.groupby('DT')['CLOSE'].mean().reset_index().sort_values('DT').reset_index(drop=True)
        b_dates = df_bank['DT'].tolist()
        b_prices = df_bank['CLOSE'].tolist()

        outcomes = {}
        for dt_str in target_dates_str:
            event_dt = pd.to_datetime(dt_str)
            res = {}

            # Nifty Outcomes
            v_idx = [i for i, d in enumerate(n_dates) if d <= event_dt]
            if v_idx:
                t0_i = v_idx[-1]
                p0 = n_prices[t0_i]
                for off in OUTCOME_OFFSETS:
                    t_off_i = t0_i + off
                    if t_off_i < len(n_prices):
                        po = n_prices[t_off_i]
                        ret = (po - p0) / p0 * 100.0
                        res[f"nifty_t{off}"] = f"{ret:+.2f}%"
                    else:
                        res[f"nifty_t{off}"] = "N/A"

            # Bank Nifty Outcomes
            v_idx_b = [i for i, d in enumerate(b_dates) if d <= event_dt]
            if v_idx_b:
                t0_ib = v_idx_b[-1]
                p0b = b_prices[t0_ib]
                for off in OUTCOME_OFFSETS:
                    t_off_ib = t0_ib + off
                    if t_off_ib < len(b_prices):
                        pob = b_prices[t_off_ib]
                        ret_b = (pob - p0b) / p0b * 100.0
                        res[f"banknifty_t{off}"] = f"{ret_b:+.2f}%"
                    else:
                        res[f"banknifty_t{off}"] = "N/A"

            outcomes[dt_str] = res

        return outcomes
