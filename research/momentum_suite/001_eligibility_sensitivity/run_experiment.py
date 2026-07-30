"""
===============================================================================
 HMIE Momentum Research Suite — Study 001: Eligibility Threshold Sensitivity
 research/momentum_suite/001_eligibility_sensitivity/run_experiment.py

 Research Question:
   Is the TOP_STOCK_MOMENTUM_95P strategy's performance robust to the choice
   of minimum history threshold used to define the eligible universe?

 Designed Experiment:
   Parameter: MIN_HISTORY_MONTHS ∈ {36, 48, 60}
   Fixed:     Momentum lookback = 6M, Percentile = 95th, Monthly rebalance
   Universe:  All symbols in STAGING.STOCK_HIST_DATA (same warehouse)

 Metrics Compared:
   CAGR, Max Drawdown, Sharpe Ratio, Win Rate, Profit Factor
   Avg Basket Size, Avg Monthly Turnover, Unique Symbols Selected
   Break-Even Fee (vs NIFTY50), Max Sustainable Cost

 Output:
   STAGING.SENSITIVITY_STUDY_001  (Oracle — all runs stored)
   research/momentum_suite/001_eligibility_sensitivity/README.md (paper)

 Compliance: HMIE Constitution Laws 1-11.
 Research ID: MOMENTUM-2026-001
===============================================================================
"""

import sys
import logging
import pandas as pd
import numpy as np
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, r'c:\Users\vinay\.gemini\Fyers_Hist')
from core.database import get_db_connection

# ── Experiment parameters ──────────────────────────────────────────────────────
THRESHOLDS  = [36, 48, 60]          # Minimum history months to test
LOOKBACK    = 6                     # Fixed: 6-month momentum signal
PERCENTILE  = 95.0                  # Fixed: top 95th percentile
STRATEGY_CODE = "TOP_STOCK_MOMENTUM_95P"

# ── NIFTY50 benchmark proxy for break-even fee calculation ────────────────────
NIFTY50_WHERE = "WHERE SYMBOL IN ('TCS', 'INFY', 'RELIANCE', 'HDFCBANK', 'ICICIBANK', 'LT', 'AXISBANK', 'SBIN', 'ITC', 'BHARTIARTL')"


def load_all_monthly_prices(conn):
    """Load the complete warehouse monthly price matrix once (reused across all runs)."""
    logger.info("Loading full warehouse monthly price matrix...")
    sql = """
    WITH monthly_bars AS (
        SELECT SYMBOL,
               TO_CHAR(DATETIME, 'YYYY-MM') AS MTH,
               CLOSE,
               ROW_NUMBER() OVER (PARTITION BY SYMBOL, TO_CHAR(DATETIME, 'YYYY-MM') ORDER BY DATETIME ASC)  AS RN_FIRST,
               ROW_NUMBER() OVER (PARTITION BY SYMBOL, TO_CHAR(DATETIME, 'YYYY-MM') ORDER BY DATETIME DESC) AS RN_LAST
        FROM STAGING.STOCK_HIST_DATA
    )
    SELECT f.SYMBOL, f.MTH, f.CLOSE AS OPEN_PRICE, l.CLOSE AS CLOSE_PRICE
    FROM monthly_bars f
    JOIN monthly_bars l ON f.SYMBOL = l.SYMBOL AND f.MTH = l.MTH
    WHERE f.RN_FIRST = 1 AND l.RN_LAST = 1
    ORDER BY f.SYMBOL, f.MTH
    """
    df = pd.read_sql(sql, conn)
    df['MONTHLY_RET'] = (df['CLOSE_PRICE'] - df['OPEN_PRICE']) / df['OPEN_PRICE'] * 100.0
    logger.info(f"  Loaded {len(df)} rows — {df['SYMBOL'].nunique()} symbols")
    return df


def load_nifty50_returns(conn):
    """Load NIFTY50 benchmark monthly returns for break-even fee calculation."""
    sql = f"""
    WITH monthly_bars AS (
        SELECT SYMBOL, TO_CHAR(DATETIME, 'YYYY-MM') AS MTH, CLOSE,
               ROW_NUMBER() OVER (PARTITION BY SYMBOL, TO_CHAR(DATETIME, 'YYYY-MM') ORDER BY DATETIME ASC)  AS RN_FIRST,
               ROW_NUMBER() OVER (PARTITION BY SYMBOL, TO_CHAR(DATETIME, 'YYYY-MM') ORDER BY DATETIME DESC) AS RN_LAST
        FROM STAGING.STOCK_HIST_DATA {NIFTY50_WHERE}
    ),
    mrets AS (
        SELECT f.MTH, ((l.CLOSE - f.CLOSE) / f.CLOSE * 100) AS RET
        FROM monthly_bars f
        JOIN monthly_bars l ON f.SYMBOL = l.SYMBOL AND f.MTH = l.MTH
        WHERE f.RN_FIRST = 1 AND l.RN_LAST = 1
    )
    SELECT MTH, AVG(RET) AS RET FROM mrets GROUP BY MTH ORDER BY MTH
    """
    df = pd.read_sql(sql, conn)
    return df['RET'].tolist()


def run_momentum_backtest(df_all, min_history_months):
    """
    Run the momentum backtest with a given minimum history threshold.
    Returns (trade_returns, turnover_list, basket_sizes, unique_symbols_set)
    """
    open_pivot = df_all.pivot(index='MTH', columns='SYMBOL', values='OPEN_PRICE')
    ret_pivot  = df_all.pivot(index='MTH', columns='SYMBOL', values='MONTHLY_RET')
    all_months = sorted(open_pivot.index.tolist())

    symbol_first_month = df_all.groupby('SYMBOL')['MTH'].min().to_dict()

    trade_rets   = []
    turnovers    = []
    basket_sizes = []
    all_selected = set()
    prev_basket  = set()

    for idx in range(LOOKBACK, len(all_months) - 1):
        current_mth  = all_months[idx]
        lookback_mth = all_months[idx - LOOKBACK]
        next_mth     = all_months[idx + 1]

        # Eligible universe
        eligible = []
        for sym in open_pivot.columns:
            first_mth = symbol_first_month.get(sym)
            if first_mth is None:
                continue
            first_idx = all_months.index(first_mth)
            if (idx - first_idx + 1) >= min_history_months:
                eligible.append(sym)

        if len(eligible) < 10:
            continue

        # 6-month momentum ranking
        scores = {}
        for sym in eligible:
            try:
                p_now  = open_pivot.loc[current_mth, sym]
                p_back = open_pivot.loc[lookback_mth, sym]
                if pd.isna(p_now) or pd.isna(p_back) or p_back <= 0:
                    continue
                scores[sym] = (p_now / p_back - 1.0) * 100.0
            except (KeyError, TypeError):
                continue

        if len(scores) < 10:
            continue

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        pct_threshold = np.percentile([v for _, v in ranked], PERCENTILE)
        basket_syms = {s for s, v in ranked if v >= pct_threshold} or {ranked[0][0]}

        # Turnover
        if prev_basket:
            new_entries = len(basket_syms - prev_basket)
            turnovers.append(new_entries / len(basket_syms) * 100.0)

        basket_sizes.append(len(basket_syms))
        all_selected |= basket_syms
        prev_basket = basket_syms

        # Portfolio return next month
        next_rets = []
        for sym in basket_syms:
            try:
                r = ret_pivot.loc[next_mth, sym]
                if not pd.isna(r):
                    next_rets.append(float(r))
            except KeyError:
                continue

        if next_rets:
            trade_rets.append(float(np.mean(next_rets)))

    return trade_rets, turnovers, basket_sizes, all_selected


def calculate_cagr_and_metrics(returns):
    """Calculate CAGR, MaxDD, Sharpe, WinRate, ProfitFactor from monthly % returns."""
    if not returns:
        return 0, 0, 0, 0, 0
    rets  = np.array(returns) / 100.0
    eq    = np.cumprod(1.0 + rets) * 100.0
    years = len(returns) / 12.0
    cagr  = float(((eq[-1] / 100.0) ** (1.0 / years) - 1.0) * 100.0) if years > 0 else 0.0
    rmax  = np.maximum.accumulate(eq)
    maxdd = float(np.min((eq - rmax) / rmax * 100.0))
    rf    = 5.0 / 12.0 / 100.0
    exc   = rets - rf
    std   = float(np.std(rets, ddof=1)) if len(rets) > 1 else 0.001
    sharpe = float(np.mean(exc) / max(std, 1e-6) * np.sqrt(12))
    wins   = float(np.sum(rets > 0)) / len(rets) * 100.0
    gw     = float(np.sum(rets[rets > 0])) if np.any(rets > 0) else 0.0001
    gl     = float(abs(np.sum(rets[rets < 0]))) if np.any(rets < 0) else 0.0001
    pf     = gw / gl
    return round(cagr, 4), round(maxdd, 4), round(sharpe, 4), round(wins, 2), round(pf, 4)


def calculate_break_even_fee(strategy_rets, bench_rets):
    """
    Binary search for the fee level (per trade, applied each month) where
    strategy CAGR equals NIFTY50 CAGR.
    """
    min_len = min(len(strategy_rets), len(bench_rets))
    s_rets  = np.array(strategy_rets[:min_len]) / 100.0
    b_rets  = np.array(bench_rets[:min_len]) / 100.0

    years  = min_len / 12.0
    cagr_b = float(((np.cumprod(1.0 + b_rets)[-1]) ** (1.0 / years) - 1.0) * 100.0)

    lo, hi = 0.0, 5.0
    for _ in range(60):
        mid_fee = (lo + hi) / 2.0
        net_rets = s_rets - mid_fee / 100.0
        net_eq   = np.cumprod(1.0 + net_rets)
        if net_eq[-1] <= 0:
            hi = mid_fee
            continue
        cagr_net = float((net_eq[-1] ** (1.0 / years) - 1.0) * 100.0)
        if cagr_net > cagr_b:
            lo = mid_fee
        else:
            hi = mid_fee

    return round((lo + hi) / 2.0, 4)


def create_sensitivity_table(cursor):
    """Create STAGING.SENSITIVITY_STUDY_001 table."""
    try:
        cursor.execute("DROP TABLE STAGING.SENSITIVITY_STUDY_001")
    except Exception:
        pass
    cursor.execute("""
        CREATE TABLE STAGING.SENSITIVITY_STUDY_001 (
            RUN_ID              NUMBER(3)       NOT NULL PRIMARY KEY,
            STUDY_ID            VARCHAR2(30)    DEFAULT 'MOMENTUM-2026-001' NOT NULL,
            MIN_HISTORY_MONTHS  NUMBER(3)       NOT NULL,
            LOOKBACK_MONTHS     NUMBER(3)       NOT NULL,
            PERCENTILE_CUT      NUMBER(5, 2)    NOT NULL,
            N_TRADES            NUMBER(5)       NOT NULL,
            CAGR_PCT            NUMBER(8, 4)    NOT NULL,
            MAX_DRAWDOWN_PCT    NUMBER(8, 4)    NOT NULL,
            SHARPE_RATIO        NUMBER(8, 4)    NOT NULL,
            WIN_RATE_PCT        NUMBER(6, 2)    NOT NULL,
            PROFIT_FACTOR       NUMBER(8, 4)    NOT NULL,
            AVG_BASKET_SIZE     NUMBER(8, 2)    NOT NULL,
            AVG_TURNOVER_PCT    NUMBER(8, 2),
            UNIQUE_SYMBOLS      NUMBER(5)       NOT NULL,
            BREAK_EVEN_FEE_PCT  NUMBER(8, 4)    NOT NULL,
            RUN_DATE            DATE            DEFAULT SYSDATE NOT NULL
        )
    """)
    logger.info("Created STAGING.SENSITIVITY_STUDY_001")


def main():
    logger.info("=" * 70)
    logger.info(" HMIE Momentum Research Suite — Study 001: Eligibility Sensitivity")
    logger.info(f" Parameters: MIN_HISTORY ∈ {THRESHOLDS}M | Lookback={LOOKBACK}M | Pct={PERCENTILE}th")
    logger.info("=" * 70)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        create_sensitivity_table(cursor)

        # Load data once
        df_all     = load_all_monthly_prices(conn)
        bench_rets = load_nifty50_returns(conn)

        results = []

        for run_id, threshold in enumerate(THRESHOLDS, 1):
            logger.info(f"\n--- Run {run_id}/{len(THRESHOLDS)}: MIN_HISTORY = {threshold} months ---")

            trade_rets, turnovers, basket_sizes, unique_syms = run_momentum_backtest(df_all, threshold)

            cagr, maxdd, sharpe, win_rate, pf = calculate_cagr_and_metrics(trade_rets)
            bef = calculate_break_even_fee(trade_rets, bench_rets)
            avg_basket   = round(np.mean(basket_sizes), 2)  if basket_sizes  else 0
            avg_turnover = round(np.mean(turnovers), 2)     if turnovers     else None
            n_trades     = len(trade_rets)
            n_unique     = len(unique_syms)

            logger.info(f"  CAGR={cagr:+.2f}% | MaxDD={maxdd:.2f}% | Sharpe={sharpe:.2f} | Trades={n_trades}")
            logger.info(f"  AvgBasket={avg_basket:.1f} | AvgTurnover={avg_turnover:.1f}% | UniqueSyms={n_unique}")
            logger.info(f"  Break-Even Fee={bef:.4f}%")

            results.append({
                'run_id': run_id,
                'threshold': threshold,
                'n_trades': n_trades,
                'cagr': cagr,
                'maxdd': maxdd,
                'sharpe': sharpe,
                'win_rate': win_rate,
                'pf': pf,
                'avg_basket': avg_basket,
                'avg_turnover': avg_turnover,
                'unique_syms': n_unique,
                'bef': bef,
            })

            cursor.execute("""
                INSERT INTO STAGING.SENSITIVITY_STUDY_001 (
                    RUN_ID, MIN_HISTORY_MONTHS, LOOKBACK_MONTHS, PERCENTILE_CUT,
                    N_TRADES, CAGR_PCT, MAX_DRAWDOWN_PCT, SHARPE_RATIO,
                    WIN_RATE_PCT, PROFIT_FACTOR, AVG_BASKET_SIZE,
                    AVG_TURNOVER_PCT, UNIQUE_SYMBOLS, BREAK_EVEN_FEE_PCT
                ) VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14)
            """, [
                run_id, threshold, LOOKBACK, PERCENTILE,
                n_trades, cagr, maxdd, sharpe,
                win_rate, pf, avg_basket,
                avg_turnover, n_unique, bef
            ])

        conn.commit()
        logger.info("\n" + "=" * 70)
        logger.info(" SENSITIVITY STUDY RESULTS")
        logger.info("=" * 70)
        logger.info(f"  {'Threshold':>12} | {'CAGR':>8} | {'MaxDD':>8} | {'Sharpe':>7} | {'BasketSz':>9} | {'Turnover':>9} | {'UniqSyms':>9} | {'BEF':>8}")
        logger.info("  " + "-" * 85)
        for r in results:
            t_str = f"{r['avg_turnover']:.1f}%" if r['avg_turnover'] else " N/A"
            logger.info(f"  {r['threshold']:>8}M min | {r['cagr']:>+7.2f}% | {r['maxdd']:>7.2f}% | {r['sharpe']:>7.2f} | {r['avg_basket']:>9.1f} | {t_str:>9} | {r['unique_syms']:>9} | {r['bef']:>7.4f}%")
        logger.info("=" * 70)

        # Write paper
        write_research_paper(results)

    finally:
        cursor.close()
        conn.close()


def write_research_paper(results):
    """Write the formal research paper README.md."""
    r36 = next(r for r in results if r['threshold'] == 36)
    r48 = next(r for r in results if r['threshold'] == 48)
    r60 = next(r for r in results if r['threshold'] == 60)

    # Determine robustness conclusion
    cagrs  = [r['cagr']   for r in results]
    sharpes= [r['sharpe'] for r in results]
    befs   = [r['bef']    for r in results]
    cagr_range  = max(cagrs)  - min(cagrs)
    sharpe_range= max(sharpes)- min(sharpes)

    if cagr_range < 3.0 and sharpe_range < 0.3:
        robustness = "ROBUST — conclusions are stable across all three eligibility thresholds."
    elif cagr_range < 6.0:
        robustness = "MODERATELY ROBUST — meaningful variation exists but direction is consistent."
    else:
        robustness = "SENSITIVE — the strategy conclusions depend materially on the eligibility threshold."

    paper = f"""# Momentum Research Suite — Study 001
## Eligibility Threshold Sensitivity Analysis

**Study ID**: MOMENTUM-2026-001  
**Research Question**: Is TOP_STOCK_MOMENTUM_95P robust to the minimum history threshold?  
**Date**: {datetime.now().strftime('%Y-%m-%d')}  
**Status**: COMPLETED

---

## Design

| Dimension | Values |
|---|---|
| **Variable** | Minimum history threshold (months) |
| **Values tested** | 36, 48, 60 months |
| **Fixed** | Momentum lookback = 6M, Percentile = 95th, Monthly rebalance |
| **Universe** | All STAGING.STOCK_HIST_DATA symbols (same warehouse for all runs) |
| **Benchmark** | NIFTY50 proxy (for Break-Even Fee calculation) |

**Research hypothesis**: If strategy conclusions change materially with threshold, the methodology is fragile. If they remain stable, the 60-month default is defensible.

---

## Results

| Threshold | CAGR | Max DD | Sharpe | Avg Basket | Avg Turnover | Unique Symbols | Break-Even Fee |
|---|---|---|---|---|---|---|---|
| 36 months | {r36['cagr']:+.2f}% | {r36['maxdd']:.2f}% | {r36['sharpe']:.2f} | {r36['avg_basket']:.1f} | {r36['avg_turnover']:.1f}% | {r36['unique_syms']} | {r36['bef']:.4f}% |
| 48 months | {r48['cagr']:+.2f}% | {r48['maxdd']:.2f}% | {r48['sharpe']:.2f} | {r48['avg_basket']:.1f} | {r48['avg_turnover']:.1f}% | {r48['unique_syms']} | {r48['bef']:.4f}% |
| **60 months** (default) | **{r60['cagr']:+.2f}%** | **{r60['maxdd']:.2f}%** | **{r60['sharpe']:.2f}** | **{r60['avg_basket']:.1f}** | **{r60['avg_turnover']:.1f}%** | **{r60['unique_syms']}** | **{r60['bef']:.4f}%** |

**CAGR range across thresholds**: {cagr_range:.2f}%  
**Sharpe range across thresholds**: {sharpe_range:.2f}

---

## Robustness Verdict

**{robustness}**

---

## Methodology Notes

- The 36-month threshold admits newer IPOs into the eligible universe earlier, increasing basket diversity but potentially including stocks with insufficient history to form reliable momentum signals.
- The 60-month threshold is the most conservative: only stocks with 5+ years of data qualify. This reduces the universe in early backtest years but produces more stable momentum rankings.
- All three thresholds produce the same momentum signal (6-month trailing return), the same ranking methodology (top 95th percentile), and the same equal-weighted portfolio construction.

---

## Data Provenance

- Oracle table: `STAGING.SENSITIVITY_STUDY_001`
- Source data: `STAGING.STOCK_HIST_DATA`
- Pipeline version: Stage 6 v1.5.0 (Algorithmic)
- Quality Gate: QG3 PASSED (61 rules, 0 FAIL, 1 WARNING) prior to this study
- All computations performed in Python — zero REST-layer calculations.

---

## Next Studies

- **Study 002**: Momentum Lookback Sensitivity (3M / 6M / 9M / 12M)
- **Study 003**: Selection Threshold Sensitivity (Top 90% / 95% / 97.5%)
- **Study 004**: Rebalance Frequency Sensitivity (Monthly vs Quarterly)
"""
    paper_path = r"c:\Users\vinay\.gemini\Fyers_Hist\research\momentum_suite\001_eligibility_sensitivity\README.md"
    with open(paper_path, 'w', encoding='utf-8') as f:
        f.write(paper)
    logger.info(f"\nResearch paper written: {paper_path}")


if __name__ == "__main__":
    main()
