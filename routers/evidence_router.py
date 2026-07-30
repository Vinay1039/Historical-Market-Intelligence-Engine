from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from core.database import get_db_connection
from schemas.evidence import (
    CorrectionResponse, CorrectionRecord,
    MacroEventResponse, MacroEventRecord,
    RecoveryStatsResponse
)

router = APIRouter()

@router.get("/evidence/corrections", response_model=CorrectionResponse)
def get_corrections_evidence():
    """Returns precomputed historical market drawdown and recovery evidence over 15+ years."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        SELECT 
            EVENT_ID, EVENT_NAME, TO_CHAR(PEAK_DATE, 'YYYY-MM-DD'), TO_CHAR(TROUGH_DATE, 'YYYY-MM-DD'),
            TO_CHAR(RECOVERY_DATE, 'YYYY-MM-DD'), MAX_DRAWDOWN_PCT, CORRECTION_DAYS, RECOVERY_DAYS,
            RECOVERY_TYPE, TOP_SECTOR_30D, TOP_SECTOR_60D, TOP_THEME_60D
        FROM STAGING.EVIDENCE_CORRECTIONS
        ORDER BY PEAK_DATE ASC
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        data = [
            CorrectionRecord(
                event_id=int(r[0]), event_name=r[1], peak_date=r[2], trough_date=r[3],
                recovery_date=r[4], max_drawdown_pct=float(r[5]), correction_days=int(r[6]),
                recovery_days=int(r[7]) if r[7] is not None else None, recovery_type=r[8],
                top_sector_30d=r[9], top_sector_60d=r[10], top_theme_60d=r[11]
            )
            for r in rows
        ]
        return CorrectionResponse(count=len(data), data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/evidence/macro-events", response_model=MacroEventResponse)
def get_macro_events_evidence(category: Optional[str] = Query(None, description="BUDGET, ELECTION, CRISIS")):
    """Returns precomputed macro event evidence (Union Budgets, Elections, Crises)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        SELECT 
            EVENT_ID, EVENT_NAME, EVENT_CATEGORY, TO_CHAR(EVENT_DATE, 'YYYY-MM-DD'), REGIME_AT_EVENT,
            PRE_30D_MARKET_RETURN, POST_30D_MARKET_RETURN, TOP_SECTOR_POST_30D, TOP_THEME_POST_30D
        FROM STAGING.EVIDENCE_MACRO_EVENTS
        """
        params = []
        if category:
            sql += " WHERE UPPER(EVENT_CATEGORY) = :1"
            params.append(category.upper().strip())

        sql += " ORDER BY EVENT_DATE ASC"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        data = [
            MacroEventRecord(
                event_id=int(r[0]), event_name=r[1], event_category=r[2], event_date=r[3],
                regime_at_event=r[4], pre_30d_market_return=float(r[5]), post_30d_market_return=float(r[6]),
                top_sector_post_30d=r[7], top_theme_post_30d=r[8]
            )
            for r in rows
        ]
        return MacroEventResponse(count=len(data), data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/evidence/recovery-stats", response_model=RecoveryStatsResponse)
def get_recovery_stats():
    """Returns aggregate historical recovery duration distributions and top recovering sector statistics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) AS TOTAL,
                ROUND(AVG(MAX_DRAWDOWN_PCT), 2) AS AVG_DD,
                ROUND(AVG(CORRECTION_DAYS), 1) AS AVG_CORR_DAYS,
                ROUND(AVG(RECOVERY_DAYS), 1) AS AVG_REC_DAYS,
                SUM(CASE WHEN RECOVERY_TYPE = 'V_SHAPED' THEN 1 ELSE 0 END) AS V_CNT,
                SUM(CASE WHEN RECOVERY_TYPE = 'U_SHAPED' THEN 1 ELSE 0 END) AS U_CNT
            FROM STAGING.EVIDENCE_CORRECTIONS
            WHERE RECOVERY_DATE IS NOT NULL
        """)
        r = cursor.fetchone()

        cursor.execute("""
            SELECT * FROM (
                SELECT TOP_SECTOR_60D, COUNT(*) AS FREQ
                FROM STAGING.EVIDENCE_CORRECTIONS
                GROUP BY TOP_SECTOR_60D
                ORDER BY FREQ DESC
            ) WHERE ROWNUM = 1
        """)
        top_sec = cursor.fetchone()[0]

        return RecoveryStatsResponse(
            total_corrections=int(r[0]),
            avg_drawdown_pct=float(r[1]),
            avg_correction_days=float(r[2]),
            avg_recovery_days=float(r[3]),
            v_shaped_count=int(r[4]),
            u_shaped_count=int(r[5]),
            most_frequent_recovering_sector_60d=top_sec
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()
