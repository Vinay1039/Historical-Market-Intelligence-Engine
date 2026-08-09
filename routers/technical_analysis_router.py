from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from core.database import get_db_connection
from schemas.technical import TechnicalResponse, TechnicalRecord, DashboardResponse, DashboardSummary

router = APIRouter()

def row_to_technical_record(r) -> TechnicalRecord:
    return TechnicalRecord(
        symbol=r[0],
        datetime=r[1],
        open=float(r[2]) if r[2] is not None else None,
        high=float(r[3]) if r[3] is not None else None,
        low=float(r[4]) if r[4] is not None else None,
        close=float(r[5]) if r[5] is not None else None,
        change=float(r[6]) if r[6] is not None else None,
        change_percent=float(r[7]) if r[7] is not None else None,
        total_low_high=float(r[8]) if r[8] is not None else None,
        gap=r[9],
        gap_percent=float(r[10]) if r[10] is not None else None,
        total_prev_low_high=float(r[11]) if r[11] is not None else None,
        total_prev_low_high_percent=float(r[12]) if r[12] is not None else None,
        upper_wick=float(r[13]) if r[13] is not None else None,
        lower_wick=float(r[14]) if r[14] is not None else None,
        volume=int(r[15]) if r[15] is not None else None,
        low_close=float(r[16]) if r[16] is not None else None,
        high_close=float(r[17]) if r[17] is not None else None,
        previous_close=float(r[18]) if r[18] is not None else None,
        high_52w=float(r[19]) if r[19] is not None else None,
        low_52w=float(r[20]) if r[20] is not None else None,
        dist_high52=float(r[21]) if r[21] is not None else None,
        dist_low52=float(r[22]) if r[22] is not None else None,
        day_name=r[23],
        month=int(r[24]) if r[24] is not None else None,
        quarter=int(r[25]) if r[25] is not None else None,
        week=int(r[26]) if r[26] is not None else None,
        rsi_14=float(r[27]) if r[27] is not None else None,
        vwap=float(r[28]) if r[28] is not None else None,
        ema_20=float(r[29]) if r[29] is not None else None,
        ema_50=float(r[30]) if r[30] is not None else None,
        ema_100=float(r[31]) if r[31] is not None else None,
        ema_200=float(r[32]) if r[32] is not None else None,
        ema_400=float(r[33]) if r[33] is not None else None,
        ema_500=float(r[34]) if r[34] is not None else None,
        macd=float(r[35]) if r[35] is not None else None,
        macd_signal=float(r[36]) if r[36] is not None else None,
        macd_hist=float(r[37]) if r[37] is not None else None,
        macd_cross=r[38],
        macd_trend=r[39]
    )

TECHNICAL_SELECT_SQL = """
SELECT 
    SYMBOL, TO_CHAR(DATETIME, 'YYYY-MM-DD'), OPEN, HIGH, LOW, CLOSE, CHANGE, CHANGE_PERCENT,
    TOTAL_LOW_HIGH, GAP, GAP_PERCENT, TOTAL_PREV_LOW_HIGH,
    TOTAL_PREV_LOW_HIGH_PERCENT, UPPER_WICK, LOWER_WICK, VOLUME,
    LOW_CLOSE, HIGH_CLOSE, PREVIOUS_CLOSE, HIGH_52W, LOW_52W,
    DIST_HIGH52, DIST_LOW52, DAY_NAME, MONTH, QUARTER, WEEK,
    RSI_14, VWAP, EMA_20, EMA_50, EMA_100, EMA_200, EMA_400, EMA_500,
    MACD, MACD_SIGNAL, MACD_HIST, MACD_CROSS, MACD_TREND
FROM STAGING.STOCK_HIST_DATA
"""

@router.get("/technical/{symbol}", response_model=TechnicalResponse)
def get_technical_data(
    symbol: str,
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD")
):
    """
    Returns authoritatively adjusted OHLCV price series along with 40+ pre-computed technical indicators
    from STAGING.STOCK_HIST_DATA (ADR-001 compliant).
    """
    sym_upper = symbol.upper().strip()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = TECHNICAL_SELECT_SQL + " WHERE SYMBOL = :1"
        params = [sym_upper]

        if start_date:
            sql += " AND DATETIME >= TO_DATE(:2, 'YYYY-MM-DD')"
            params.append(start_date)

        if end_date:
            param_idx = len(params) + 1
            sql += f" AND DATETIME <= TO_DATE(:{param_idx}, 'YYYY-MM-DD')"
            params.append(end_date)

        sql += " ORDER BY DATETIME ASC"

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail=f"No technical indicator data found for symbol '{sym_upper}'.")

        records = [row_to_technical_record(r) for r in rows]

        return TechnicalResponse(
            symbol=sym_upper,
            count=len(records),
            data=records
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying technical indicators: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/dashboard/{symbol}", response_model=DashboardResponse)
def get_dashboard_data(symbol: str, limit: int = Query(30, ge=1, le=365)):
    """
    Returns single composite dataset required by Market Intelligence Terminal (MIT) dashboard UI.
    Includes latest summary metrics and recent history rows from STAGING.STOCK_HIST_DATA.
    """
    sym_upper = symbol.upper().strip()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = f"""
        SELECT * FROM (
            {TECHNICAL_SELECT_SQL}
            WHERE SYMBOL = :1
            ORDER BY DATETIME DESC
        ) WHERE ROWNUM <= :2
        """
        cursor.execute(sql, [sym_upper, limit])
        rows = cursor.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail=f"No dashboard data found for symbol '{sym_upper}'.")

        # Convert rows (currently DESC date order)
        records = [row_to_technical_record(r) for r in rows]
        latest = records[0]

        summary = DashboardSummary(
            symbol=sym_upper,
            latest_date=latest.datetime,
            close_price=latest.close or 0.0,
            change_percent=latest.change_percent or 0.0,
            rsi_14=latest.rsi_14,
            macd_signal=latest.macd_cross,
            high_52w=latest.high_52w,
            low_52w=latest.low_52w
        )

        # Reverse records so recent history is ASC chronological
        chronological_records = list(reversed(records))

        return DashboardResponse(
            summary=summary,
            recent_history=chronological_records
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying dashboard dataset: {str(e)}")
    finally:
        cursor.close()
        conn.close()
