"""
===============================================================================
 HMIE Stage 10: Research Plausibility Engine (stage10_plausibility_engine.py)
 Quality Gate 3 — Validates research-design soundness of all strategy-benchmark pairs.
 Compliance: HMIE Constitution Laws 1-11 (v1.0.0 Plausibility Extension).

 This gate distinguishes:
   Engineering correctness  (QG1 — Unit Tests)
   Historical validation    (QG2 — Dual Pipeline Replay)
   Research plausibility    (QG3 — THIS FILE)

 Rules:
   UNIVERSE_IDENTICAL       → FAIL   (Strategy == Benchmark universe 100%)
   UNIVERSE_OVERLAP_HIGH    → WARNING (>80% overlap)
   UNIVERSE_OVERLAP_MEDIUM  → WARNING (50–80% overlap)
   CORR_NEAR_PERFECT        → WARNING (|r| >= 0.99)
   ALPHA_NEAR_ZERO_BETA_ONE → WARNING (|alpha| < 0.1% AND |beta - 1| < 0.05)
   TRACKING_ERROR_ZERO      → FAIL   (TE < 0.01%)
   CAGR_IDENTICAL           → WARNING (|CAGR_s - CAGR_b| < 0.01%)
   INFO_RATIO_ZERO          → WARNING (|IR| < 0.001)
===============================================================================
"""

import sys
import logging
import numpy as np
import pandas as pd
from datetime import date

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, r'c:\Users\vinay\.gemini\Fyers_Hist')
from core.database import get_db_connection

# ── Known benchmark symbol universes ─────────────────────────────────────────
BENCHMARK_UNIVERSES = {
    "NIFTY50": {
        "TCS", "INFY", "RELIANCE", "HDFCBANK", "ICICIBANK",
        "LT", "AXISBANK", "SBIN", "ITC", "BHARTIARTL"
    },
    "NIFTY500": {
        "TCS", "INFY", "RELIANCE", "HDFCBANK", "ICICIBANK",
        "LT", "AXISBANK", "SBIN", "ITC", "BHARTIARTL",
        "WIPRO", "HCLTECH", "BEL", "HAL", "RVNL"
    },
    "NIFTY_EQUAL": {
        "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
        "LT", "AXISBANK", "SBIN", "ITC", "BHARTIARTL"
    },
    "NIFTY_MOMENTUM_30": {
        "DIVISLAB", "AUROPHARMA", "LUPIN", "PIDILITIND", "BRITANNIA",
        "NTPC", "ONGC", "ASHOKLEY", "KAJARIACER", "MANAPPURAM"
    },
}

# ── Fixed-universe strategy symbol sets ───────────────────────────────────────
FIXED_STRATEGY_UNIVERSES = {
    "SECTOR_ROTATION_TOP3": {
        "TCS", "INFY", "WIPRO", "HCLTECH", "TECHM", "LTIM", "PERSISTENT", "COFORGE"
    },
    "THEME_MOMENTUM_TOP1": {
        "BEL", "HAL", "BDL", "COCHINSHIP", "MAZDOCK", "IRCTC", "RAILTEL", "RVNL"
    },
}


def jaccard_overlap(set_a: set, set_b: set) -> float:
    """Jaccard similarity: |A ∩ B| / |A ∪ B| × 100."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return round((intersection / union) * 100.0, 2) if union > 0 else 0.0


def classify_overlap(overlap_pct: float, strategy_set: set, benchmark_set: set) -> tuple:
    """Returns (rule_code, severity, recommendation)."""
    if overlap_pct >= 100.0 and strategy_set == benchmark_set:
        return (
            "UNIVERSE_IDENTICAL",
            "FAIL",
            "Strategy and benchmark share an identical symbol universe. "
            "Correlation=1.0 and Alpha=0.0 are mathematically guaranteed. "
            "Redesign the strategy universe or replace the benchmark."
        )
    elif overlap_pct > 80.0:
        return (
            "UNIVERSE_OVERLAP_HIGH",
            "WARNING",
            f"Strategy and benchmark share {overlap_pct:.1f}% of symbols (Jaccard). "
            "High overlap will suppress alpha and inflate correlation. "
            "Consider diversifying the strategy universe."
        )
    elif overlap_pct > 50.0:
        return (
            "UNIVERSE_OVERLAP_MEDIUM",
            "WARNING",
            f"Strategy and benchmark share {overlap_pct:.1f}% of symbols (Jaccard). "
            "Moderate overlap — document universe relationship in the research paper."
        )
    else:
        return (
            "UNIVERSE_OVERLAP_PASS",
            "PASS",
            f"Universe overlap is {overlap_pct:.1f}% — within acceptable range."
        )


def run_plausibility_engine(conn):
    """Execute all Quality Gate 3 plausibility rules against STAGING.STRATEGY_BENCHMARK_PERFORMANCE."""
    logger.info("--- Stage 10: Research Plausibility Engine (Quality Gate 3) ---")
    cursor = conn.cursor()

    # Clear previous audit run
    cursor.execute("TRUNCATE TABLE STAGING.PLAUSIBILITY_AUDIT")

    audit_records = []
    audit_id = 1

    # ── Load benchmark comparisons from Oracle ────────────────────────────────
    df_bench = pd.read_sql("""
        SELECT STRATEGY_CODE, BENCHMARK_CODE,
               STRATEGY_CAGR_PCT, BENCHMARK_CAGR_PCT,
               ALPHA_PCT, BETA, INFORMATION_RATIO, TRACKING_ERROR_PCT
        FROM STAGING.STRATEGY_BENCHMARK_PERFORMANCE
        ORDER BY STRATEGY_CODE, BENCHMARK_CODE
    """, conn)

    logger.info(f"    Loaded {len(df_bench)} strategy-benchmark pairs for audit")

    # ── Load algorithmic strategy universe selections ─────────────────────────
    # For TOP_STOCK_MOMENTUM_95P: get all symbols that ever appeared in the basket
    try:
        df_universe = pd.read_sql("""
            SELECT STRATEGY_CODE, SYMBOL, COUNT(*) AS MONTHS_SELECTED
            FROM STAGING.STRATEGY_MONTHLY_UNIVERSE
            GROUP BY STRATEGY_CODE, SYMBOL
        """, conn)
        algo_universes = {}
        for scode, grp in df_universe.groupby('STRATEGY_CODE'):
            algo_universes[scode] = set(grp['SYMBOL'].tolist())
        logger.info(f"    Algorithmic universe: {len(algo_universes)} strategies with dynamic selection logs")
    except Exception as e:
        logger.warning(f"    Could not load STRATEGY_MONTHLY_UNIVERSE: {e}")
        algo_universes = {}

    strategies = df_bench['STRATEGY_CODE'].unique().tolist()
    benchmarks = df_bench['BENCHMARK_CODE'].unique().tolist()

    for scode in strategies:
        # ── Determine strategy universe ──
        if scode in FIXED_STRATEGY_UNIVERSES:
            strat_universe = FIXED_STRATEGY_UNIVERSES[scode]
        elif scode in algo_universes:
            strat_universe = algo_universes[scode]
        else:
            strat_universe = set()

        for bcode in benchmarks:
            bench_universe = BENCHMARK_UNIVERSES.get(bcode, set())

            # Filter to this strategy-benchmark pair
            row = df_bench[(df_bench['STRATEGY_CODE'] == scode) & (df_bench['BENCHMARK_CODE'] == bcode)]
            if row.empty:
                continue

            alpha    = float(row['ALPHA_PCT'].iloc[0])
            beta     = float(row['BETA'].iloc[0])
            ir       = float(row['INFORMATION_RATIO'].iloc[0])
            te       = float(row['TRACKING_ERROR_PCT'].iloc[0])
            cagr_s   = float(row['STRATEGY_CAGR_PCT'].iloc[0])
            cagr_b   = float(row['BENCHMARK_CAGR_PCT'].iloc[0])

            # ── Rule 1: Universe overlap ──────────────────────────────────────
            if strat_universe and bench_universe:
                overlap_pct = jaccard_overlap(strat_universe, bench_universe)
                rule_code, severity, recommendation = classify_overlap(overlap_pct, strat_universe, bench_universe)

                audit_records.append((
                    audit_id, scode, bcode,
                    rule_code,
                    "Universe Overlap (Jaccard): strategy symbols vs benchmark symbols",
                    f"{overlap_pct:.2f}%",
                    "< 50%: PASS | 50-80%: WARNING | > 80%: WARNING | 100%: FAIL",
                    severity,
                    recommendation
                ))
                audit_id += 1

            # ── Rule 2: Near-perfect correlation proxy (Tracking Error = 0) ──
            te_abs = abs(te)
            if te_abs < 0.01:
                sev = "FAIL"
                rec = "Tracking Error is effectively zero — strategy and benchmark are identical series. Check for universe overlap."
            elif te_abs < 1.0:
                sev = "WARNING"
                rec = f"Tracking Error of {te:.4f}% is unusually low. Verify strategy has genuine active positions."
            else:
                sev = "PASS"
                rec = f"Tracking Error = {te:.2f}% — acceptable active management divergence."

            audit_records.append((
                audit_id, scode, bcode,
                "TRACKING_ERROR_CHECK",
                "Tracking Error: annualised std dev of (strategy returns - benchmark returns)",
                f"{te:.4f}%",
                "< 0.01%: FAIL | < 1.0%: WARNING | >= 1.0%: PASS",
                sev,
                rec
            ))
            audit_id += 1

            # ── Rule 3: Alpha near zero + Beta near 1 (CAPM replication) ──────
            alpha_near_zero = abs(alpha) < 0.10
            beta_near_one   = abs(beta - 1.0) < 0.05
            if alpha_near_zero and beta_near_one:
                sev = "WARNING"
                rec = (f"Alpha={alpha:+.4f}% and Beta={beta:.4f} together suggest this strategy "
                       "is replicating the benchmark rather than generating independent returns. "
                       "Investigate universe composition.")
            else:
                sev = "PASS"
                rec = f"Alpha={alpha:+.2f}% and Beta={beta:.2f} — strategy shows meaningful differentiation."

            audit_records.append((
                audit_id, scode, bcode,
                "ALPHA_BETA_REPLICATION",
                "CAPM Replication Check: |Alpha| < 0.1% AND |Beta - 1| < 0.05",
                f"Alpha={alpha:+.4f}%, Beta={beta:.4f}",
                "|Alpha| >= 0.1% OR |Beta - 1| >= 0.05 for PASS",
                sev,
                rec
            ))
            audit_id += 1

            # ── Rule 4: CAGR identical ────────────────────────────────────────
            cagr_diff = abs(cagr_s - cagr_b)
            if cagr_diff < 0.01:
                sev = "WARNING"
                rec = (f"Strategy CAGR ({cagr_s:.4f}%) and Benchmark CAGR ({cagr_b:.4f}%) "
                       "are effectively identical. Strategy provides no growth advantage.")
            else:
                sev = "PASS"
                rec = f"CAGR difference of {cagr_diff:.2f}% — meaningful performance gap exists."

            audit_records.append((
                audit_id, scode, bcode,
                "CAGR_IDENTICAL_CHECK",
                "CAGR Identical: |Strategy CAGR - Benchmark CAGR| < 0.01%",
                f"Strat={cagr_s:.4f}%, Bench={cagr_b:.4f}%, Diff={cagr_diff:.4f}%",
                "|CAGR_diff| >= 0.01% for PASS",
                sev,
                rec
            ))
            audit_id += 1

            # ── Rule 5: Information Ratio near zero ───────────────────────────
            ir_abs = abs(ir)
            if ir_abs < 0.001:
                sev = "WARNING"
                rec = (f"Information Ratio = {ir:.6f} — strategy generates no active return "
                       "above the benchmark. Risk-adjusted alpha is negligible.")
            else:
                sev = "PASS"
                rec = f"Information Ratio = {ir:.4f} — strategy demonstrates active return signal."

            audit_records.append((
                audit_id, scode, bcode,
                "INFO_RATIO_CHECK",
                "Information Ratio: mean active return / tracking error",
                f"IR = {ir:.6f}",
                "|IR| >= 0.001 for PASS",
                sev,
                rec
            ))
            audit_id += 1

        # ── Rule 6: Per-strategy — check if algorithmic universe shows diversity ──
        if scode == "TOP_STOCK_MOMENTUM_95P" and scode in algo_universes:
            unique_syms = len(algo_universes[scode])
            if unique_syms < 15:
                sev = "WARNING"
                rec = (f"Algorithmic strategy has only selected {unique_syms} unique symbols "
                       "across the entire backtest. Basket may be too concentrated.")
            elif unique_syms > 30:
                sev = "PASS"
                rec = f"Strategy selected {unique_syms} unique symbols — healthy universe diversity."
            else:
                sev = "PASS"
                rec = f"Strategy selected {unique_syms} unique symbols — acceptable diversity."

            audit_records.append((
                audit_id, scode, None,
                "ALGO_UNIVERSE_DIVERSITY",
                "Algorithmic Universe Diversity: count of unique symbols ever selected",
                f"{unique_syms} unique symbols selected across backtest",
                ">= 15 unique symbols for PASS",
                sev,
                rec
            ))
            audit_id += 1

    # ── Insert all audit records ──────────────────────────────────────────────
    cursor.executemany("""
        INSERT INTO STAGING.PLAUSIBILITY_AUDIT (
            AUDIT_ID, STRATEGY_CODE, BENCHMARK_CODE,
            RULE_CODE, RULE_DESCRIPTION,
            OBSERVED_VALUE, THRESHOLD_VALUE, SEVERITY, RECOMMENDATION
        ) VALUES (
            :1, :2, :3, :4, :5, :6, :7, :8, :9
        )
    """, audit_records)

    conn.commit()
    cursor.close()

    # ── Print summary ─────────────────────────────────────────────────────────
    fails    = [r for r in audit_records if r[7] == 'FAIL']
    warnings = [r for r in audit_records if r[7] == 'WARNING']
    passes   = [r for r in audit_records if r[7] == 'PASS']

    logger.info("\n" + "=" * 70)
    logger.info(f" QUALITY GATE 3 RESULTS: {len(audit_records)} rules evaluated")
    logger.info(f"   PASS:    {len(passes)}")
    logger.info(f"   WARNING: {len(warnings)}")
    logger.info(f"   FAIL:    {len(fails)}")
    logger.info("=" * 70)

    if fails:
        logger.warning("FAIL — Research Plausibility Gate Failed. Do not publish these results:")
        for r in fails:
            logger.warning(f"  [{r[1]} vs {r[2]}] Rule: {r[3]} | {r[5]}")

    if warnings:
        logger.info("WARNINGS (require disclosure in research paper):")
        for r in warnings:
            logger.info(f"  [{r[1]} vs {r[2]}] Rule: {r[3]} | {r[5]}")

    return len(fails) == 0


def main():
    logger.info("=" * 70)
    logger.info(" HMIE Stage 10: Research Plausibility Engine v1.0.0")
    logger.info("=" * 70)

    conn = get_db_connection()
    try:
        passed = run_plausibility_engine(conn)
        status = "ALL CHECKS PASSED" if passed else "GATE FAILED — REVIEW REQUIRED"
        logger.info(f"\n STAGE 10 COMPLETE: {status}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
