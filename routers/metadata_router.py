from fastapi import APIRouter, HTTPException, Query
from core.database import get_db_connection
from schemas.metadata import SymbolListResponse, StockSymbolItem

router = APIRouter()

@router.get("/symbols", response_model=SymbolListResponse)
def get_symbols(limit: int = Query(500, ge=1, le=2000)):
    """Fetches top N stocks by market cap from HR.STOCKS table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
        SELECT SYMBOL, COMPANY, MARKET_CAP
        FROM (
            SELECT SYMBOL, COMPANY, MARKET_CAP
            FROM HR.STOCKS
            WHERE EXCHANGE = 'NSE'
              AND MARKET_CAP IS NOT NULL
              AND SYMBOL NOT LIKE '%.%'
            ORDER BY MARKET_CAP DESC
        ) WHERE ROWNUM <= :1
        """
        cursor.execute(query, [limit])
        rows = cursor.fetchall()
        items = [
            StockSymbolItem(
                symbol=r[0],
                company=r[1],
                market_cap=float(r[2]) if r[2] is not None else None
            )
            for r in rows
        ]
        return SymbolListResponse(count=len(items), symbols=items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/search", response_model=SymbolListResponse)
def search_symbols(q: str = Query(..., min_length=1)):
    """Searches stocks by symbol or company name."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        search_pattern = f"%{q.upper()}%"
        query = """
        SELECT SYMBOL, COMPANY, MARKET_CAP
        FROM HR.STOCKS
        WHERE UPPER(SYMBOL) LIKE :1 OR UPPER(COMPANY) LIKE :2
        ORDER BY MARKET_CAP DESC NULLS LAST
        """
        cursor.execute(query, [search_pattern, search_pattern])
        rows = cursor.fetchall()
        items = [
            StockSymbolItem(
                symbol=r[0],
                company=r[1],
                market_cap=float(r[2]) if r[2] is not None else None
            )
            for r in rows
        ]
        return SymbolListResponse(count=len(items), symbols=items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database search error: {str(e)}")
    finally:
        cursor.close()
        conn.close()
