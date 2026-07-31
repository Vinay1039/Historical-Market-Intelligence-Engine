from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from core.database import get_db_connection
from schemas.strategy import (
    StrategySummaryResponse, StrategySummaryRecord,
    TradeResponse, TradeRecord,
    BenchmarkPerformanceResponse, BenchmarkPerformanceRecord,
    FeeSensitivityResponse, FeeSensitivityRecord,
    PlausibilityAuditResponse, PlausibilityAuditRecord,
    CanonicalResearchResponse, CanonicalResearchRecord
)

router = APIRouter()

@router.get("/strategy/summary", response_model=StrategySummaryResponse)
def get_strategy_summary():
    """Returns precomputed 15-year quantitative strategy backtest performance summary metrics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        SELECT 
            STRATEGY_ID, STRATEGY_CODE, STRATEGY_NAME, BENCHMARK,
            TO_CHAR(START_DATE, 'YYYY-MM-DD'), TO_CHAR(END_DATE, 'YYYY-MM-DD'),
            TOTAL_RETURN_PCT, CAGR_PCT, MAX_DRAWDOWN_PCT, WIN_RATE_PCT,
            SHARPE_RATIO, PROFIT_FACTOR, TOTAL_TRADES
        FROM STAGING.STRATEGY_PERFORMANCE
        ORDER BY STRATEGY_ID ASC
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        data = [
            StrategySummaryRecord(
                strategy_id=int(r[0]), strategy_code=r[1], strategy_name=r[2], benchmark=r[3],
                start_date=r[4], end_date=r[5], total_return_pct=float(r[6]), cagr_pct=float(r[7]),
                max_drawdown_pct=float(r[8]), win_rate_pct=float(r[9]), sharpe_ratio=float(r[10]),
                profit_factor=float(r[11]), total_trades=int(r[12])
            )
            for r in rows
        ]
        return StrategySummaryResponse(count=len(data), data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/strategy/trades", response_model=TradeResponse)
def get_strategy_trades(
    strategy_code: Optional[str] = Query(None, description="SECTOR_ROTATION_TOP3, THEME_MOMENTUM_TOP1, TOP_STOCK_MOMENTUM_95P"),
    limit: int = Query(50, ge=1, le=500)
):
    """Returns individual trade logs for quantitative strategy backtests."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        SELECT 
            TRADE_ID, STRATEGY_CODE, SYMBOL_OR_CODE,
            TO_CHAR(ENTRY_DATE, 'YYYY-MM-DD'), TO_CHAR(EXIT_DATE, 'YYYY-MM-DD'),
            HOLDING_DAYS, ENTRY_PRICE, EXIT_PRICE, RETURN_PCT, WIN_FLAG
        FROM STAGING.STRATEGY_TRADES
        """
        params = []
        if strategy_code:
            sql += " WHERE UPPER(STRATEGY_CODE) = :1"
            params.append(strategy_code.upper().strip())

        sql += " ORDER BY ENTRY_DATE DESC FETCH FIRST :2 ROWS ONLY"
        params.append(limit)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        data = [
            TradeRecord(
                trade_id=int(r[0]), strategy_code=r[1], symbol_or_code=r[2],
                entry_date=r[3], exit_date=r[4], holding_days=int(r[5]),
                entry_price=float(r[6]), exit_price=float(r[7]), return_pct=float(r[8]),
                win_flag=int(r[9])
            )
            for r in rows
        ]
        return TradeResponse(count=len(data), data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/strategy/benchmarks", response_model=BenchmarkPerformanceResponse)
def get_strategy_benchmarks(
    strategy_code: Optional[str] = Query(None, description="SECTOR_ROTATION_TOP3, THEME_MOMENTUM_TOP1, TOP_STOCK_MOMENTUM_95P")
):
    """Returns precomputed strategy relative performance metrics (Alpha, Beta, Volatility, InfoRatio) vs benchmark indices."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        SELECT 
            STRATEGY_CODE, BENCHMARK_CODE, BENCHMARK_NAME,
            STRATEGY_CAGR_PCT, BENCHMARK_CAGR_PCT, STRATEGY_VOLATILITY_PCT, BENCHMARK_VOLATILITY_PCT,
            ALPHA_PCT, BETA, INFORMATION_RATIO, TRACKING_ERROR_PCT
        FROM STAGING.STRATEGY_BENCHMARK_PERFORMANCE
        """
        params = []
        if strategy_code:
            sql += " WHERE UPPER(STRATEGY_CODE) = :1"
            params.append(strategy_code.upper().strip())

        sql += " ORDER BY STRATEGY_CODE ASC, BENCHMARK_CODE ASC"

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        data = [
            BenchmarkPerformanceRecord(
                strategy_code=r[0], benchmark_code=r[1], benchmark_name=r[2],
                strategy_cagr_pct=float(r[3]), benchmark_cagr_pct=float(r[4]),
                strategy_volatility_pct=float(r[5]), benchmark_volatility_pct=float(r[6]),
                alpha_pct=float(r[7]), beta=float(r[8]), information_ratio=float(r[9]),
                tracking_error_pct=float(r[10])
            )
            for r in rows
        ]
        return BenchmarkPerformanceResponse(count=len(data), data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/strategy/fee-sensitivity", response_model=FeeSensitivityResponse)
def get_strategy_fee_sensitivity(
    strategy_code: Optional[str] = Query(None, description="SECTOR_ROTATION_TOP3, THEME_MOMENTUM_TOP1, TOP_STOCK_MOMENTUM_95P")
):
    """Returns precomputed strategy performance metrics across transaction fee friction levels (0.0%, 0.10%, 0.25%, 0.50%)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        SELECT 
            STRATEGY_CODE, FEE_LEVEL_PCT, NET_TOTAL_RETURN_PCT, NET_CAGR_PCT,
            NET_MAX_DRAWDOWN_PCT, NET_SHARPE_RATIO, NET_PROFIT_FACTOR, CAGR_DRAG_PCT,
            BREAK_EVEN_FEE_PCT, MAX_SUSTAINABLE_COST_PCT, ROBUSTNESS_CLASSIFICATION
        FROM STAGING.STRATEGY_FEE_SENSITIVITY
        """
        params = []
        if strategy_code:
            sql += " WHERE UPPER(STRATEGY_CODE) = :1"
            params.append(strategy_code.upper().strip())

        sql += " ORDER BY STRATEGY_CODE ASC, FEE_LEVEL_PCT ASC"

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        data = [
            FeeSensitivityRecord(
                strategy_code=r[0], fee_level_pct=float(r[1]),
                net_total_return_pct=float(r[2]), net_cagr_pct=float(r[3]),
                net_max_drawdown_pct=float(r[4]), net_sharpe_ratio=float(r[5]),
                net_profit_factor=float(r[6]), cagr_drag_pct=float(r[7]),
                break_even_fee_pct=float(r[8]) if r[8] is not None else None,
                max_sustainable_cost_pct=float(r[9]) if r[9] is not None else None,
                robustness_classification=r[10]
            )
            for r in rows
        ]
        return FeeSensitivityResponse(count=len(data), data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/strategy/plausibility-audit", response_model=PlausibilityAuditResponse)
def get_plausibility_audit(
    severity: Optional[str] = Query(None, description="Filter by severity: PASS, WARNING, FAIL"),
    strategy_code: Optional[str] = Query(None, description="Filter by strategy code")
):
    """
    Quality Gate 3 — Research Plausibility Engine results.
    Returns all rule evaluations from STAGING.PLAUSIBILITY_AUDIT.
    gate_passed=true only when fail_count == 0.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conditions = []
        params = []
        if severity:
            conditions.append("SEVERITY = :sev")
            params.append(severity.upper())
        if strategy_code:
            conditions.append("STRATEGY_CODE = :scode")
            params.append(strategy_code.upper())

        where_sql = "WHERE " + " AND ".join(conditions) if conditions else ""
        sql = f"""
            SELECT AUDIT_ID, TO_CHAR(RUN_DATE, 'YYYY-MM-DD'), STRATEGY_CODE, BENCHMARK_CODE,
                   RULE_CODE, RULE_DESCRIPTION, OBSERVED_VALUE, THRESHOLD_VALUE,
                   SEVERITY, RECOMMENDATION
            FROM STAGING.PLAUSIBILITY_AUDIT
            {where_sql}
            ORDER BY AUDIT_ID ASC
        """
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        data = [
            PlausibilityAuditRecord(
                audit_id=int(r[0]),
                run_date=r[1],
                strategy_code=r[2],
                benchmark_code=r[3],
                rule_code=r[4],
                rule_description=r[5],
                observed_value=r[6],
                threshold_value=r[7],
                severity=r[8],
                recommendation=r[9]
            )
            for r in rows
        ]
        # Count summaries over all records (not filtered) for gate_passed determination
        cursor.execute("SELECT COUNT(*) FROM STAGING.PLAUSIBILITY_AUDIT WHERE SEVERITY = 'FAIL'")
        fail_count_total = int(cursor.fetchone()[0])
        cursor.execute("SELECT COUNT(*) FROM STAGING.PLAUSIBILITY_AUDIT WHERE SEVERITY = 'WARNING'")
        warn_count_total = int(cursor.fetchone()[0])
        cursor.execute("SELECT COUNT(*) FROM STAGING.PLAUSIBILITY_AUDIT WHERE SEVERITY = 'PASS'")
        pass_count_total = int(cursor.fetchone()[0])

        return PlausibilityAuditResponse(
            total_rules_evaluated=fail_count_total + warn_count_total + pass_count_total,
            pass_count=pass_count_total,
            warning_count=warn_count_total,
            fail_count=fail_count_total,
            gate_passed=(fail_count_total == 0),
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/research/canonical-studies", response_model=CanonicalResearchResponse)
def get_canonical_research_studies(
    study_id: Optional[str] = Query(None, description="Filter by study ID")
):
    """
    Research Governance Layer — Returns authoritative canonical research executions.
    Enforces the Canonical Result Policy (only executions with CANONICAL_FLAG=1 are returned by default).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        where_sql = "WHERE CANONICAL_FLAG = 1"
        params = []
        if study_id:
            where_sql += " AND STUDY_ID = :sid"
            params.append(study_id.upper())

        sql = f"""
            SELECT EXECUTION_ID, STUDY_ID, STUDY_NAME, METHODOLOGY_VERSION,
                   DATASET_VERSION, GIT_COMMIT, TO_CHAR(EXECUTION_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS'),
                   CANONICAL_FLAG, EXECUTION_HASH, RESULT_HASH, SUMMARY_METRICS_JSON,
                   LIMITATIONS_JSON, SUPERSEDES_EXEC_ID
            FROM STAGING.RESEARCH_EXECUTIONS
            {where_sql}
            ORDER BY EXECUTION_ID ASC
        """
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        data = [
            CanonicalResearchRecord(
                execution_id=int(r[0]),
                study_id=r[1],
                study_name=r[2],
                methodology_version=r[3],
                dataset_version=r[4],
                git_commit=r[5],
                execution_timestamp=r[6],
                canonical_flag=int(r[7]),
                execution_hash=r[8],
                result_hash=r[9],
                summary_metrics_json=r[10],
                limitations_json=r[11],
                supersedes_exec_id=int(r[12]) if r[12] is not None else None
            )
            for r in rows
        ]
        return CanonicalResearchResponse(count=len(data), data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

from pydantic import BaseModel
class AIQueryRequest(BaseModel):
    query: str

@router.post("/research/query")
def query_research_engine(req: AIQueryRequest):
    """
    HMIE 2.0 AI Evidence Engine — Natural Language Research Query Endpoint.
    Parses intent/entities, traverses canonical evidence graph, ranks evidence,
    and returns traceable answers with study IDs, execution IDs, and hashes.
    """
    import time, datetime
    start_time = time.time()
    from core.ai_evidence_engine import HMIEResearchEngine, close_engine
    engine = HMIEResearchEngine()
    result = None
    status = "SUCCESS"
    try:
        result = engine.query_evidence(req.query)
        return result
    except Exception as e:
        status = "SYSTEM_ERROR"
        raise e
    finally:
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        close_engine(engine)

        # Silent, Non-Blocking Operational Telemetry Logging
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
            intent = result.get("intent", "UNKNOWN") if result else "ERROR"
            mode = result.get("mode", "UNKNOWN") if result else "ERROR"
            
            # Infer event source
            q_text = req.query.strip()
            source = "SEARCH_BOX"
            if any(k in q_text for k in ["Compare Independence Day", "Which Auto stocks performed best on Independence"]):
                source = "EXPLORE_BUTTON"

            cursor.execute("""
                INSERT INTO STAGING.QUERY_LOGS (QUERY_ID, QUERY_TIME, QUERY_TEXT, INTENT, ENGINE_MODE, RESPONSE_STATUS, RESPONSE_MS, EVENT_SOURCE)
                VALUES (STAGING.QUERY_LOGS_SEQ.NEXTVAL, :1, :2, :3, :4, :5, :6, :7)
            """, (query_time, q_text[:1000], intent, mode, status, elapsed_ms, source))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception:
            pass  # Logging must never block user research

@router.get("/research/study/{study_id}")
def get_study_details(study_id: str):
    """
    HMIE 2.0 Study Retrieval Endpoint.
    Returns detailed canonical research record, execution provenance, and summary metrics.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
            SELECT EXECUTION_ID, STUDY_ID, STUDY_NAME, METHODOLOGY_VERSION,
                   DATASET_VERSION, GIT_COMMIT, TO_CHAR(EXECUTION_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS'),
                   CANONICAL_FLAG, EXECUTION_HASH, RESULT_HASH, SUMMARY_METRICS_JSON,
                   LIMITATIONS_JSON, SUPERSEDES_EXEC_ID
            FROM STAGING.RESEARCH_EXECUTIONS
            WHERE UPPER(STUDY_ID) = :1 AND CANONICAL_FLAG = 1
        """
        cursor.execute(sql, [study_id.upper().strip()])
        r = cursor.fetchone()
        if not r:
            raise HTTPException(status_code=404, detail=f"Canonical study {study_id} not found.")
        return {
            "execution_id": int(r[0]),
            "study_id": r[1],
            "study_name": r[2],
            "methodology_version": r[3],
            "dataset_version": r[4],
            "git_commit": r[5],
            "execution_timestamp": r[6],
            "canonical_flag": int(r[7]),
            "execution_hash": r[8],
            "result_hash": r[9],
            "summary_metrics": r[10],
            "limitations": r[11],
            "supersedes_exec_id": int(r[12]) if r[12] is not None else None
        }
    finally:
        cursor.close()
        conn.close()


