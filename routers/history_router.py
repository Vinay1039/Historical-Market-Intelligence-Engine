from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from core.database import get_db_connection
from schemas.history import HistoryResponse, RawOHLCVRecord

router = APIRouter()

@router.get("/history/{symbol}", response_model=HistoryResponse)
def get_raw_history(
    symbol: str,
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD")
):
    """
    Returns the original unadjusted historical market data from STAGING.RAW_STOCK_HISTORY.
    Prices are not adjusted for corporate actions such as stock splits or bonus issues.
    """
    sym_upper = symbol.upper().strip()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """
        SELECT SYMBOL, TO_CHAR(DATETIME, 'YYYY-MM-DD') AS DT_STR, OPEN, HIGH, LOW, CLOSE, VOLUME
        FROM STAGING.RAW_STOCK_HISTORY
        WHERE SYMBOL = :1
        """
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
            raise HTTPException(status_code=404, detail=f"No raw historical data found for symbol '{sym_upper}'.")

        records = [
            RawOHLCVRecord(
                symbol=r[0],
                datetime=r[1],
                open=float(r[2]) if r[2] is not None else None,
                high=float(r[3]) if r[3] is not None else None,
                low=float(r[4]) if r[4] is not None else None,
                close=float(r[5]) if r[5] is not None else None,
                volume=int(r[6]) if r[6] is not None else None
            )
            for r in rows
        ]

        return HistoryResponse(
            symbol=sym_upper,
            count=len(records),
            data=records
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying raw stock history: {str(e)}")
    finally:
        cursor.close()
        conn.close()
