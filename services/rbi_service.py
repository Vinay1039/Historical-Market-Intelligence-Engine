import datetime
import numpy as np
import pandas as pd
from typing import Optional, List, Dict, Any
from core.database import get_db_connection

WINDOWS = [-10, -5, -3, -1, 0, 1, 3, 5, 10]

SECTOR_PROXIES = {
    "BANKING": ['HDFCBANK', 'ICICIBANK', 'AXISBANK', 'SBIN'],
    "AUTO": ['TATAMOTORS', 'MARUTI', 'M&M'],
    "IT": ['TCS', 'INFY'],
    "FMCG": ['ITC'],
    "ENERGY": ['RELIANCE']
}

NIFTY50_SYMBOLS = ['TCS', 'INFY', 'RELIANCE', 'HDFCBANK', 'ICICIBANK', 'LT', 'AXISBANK', 'SBIN', 'ITC', 'BHARTIARTL']

class RBIMonetaryService:
    def __init__(self, conn=None):
        self._external_conn = conn

    def _get_connection(self):
        if self._external_conn:
            return self._external_conn
        return get_db_connection()

    def get_rbi_events_from_oracle(self, stance: str = "ALL") -> List[Dict[str, Any]]:
        """Queries STAGING.MARKET_CALENDAR to fetch RBI Policy dates and stances from Oracle."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            if stance.upper() == "ALL":
                cur.execute("""
                SELECT EVENT_DATE, RBI_STANCE, CHANGE_BPS, EXPECTED_ACTION, STATEMENT_TONE
                FROM STAGING.MARKET_CALENDAR
                WHERE CATEGORY = 'RBI_POLICY'
                ORDER BY EVENT_DATE ASC
                """)
            else:
                cur.execute("""
                SELECT EVENT_DATE, RBI_STANCE, CHANGE_BPS, EXPECTED_ACTION, STATEMENT_TONE
                FROM STAGING.MARKET_CALENDAR
                WHERE CATEGORY = 'RBI_POLICY' AND UPPER(RBI_STANCE) = :1
                ORDER BY EVENT_DATE ASC
                """, [stance.upper()])
            
            rows = cur.fetchall()
            events = []
            for r in rows:
                events.append({
                    "event_date": r[0],
                    "stance": r[1],
                    "change_bps": float(r[2]) if r[2] is not None else 0.0,
                    "expected_action": r[3],
                    "statement_tone": r[4]
                })
            cur.close()
            return events
        finally:
            if not self._external_conn:
                conn.close()

    def calculate_rbi_metrics(self, stance: str = "ALL") -> Dict[str, Any]:
        stance = stance.upper()
        events = self.get_rbi_events_from_oracle(stance)
        if not events:
            return {"status": "SUCCESS", "stance": stance, "event_count": 0, "summary": [], "sectors": [], "champions": [], "laggards": []}

        target_dates = [pd.to_datetime(e["event_date"]) for e in events]

        conn = self._get_connection()
        try:
            # 1. Fetch complete trading dates index from Oracle
            sql_dates = """
            SELECT DISTINCT TO_CHAR(DATETIME, 'YYYY-MM-DD') AS DT
            FROM STAGING.STOCK_HIST_DATA
            WHERE SYMBOL = 'SBIN'
            ORDER BY DT ASC
            """
            df_all_dates = pd.read_sql(sql_dates, conn)
            trading_dates = pd.to_datetime(df_all_dates['DT']).tolist()

            # Find needed target dates for window offsets
            needed_dates = set()
            for event_dt in target_dates:
                valid_idx = [i for i, d in enumerate(trading_dates) if d <= event_dt]
                if not valid_idx:
                    continue
                t0_idx = valid_idx[-1]
                for w in WINDOWS:
                    target_idx = t0_idx + w
                    if 0 <= target_idx < len(trading_dates):
                        needed_dates.add(trading_dates[target_idx].strftime('%Y-%m-%d'))
            
            needed_dates_list = list(needed_dates)
            dates_str = ",".join(f"TO_DATE('{d}', 'YYYY-MM-DD')" for d in needed_dates_list)

            # 2. Fetch Nifty 50 proxy benchmark prices
            nifty_syms_str = ",".join(f"'{s}'" for s in NIFTY50_SYMBOLS)
            sql_nifty = f"""
            SELECT TO_CHAR(DATETIME, 'YYYY-MM-DD') AS DT, CLOSE
            FROM STAGING.STOCK_HIST_DATA
            WHERE SYMBOL IN ({nifty_syms_str})
              AND DATETIME IN ({dates_str})
            """
            df_nifty_raw = pd.read_sql(sql_nifty, conn)
            df_nifty_raw['DT'] = pd.to_datetime(df_nifty_raw['DT'])
            
            df_nifty = df_nifty_raw.groupby('DT')['CLOSE'].mean().reset_index().sort_values('DT').reset_index(drop=True)
            n_dates = df_nifty['DT'].tolist()
            n_prices = df_nifty['CLOSE'].tolist()

            nifty_window_rets = {w: [] for w in WINDOWS}
            for event_dt in target_dates:
                valid_idx = [i for i, d in enumerate(n_dates) if d <= event_dt]
                if not valid_idx:
                    continue
                t0_idx = valid_idx[-1]
                p0 = n_prices[t0_idx]

                for w in WINDOWS:
                    target_idx = t0_idx + w
                    if 0 <= target_idx < len(n_prices):
                        pw = n_prices[target_idx]
                        if w < 0:
                            ret = (p0 - pw) / pw * 100.0
                        elif w == 0:
                            ret = 0.0
                        else:
                            ret = (pw - p0) / p0 * 100.0
                        nifty_window_rets[w].append(ret)

            summary = []
            for w in WINDOWS:
                rets = nifty_window_rets[w]
                if rets:
                    mean_ret = float(np.mean(rets))
                    median_ret = float(np.median(rets))
                    win_rate = float(np.sum(np.array(rets) > 0)) / len(rets) * 100.0
                    volatility = float(np.std(rets, ddof=1)) if len(rets) > 1 else 0.0
                    max_gain = float(np.max(rets))
                    max_loss = float(np.min(rets))
                else:
                    mean_ret = median_ret = win_rate = volatility = max_gain = max_loss = 0.0

                summary.append({
                    "window": f"T{w:+d}" if w != 0 else "T0",
                    "offset": w,
                    "n_events": len(rets),
                    "mean_return": f"{mean_ret:+.2f}%",
                    "median_return": f"{median_ret:+.2f}%",
                    "win_rate": f"{win_rate:.1f}%",
                    "volatility": f"{volatility:.2f}%",
                    "max_gain": f"{max_gain:+.2f}%",
                    "max_loss": f"{max_loss:+.2f}%"
                })

            # 3. Sector performance
            sector_symbols = set()
            for syms in SECTOR_PROXIES.values():
                sector_symbols.update(syms)
            sector_syms_str = ",".join(f"'{s}'" for s in sector_symbols)

            sql_sectors = f"""
            SELECT SYMBOL, TO_CHAR(DATETIME, 'YYYY-MM-DD') AS DT, CLOSE
            FROM STAGING.STOCK_HIST_DATA
            WHERE SYMBOL IN ({sector_syms_str})
              AND DATETIME IN ({dates_str})
            """
            df_sec_raw = pd.read_sql(sql_sectors, conn)
            df_sec_raw['DT'] = pd.to_datetime(df_sec_raw['DT'])
            
            sym_to_sector = {s: sect for sect, syms in SECTOR_PROXIES.items() for s in syms}
            df_sec_raw['SECTOR'] = df_sec_raw['SYMBOL'].map(sym_to_sector)
            df_sec_agg = df_sec_raw.groupby(['SECTOR', 'DT'])['CLOSE'].mean().reset_index()

            sectors_res = []
            for sect_name in SECTOR_PROXIES.keys():
                df_s = df_sec_agg[df_sec_agg['SECTOR'] == sect_name].sort_values('DT').reset_index(drop=True)
                if df_s.empty:
                    continue
                s_dates = df_s['DT'].tolist()
                s_prices = df_s['CLOSE'].tolist()

                sec_rets = []
                for event_dt in target_dates:
                    valid_idx = [i for i, d in enumerate(s_dates) if d <= event_dt]
                    if not valid_idx:
                        continue
                    t0_idx = valid_idx[-1]
                    t_plus_3_idx = t0_idx + 3
                    if t_plus_3_idx < len(s_prices):
                        p0 = s_prices[t0_idx]
                        p3 = s_prices[t_plus_3_idx]
                        ret = (p3 - p0) / p0 * 100.0
                        sec_rets.append(ret)

                if sec_rets:
                    mean_ret = float(np.mean(sec_rets))
                    win_rate = float(np.sum(np.array(sec_rets) > 0)) / len(sec_rets) * 100.0
                else:
                    mean_ret = win_rate = 0.0

                sectors_res.append({
                    "sector": sect_name,
                    "mean_return": mean_ret,
                    "win_rate": f"{win_rate:.1f}%"
                })

            sectors_res = sorted(sectors_res, key=lambda x: x["mean_return"], reverse=True)
            for s in sectors_res:
                s["mean_return"] = f"{s['mean_return']:+.2f}%"

            # 4. F&O Champions/Laggards
            cur = conn.cursor()
            cur.execute("""
            SELECT DISTINCT SYMBOL FROM HR.STOCKS 
            WHERE SYMBOL IN ('ICICIBANK', 'SBIN', 'AXISBANK', 'RELIANCE', 'LT', 'BHARTIARTL', 'TATAMOTORS', 'MARUTI', 'M&M', 'POLYCAB', 'DIXON')
            """)
            fo_candidates = [r[0] for r in cur.fetchall()]
            cur.close()

            fo_syms_str = ",".join(f"'{s}'" for s in fo_candidates)
            sql_fo = f"""
            SELECT SYMBOL, TO_CHAR(DATETIME, 'YYYY-MM-DD') AS DT, CLOSE
            FROM STAGING.STOCK_HIST_DATA
            WHERE SYMBOL IN ({fo_syms_str})
              AND DATETIME IN ({dates_str})
            """
            df_fo = pd.read_sql(sql_fo, conn)
            df_fo['DT'] = pd.to_datetime(df_fo['DT'])
            
            fo_res = []
            for sym in fo_candidates:
                df_sym = df_fo[df_fo['SYMBOL'] == sym].sort_values('DT').reset_index(drop=True)
                if df_sym.empty:
                    continue
                f_dates = df_sym['DT'].tolist()
                f_prices = df_sym['CLOSE'].tolist()

                sym_rets = []
                for event_dt in target_dates:
                    valid_idx = [i for i, d in enumerate(f_dates) if d <= event_dt]
                    if not valid_idx:
                        continue
                    t0_idx = valid_idx[-1]
                    t_plus_3_idx = t0_idx + 3
                    if t_plus_3_idx < len(f_prices):
                        p0 = f_prices[t0_idx]
                        p3 = f_prices[t_plus_3_idx]
                        ret = (p3 - p0) / p0 * 100.0
                        sym_rets.append(ret)

                if sym_rets:
                    mean_ret = float(np.mean(sym_rets))
                    win_rate = float(np.sum(np.array(sym_rets) > 0)) / len(sym_rets) * 100.0
                else:
                    mean_ret = win_rate = 0.0

                fo_res.append({
                    "symbol": sym,
                    "mean_return": mean_ret,
                    "win_rate": f"{win_rate:.1f}%",
                    "n_events": len(sym_rets)
                })

            fo_res = sorted(fo_res, key=lambda x: x["mean_return"], reverse=True)
            for f in fo_res:
                f["mean_return"] = f"{f['mean_return']:+.2f}%"

            for s in sectors_res:
                s["n_events"] = len(target_dates)

            return {
                "status": "SUCCESS",
                "stance": stance,
                "event_count": len(target_dates),
                "summary": summary,
                "sectors": sectors_res,
                "champions": fo_res[:5],
                "laggards": list(reversed(fo_res[-5:]))
            }
        finally:
            if not self._external_conn:
                conn.close()

    def get_cross_stance_comparison(self) -> Dict[str, Any]:
        """Calculates side-by-side metrics across Rate Cut, Rate Pause, and Rate Hike regimes."""
        stances = ["CUT", "PAUSE", "HIKE"]
        comparison = {}
        for st in stances:
            res = self.calculate_rbi_metrics(st)
            t3_summary = next((s for s in res["summary"] if s["offset"] == 3), {})
            top_sector = res["sectors"][0]["sector"] if res["sectors"] else "N/A"
            top_sector_ret = res["sectors"][0]["mean_return"] if res["sectors"] else "0.00%"
            top_stock = res["champions"][0]["symbol"] if res["champions"] else "N/A"
            top_stock_ret = res["champions"][0]["mean_return"] if res["champions"] else "0.00%"

            comparison[st] = {
                "n_events": res["event_count"],
                "avg_return_t3": t3_summary.get("mean_return", "0.00%"),
                "win_rate_t3": t3_summary.get("win_rate", "0.0%"),
                "volatility_t3": t3_summary.get("volatility", "0.00%"),
                "best_sector": f"{top_sector} ({top_sector_ret})",
                "best_stock": f"{top_stock} ({top_stock_ret})"
            }
        return {"status": "SUCCESS", "comparison": comparison}
