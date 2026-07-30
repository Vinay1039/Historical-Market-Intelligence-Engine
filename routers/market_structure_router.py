from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from core.database import get_db_connection
from services.ai_research_agent import generate_market_narrative
from schemas.market_structure import (
    SectorListResponse, SectorItem,
    IndustryListResponse, IndustryItem,
    DailyAggregationResponse, DailyAggregationRecord,
    MarketBreadthResponse, MarketBreadthRecord,
    PerformanceResponse, PerformanceRecord,
    RotationResponse, RotationRecord,
    StockRankingResponse, StockRankingRecord,
    ThemeListResponse, ThemeItem,
    ThemeRotationResponse, ThemeRotationRecord,
    RegimeResponse, RegimeRecord,
    RegimeSummaryResponse, RegimeSummaryItem,
    AINarrativeRequest, AINarrativeResponse
)

router = APIRouter()

@router.post("/market-structure/ai/narrate", response_model=AINarrativeResponse)
def narrate_market_structure(req: AINarrativeRequest):
    """Generates an evidence-backed markdown research narrative adhering to Constitution Law #8."""
    try:
        res = generate_market_narrative(req.prompt, req.target_date)
        return AINarrativeResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Research Agent error: {str(e)}")

@router.get("/market-structure/sectors", response_model=SectorListResponse)
def get_sectors():
    """Returns list of all 20 sectors with stock count and total market cap."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
        SELECT SECTOR_CODE, SECTOR_NAME, STOCK_COUNT, TOTAL_MARKET_CAP
        FROM STAGING.SECTOR_MASTER
        ORDER BY TOTAL_MARKET_CAP DESC NULLS LAST
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        sectors = [
            SectorItem(
                sector_code=r[0],
                sector_name=r[1],
                stock_count=int(r[2]) if r[2] is not None else 0,
                total_market_cap=float(r[3]) if r[3] is not None else None
            )
            for r in rows
        ]
        return SectorListResponse(count=len(sectors), sectors=sectors)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error fetching sectors: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/market-structure/industries", response_model=IndustryListResponse)
def get_industries(sector_code: Optional[str] = Query(None, description="Optional sector code filter (e.g. FINANCE)")):
    """Returns list of industries, optionally filtered by sector code."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        SELECT INDUSTRY_CODE, INDUSTRY_NAME, SECTOR_CODE, STOCK_COUNT, TOTAL_MARKET_CAP
        FROM STAGING.INDUSTRY_MASTER
        """
        params = []
        if sector_code:
            sql += " WHERE SECTOR_CODE = :1"
            params.append(sector_code.upper().strip())
        
        sql += " ORDER BY TOTAL_MARKET_CAP DESC NULLS LAST"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        industries = [
            IndustryItem(
                industry_code=r[0],
                industry_name=r[1],
                sector_code=r[2],
                stock_count=int(r[3]) if r[3] is not None else 0,
                total_market_cap=float(r[4]) if r[4] is not None else None
            )
            for r in rows
        ]
        return IndustryListResponse(count=len(industries), industries=industries)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error fetching industries: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/market-structure/breadth/market", response_model=MarketBreadthResponse)
def get_market_breadth(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD")
):
    """Returns market-wide daily breadth metrics across all 2,234 NSE stocks."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        SELECT 
            TO_CHAR(DATETIME, 'YYYY-MM-DD'), TOTAL_STOCKS, ADVANCING_STOCKS, DECLINING_STOCKS, UNCHANGED_STOCKS,
            BREADTH_RATIO, NET_ADVANCES, PCT_ABOVE_EMA20, PCT_ABOVE_EMA50, PCT_ABOVE_EMA200
        FROM STAGING.MARKET_BREADTH_DAILY
        """
        params = []
        if start_date:
            sql += " WHERE DATETIME >= TO_DATE(:1, 'YYYY-MM-DD')"
            params.append(start_date)
        if end_date:
            param_idx = len(params) + 1
            clause = "WHERE" if not params else "AND"
            sql += f" {clause} DATETIME <= TO_DATE(:{param_idx}, 'YYYY-MM-DD')"
            params.append(end_date)

        sql += " ORDER BY DATETIME ASC"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        data = [
            MarketBreadthRecord(
                datetime=r[0],
                total_stocks=int(r[1]),
                advancing_stocks=int(r[2]),
                declining_stocks=int(r[3]),
                unchanged_stocks=int(r[4]),
                breadth_ratio=float(r[5]) if r[5] is not None else None,
                net_advances=int(r[6]),
                pct_above_ema20=float(r[7]) if r[7] is not None else None,
                pct_above_ema50=float(r[8]) if r[8] is not None else None,
                pct_above_ema200=float(r[9]) if r[9] is not None else None
            )
            for r in rows
        ]
        return MarketBreadthResponse(count=len(data), data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error fetching market breadth: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/market-structure/regimes/current", response_model=RegimeRecord)
def get_current_regime():
    """Returns the latest market regime and active duration."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        SELECT 
            TO_CHAR(DATETIME, 'YYYY-MM-DD'), REGIME_NAME, PCT_ABOVE_EMA20, PCT_ABOVE_EMA50, PCT_ABOVE_EMA200,
            BREADTH_RATIO, NET_ADVANCES, AVG_MARKET_RETURN_PCT, REGIME_DURATION_DAYS
        FROM STAGING.MARKET_REGIMES
        WHERE DATETIME = (SELECT MAX(DATETIME) FROM STAGING.MARKET_REGIMES)
        """
        cursor.execute(sql)
        r = cursor.fetchone()
        if not r:
            raise HTTPException(status_code=404, detail="No market regime data found.")
        return RegimeRecord(
            datetime=r[0], regime_name=r[1],
            pct_above_ema20=float(r[2]) if r[2] is not None else None,
            pct_above_ema50=float(r[3]) if r[3] is not None else None,
            pct_above_ema200=float(r[4]) if r[4] is not None else None,
            breadth_ratio=float(r[5]) if r[5] is not None else None,
            net_advances=int(r[6]) if r[6] is not None else None,
            avg_market_return_pct=float(r[7]) if r[7] is not None else None,
            regime_duration_days=int(r[8])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/market-structure/regimes/timeline", response_model=RegimeResponse)
def get_regime_timeline(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD")
):
    """Returns historical market regime time-series."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        SELECT 
            TO_CHAR(DATETIME, 'YYYY-MM-DD'), REGIME_NAME, PCT_ABOVE_EMA20, PCT_ABOVE_EMA50, PCT_ABOVE_EMA200,
            BREADTH_RATIO, NET_ADVANCES, AVG_MARKET_RETURN_PCT, REGIME_DURATION_DAYS
        FROM STAGING.MARKET_REGIMES
        """
        params = []
        if start_date:
            sql += " WHERE DATETIME >= TO_DATE(:1, 'YYYY-MM-DD')"
            params.append(start_date)
        if end_date:
            param_idx = len(params) + 1
            clause = "WHERE" if not params else "AND"
            sql += f" {clause} DATETIME <= TO_DATE(:{param_idx}, 'YYYY-MM-DD')"
            params.append(end_date)

        sql += " ORDER BY DATETIME ASC"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        data = [
            RegimeRecord(
                datetime=r[0], regime_name=r[1],
                pct_above_ema20=float(r[2]) if r[2] is not None else None,
                pct_above_ema50=float(r[3]) if r[3] is not None else None,
                pct_above_ema200=float(r[4]) if r[4] is not None else None,
                breadth_ratio=float(r[5]) if r[5] is not None else None,
                net_advances=int(r[6]) if r[6] is not None else None,
                avg_market_return_pct=float(r[7]) if r[7] is not None else None,
                regime_duration_days=int(r[8])
            )
            for r in rows
        ]
        return RegimeResponse(count=len(data), data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/market-structure/regimes/stats", response_model=RegimeSummaryResponse)
def get_regime_stats():
    """Returns summary duration and return statistics per regime type."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        SELECT 
            REGIME_NAME,
            COUNT(*) AS TOTAL_DAYS,
            ROUND(AVG(AVG_MARKET_RETURN_PCT), 4) AS AVG_DAILY_RETURN_PCT,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM STAGING.MARKET_REGIMES), 2) AS PCT_OF_TIME
        FROM STAGING.MARKET_REGIMES
        GROUP BY REGIME_NAME
        ORDER BY TOTAL_DAYS DESC
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        regimes = [
            RegimeSummaryItem(
                regime_name=r[0],
                total_days=int(r[1]),
                avg_daily_return_pct=float(r[2]) if r[2] is not None else None,
                pct_of_time=float(r[3]) if r[3] is not None else None
            )
            for r in rows
        ]
        return RegimeSummaryResponse(count=len(regimes), regimes=regimes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/market-structure/themes", response_model=ThemeListResponse)
def get_themes():
    """Returns list of custom stock baskets / themes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "SELECT THEME_CODE, THEME_NAME, DESCRIPTION, STOCK_COUNT FROM STAGING.THEME_MASTER ORDER BY THEME_CODE ASC"
        cursor.execute(sql)
        rows = cursor.fetchall()
        themes = [
            ThemeItem(theme_code=r[0], theme_name=r[1], description=r[2], stock_count=int(r[3]))
            for r in rows
        ]
        return ThemeListResponse(count=len(themes), themes=themes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/market-structure/themes/rotation", response_model=ThemeRotationResponse)
def get_theme_rotation(
    target_date: Optional[str] = Query(None, description="YYYY-MM-DD (defaults to latest trading date)"),
    status: Optional[str] = Query(None, description="Filter by status: LEADING, EMERGING, WEAKENING, LAGGING")
):
    """Returns custom theme rotation leaderboard."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if not target_date:
            cursor.execute("SELECT TO_CHAR(MAX(DATETIME), 'YYYY-MM-DD') FROM STAGING.THEME_ROTATION")
            target_date = cursor.fetchone()[0]

        sql = """
        SELECT 
            THEME_CODE, TO_CHAR(DATETIME, 'YYYY-MM-DD'),
            RETURN_1M, RETURN_3M, RETURN_6M, RETURN_12M,
            RELATIVE_STRENGTH_1M, RELATIVE_STRENGTH_3M, RELATIVE_STRENGTH_6M, RELATIVE_STRENGTH_12M,
            THEME_RANK_3M, RANK_DELTA_3M, ROTATION_STATUS
        FROM STAGING.THEME_ROTATION
        WHERE DATETIME = TO_DATE(:1, 'YYYY-MM-DD')
        """
        params = [target_date]
        if status:
            sql += " AND UPPER(ROTATION_STATUS) = :2"
            params.append(status.upper().strip())

        sql += " ORDER BY THEME_RANK_3M ASC NULLS LAST"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        data = [
            ThemeRotationRecord(
                theme_code=r[0], datetime=r[1],
                return_1m=float(r[2]) if r[2] is not None else None,
                return_3m=float(r[3]) if r[3] is not None else None,
                return_6m=float(r[4]) if r[4] is not None else None,
                return_12m=float(r[5]) if r[5] is not None else None,
                relative_strength_1m=float(r[6]) if r[6] is not None else None,
                relative_strength_3m=float(r[7]) if r[7] is not None else None,
                relative_strength_6m=float(r[8]) if r[8] is not None else None,
                relative_strength_12m=float(r[9]) if r[9] is not None else None,
                theme_rank_3m=int(r[10]) if r[10] is not None else None,
                rank_delta_3m=int(r[11]) if r[11] is not None else None,
                rotation_status=r[12]
            )
            for r in rows
        ]
        return ThemeRotationResponse(count=len(data), data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/market-structure/themes/daily/{theme_code}", response_model=DailyAggregationResponse)
def get_theme_daily(
    theme_code: str,
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD")
):
    """Returns precomputed daily aggregated metrics & breadth for a custom theme."""
    code_upper = theme_code.upper().strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        SELECT 
            THEME_CODE, TO_CHAR(DATETIME, 'YYYY-MM-DD'), AVG_CHANGE_PCT, MEDIAN_CHANGE_PCT, TOTAL_VOLUME, AVG_RSI_14, ACTIVE_STOCKS,
            ADVANCING_STOCKS, DECLINING_STOCKS, UNCHANGED_STOCKS, BREADTH_RATIO, NET_ADVANCES,
            PCT_ABOVE_EMA20, PCT_ABOVE_EMA50, PCT_ABOVE_EMA200
        FROM STAGING.THEME_DAILY
        WHERE THEME_CODE = :1
        """
        params = [code_upper]
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
            raise HTTPException(status_code=404, detail=f"No daily data found for theme '{code_upper}'.")

        data = [
            DailyAggregationRecord(
                code=r[0],
                datetime=r[1],
                avg_change_pct=float(r[2]) if r[2] is not None else None,
                median_change_pct=float(r[3]) if r[3] is not None else None,
                total_volume=int(r[4]) if r[4] is not None else None,
                avg_rsi_14=float(r[5]) if r[5] is not None else None,
                active_stocks=int(r[6]) if r[6] is not None else None,
                advancing_stocks=int(r[7]) if r[7] is not None else None,
                declining_stocks=int(r[8]) if r[8] is not None else None,
                unchanged_stocks=int(r[9]) if r[9] is not None else None,
                breadth_ratio=float(r[10]) if r[10] is not None else None,
                net_advances=int(r[11]) if r[11] is not None else None,
                pct_above_ema20=float(r[12]) if r[12] is not None else None,
                pct_above_ema50=float(r[13]) if r[13] is not None else None,
                pct_above_ema200=float(r[14]) if r[14] is not None else None
            )
            for r in rows
        ]
        return DailyAggregationResponse(code=code_upper, count=len(data), data=data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/market-structure/rotation/sectors", response_model=RotationResponse)
def get_sector_rotation(
    target_date: Optional[str] = Query(None, description="YYYY-MM-DD (defaults to latest trading date)"),
    status: Optional[str] = Query(None, description="Filter by status: LEADING, EMERGING, WEAKENING, LAGGING")
):
    """Returns sector rotation leaderboard and leadership statuses."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if not target_date:
            cursor.execute("SELECT TO_CHAR(MAX(DATETIME), 'YYYY-MM-DD') FROM STAGING.SECTOR_ROTATION")
            target_date = cursor.fetchone()[0]

        sql = """
        SELECT 
            SECTOR_CODE, TO_CHAR(DATETIME, 'YYYY-MM-DD'),
            RETURN_1M, RETURN_3M, RETURN_6M, RETURN_12M,
            RELATIVE_STRENGTH_1M, RELATIVE_STRENGTH_3M, RELATIVE_STRENGTH_6M, RELATIVE_STRENGTH_12M,
            SECTOR_RANK_1M, SECTOR_RANK_3M, SECTOR_RANK_12M, RANK_DELTA_3M, ROTATION_STATUS
        FROM STAGING.SECTOR_ROTATION
        WHERE DATETIME = TO_DATE(:1, 'YYYY-MM-DD')
        """
        params = [target_date]
        if status:
            sql += " AND UPPER(ROTATION_STATUS) = :2"
            params.append(status.upper().strip())

        sql += " ORDER BY SECTOR_RANK_3M ASC NULLS LAST"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        data = [
            RotationRecord(
                code=r[0], datetime=r[1],
                return_1m=float(r[2]) if r[2] is not None else None,
                return_3m=float(r[3]) if r[3] is not None else None,
                return_6m=float(r[4]) if r[4] is not None else None,
                return_12m=float(r[5]) if r[5] is not None else None,
                relative_strength_1m=float(r[6]) if r[6] is not None else None,
                relative_strength_3m=float(r[7]) if r[7] is not None else None,
                relative_strength_6m=float(r[8]) if r[8] is not None else None,
                relative_strength_12m=float(r[9]) if r[9] is not None else None,
                rank_1m=int(r[10]) if r[10] is not None else None,
                rank_3m=int(r[11]) if r[11] is not None else None,
                rank_12m=int(r[12]) if r[12] is not None else None,
                rank_delta_3m=int(r[13]) if r[13] is not None else None,
                rotation_status=r[14]
            )
            for r in rows
        ]
        return RotationResponse(count=len(data), data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/market-structure/rotation/timeline/{sector_code}", response_model=RotationResponse)
def get_sector_rotation_timeline(
    sector_code: str,
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD")
):
    """Returns historical rotation rank timeline for a sector."""
    code_upper = sector_code.upper().strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        SELECT 
            SECTOR_CODE, TO_CHAR(DATETIME, 'YYYY-MM-DD'),
            RETURN_1M, RETURN_3M, RETURN_6M, RETURN_12M,
            RELATIVE_STRENGTH_1M, RELATIVE_STRENGTH_3M, RELATIVE_STRENGTH_6M, RELATIVE_STRENGTH_12M,
            SECTOR_RANK_1M, SECTOR_RANK_3M, SECTOR_RANK_12M, RANK_DELTA_3M, ROTATION_STATUS
        FROM STAGING.SECTOR_ROTATION
        WHERE SECTOR_CODE = :1
        """
        params = [code_upper]
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
        data = [
            RotationRecord(
                code=r[0], datetime=r[1],
                return_1m=float(r[2]) if r[2] is not None else None,
                return_3m=float(r[3]) if r[3] is not None else None,
                return_6m=float(r[4]) if r[4] is not None else None,
                return_12m=float(r[5]) if r[5] is not None else None,
                relative_strength_1m=float(r[6]) if r[6] is not None else None,
                relative_strength_3m=float(r[7]) if r[7] is not None else None,
                relative_strength_6m=float(r[8]) if r[8] is not None else None,
                relative_strength_12m=float(r[9]) if r[9] is not None else None,
                rank_1m=int(r[10]) if r[10] is not None else None,
                rank_3m=int(r[11]) if r[11] is not None else None,
                rank_12m=int(r[12]) if r[12] is not None else None,
                rank_delta_3m=int(r[13]) if r[13] is not None else None,
                rotation_status=r[14]
            )
            for r in rows
        ]
        return RotationResponse(count=len(data), data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/market-structure/rankings/stocks", response_model=StockRankingResponse)
def get_stock_rankings(
    target_date: Optional[str] = Query(None, description="YYYY-MM-DD (defaults to latest trading date)"),
    sector_code: Optional[str] = Query(None, description="Filter by sector code"),
    industry_code: Optional[str] = Query(None, description="Filter by industry code"),
    limit: int = Query(50, ge=1, le=500, description="Max rows to return")
):
    """Returns top ranked stocks by industry, sector, or market for a target date."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if not target_date:
            cursor.execute("SELECT TO_CHAR(MAX(DATETIME), 'YYYY-MM-DD') FROM STAGING.STOCK_RANKINGS")
            target_date = cursor.fetchone()[0]

        sql = """
        SELECT 
            SYMBOL, TO_CHAR(DATETIME, 'YYYY-MM-DD'), SECTOR_CODE, INDUSTRY_CODE, RETURN_3M,
            SECTOR_RANK, INDUSTRY_RANK, MARKET_RANK,
            SECTOR_PERCENTILE, INDUSTRY_PERCENTILE, MARKET_PERCENTILE, RSI_RANK_INDUSTRY
        FROM STAGING.STOCK_RANKINGS
        WHERE DATETIME = TO_DATE(:1, 'YYYY-MM-DD')
        """
        params = [target_date]
        if sector_code:
            param_idx = len(params) + 1
            sql += f" AND UPPER(SECTOR_CODE) = :{param_idx}"
            params.append(sector_code.upper().strip())
        if industry_code:
            param_idx = len(params) + 1
            sql += f" AND UPPER(INDUSTRY_CODE) = :{param_idx}"
            params.append(industry_code.upper().strip())

        if industry_code:
            sql += " ORDER BY INDUSTRY_RANK ASC NULLS LAST"
        elif sector_code:
            sql += " ORDER BY SECTOR_RANK ASC NULLS LAST"
        else:
            sql += " ORDER BY MARKET_RANK ASC NULLS LAST"

        param_idx = len(params) + 1
        sql += f" FETCH FIRST :{param_idx} ROWS ONLY"
        params.append(limit)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        data = [
            StockRankingRecord(
                symbol=r[0], datetime=r[1], sector_code=r[2], industry_code=r[3],
                return_3m=float(r[4]) if r[4] is not None else None,
                sector_rank=int(r[5]) if r[5] is not None else None,
                industry_rank=int(r[6]) if r[6] is not None else None,
                market_rank=int(r[7]) if r[7] is not None else None,
                sector_percentile=float(r[8]) if r[8] is not None else None,
                industry_percentile=float(r[9]) if r[9] is not None else None,
                market_percentile=float(r[10]) if r[10] is not None else None,
                rsi_rank_industry=int(r[11]) if r[11] is not None else None
            )
            for r in rows
        ]
        return StockRankingResponse(count=len(data), data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/market-structure/rankings/stocks/{symbol}", response_model=StockRankingResponse)
def get_stock_ranking_history(
    symbol: str,
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD")
):
    """Returns historical ranking and percentile timeline for a specific stock."""
    sym_upper = symbol.upper().strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        SELECT 
            SYMBOL, TO_CHAR(DATETIME, 'YYYY-MM-DD'), SECTOR_CODE, INDUSTRY_CODE, RETURN_3M,
            SECTOR_RANK, INDUSTRY_RANK, MARKET_RANK,
            SECTOR_PERCENTILE, INDUSTRY_PERCENTILE, MARKET_PERCENTILE, RSI_RANK_INDUSTRY
        FROM STAGING.STOCK_RANKINGS
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
        data = [
            StockRankingRecord(
                symbol=r[0], datetime=r[1], sector_code=r[2], industry_code=r[3],
                return_3m=float(r[4]) if r[4] is not None else None,
                sector_rank=int(r[5]) if r[5] is not None else None,
                industry_rank=int(r[6]) if r[6] is not None else None,
                market_rank=int(r[7]) if r[7] is not None else None,
                sector_percentile=float(r[8]) if r[8] is not None else None,
                industry_percentile=float(r[9]) if r[9] is not None else None,
                market_percentile=float(r[10]) if r[10] is not None else None,
                rsi_rank_industry=int(r[11]) if r[11] is not None else None
            )
            for r in rows
        ]
        return StockRankingResponse(count=len(data), data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/market-structure/sector-daily/{sector_code}", response_model=DailyAggregationResponse)
def get_sector_daily(
    sector_code: str,
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD")
):
    """Returns precomputed daily aggregated metrics & breadth for a sector."""
    code_upper = sector_code.upper().strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        SELECT 
            SECTOR_CODE, TO_CHAR(DATETIME, 'YYYY-MM-DD'), AVG_CHANGE_PCT, MEDIAN_CHANGE_PCT, TOTAL_VOLUME, AVG_RSI_14, ACTIVE_STOCKS,
            ADVANCING_STOCKS, DECLINING_STOCKS, UNCHANGED_STOCKS, BREADTH_RATIO, NET_ADVANCES,
            PCT_ABOVE_EMA20, PCT_ABOVE_EMA50, PCT_ABOVE_EMA200
        FROM STAGING.SECTOR_DAILY
        WHERE SECTOR_CODE = :1
        """
        params = [code_upper]
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
            raise HTTPException(status_code=404, detail=f"No daily aggregated data found for sector '{code_upper}'.")

        data = [
            DailyAggregationRecord(
                code=r[0],
                datetime=r[1],
                avg_change_pct=float(r[2]) if r[2] is not None else None,
                median_change_pct=float(r[3]) if r[3] is not None else None,
                total_volume=int(r[4]) if r[4] is not None else None,
                avg_rsi_14=float(r[5]) if r[5] is not None else None,
                active_stocks=int(r[6]) if r[6] is not None else None,
                advancing_stocks=int(r[7]) if r[7] is not None else None,
                declining_stocks=int(r[8]) if r[8] is not None else None,
                unchanged_stocks=int(r[9]) if r[9] is not None else None,
                breadth_ratio=float(r[10]) if r[10] is not None else None,
                net_advances=int(r[11]) if r[11] is not None else None,
                pct_above_ema20=float(r[12]) if r[12] is not None else None,
                pct_above_ema50=float(r[13]) if r[13] is not None else None,
                pct_above_ema200=float(r[14]) if r[14] is not None else None
            )
            for r in rows
        ]
        return DailyAggregationResponse(code=code_upper, count=len(data), data=data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/market-structure/industry-daily/{industry_code}", response_model=DailyAggregationResponse)
def get_industry_daily(
    industry_code: str,
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD")
):
    """Returns precomputed daily aggregated metrics & breadth for an industry."""
    code_upper = industry_code.upper().strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        SELECT 
            INDUSTRY_CODE, TO_CHAR(DATETIME, 'YYYY-MM-DD'), AVG_CHANGE_PCT, MEDIAN_CHANGE_PCT, TOTAL_VOLUME, AVG_RSI_14, ACTIVE_STOCKS,
            ADVANCING_STOCKS, DECLINING_STOCKS, UNCHANGED_STOCKS, BREADTH_RATIO, NET_ADVANCES,
            PCT_ABOVE_EMA20, PCT_ABOVE_EMA50, PCT_ABOVE_EMA200
        FROM STAGING.INDUSTRY_DAILY
        WHERE INDUSTRY_CODE = :1
        """
        params = [code_upper]
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
            raise HTTPException(status_code=404, detail=f"No daily aggregated data found for industry '{code_upper}'.")

        data = [
            DailyAggregationRecord(
                code=r[0],
                datetime=r[1],
                avg_change_pct=float(r[2]) if r[2] is not None else None,
                median_change_pct=float(r[3]) if r[3] is not None else None,
                total_volume=int(r[4]) if r[4] is not None else None,
                avg_rsi_14=float(r[5]) if r[5] is not None else None,
                active_stocks=int(r[6]) if r[6] is not None else None,
                advancing_stocks=int(r[7]) if r[7] is not None else None,
                declining_stocks=int(r[8]) if r[8] is not None else None,
                unchanged_stocks=int(r[9]) if r[9] is not None else None,
                breadth_ratio=float(r[10]) if r[10] is not None else None,
                net_advances=int(r[11]) if r[11] is not None else None,
                pct_above_ema20=float(r[12]) if r[12] is not None else None,
                pct_above_ema50=float(r[13]) if r[13] is not None else None,
                pct_above_ema200=float(r[14]) if r[14] is not None else None
            )
            for r in rows
        ]
        return DailyAggregationResponse(code=code_upper, count=len(data), data=data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/market-structure/sector-performance", response_model=PerformanceResponse)
def get_sector_performance(period_type: str = Query("MONTHLY", description="MONTHLY, QUARTERLY, ANNUAL")):
    """Returns precomputed sector performance leaderboard."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        SELECT SECTOR_CODE, PERIOD_TYPE, PERIOD_LABEL, AVG_RETURN_PCT, WIN_RATE_PCT, VOLATILITY_PCT, SAMPLE_COUNT
        FROM STAGING.SECTOR_PERFORMANCE
        WHERE UPPER(PERIOD_TYPE) = :1
        ORDER BY AVG_RETURN_PCT DESC NULLS LAST
        """
        cursor.execute(sql, [period_type.upper().strip()])
        rows = cursor.fetchall()
        data = [
            PerformanceRecord(
                code=r[0],
                period_type=r[1],
                period_label=r[2],
                avg_return_pct=float(r[3]) if r[3] is not None else None,
                win_rate_pct=float(r[4]) if r[4] is not None else None,
                volatility_pct=float(r[5]) if r[5] is not None else None,
                sample_count=int(r[6]) if r[6] is not None else 0
            )
            for r in rows
        ]
        return PerformanceResponse(count=len(data), data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/market-structure/industry-performance", response_model=PerformanceResponse)
def get_industry_performance(
    sector_code: Optional[str] = Query(None, description="Optional sector code filter"),
    period_type: str = Query("MONTHLY", description="MONTHLY, QUARTERLY, ANNUAL")
):
    """Returns precomputed industry performance leaderboard."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        SELECT ip.INDUSTRY_CODE, ip.PERIOD_TYPE, ip.PERIOD_LABEL, ip.AVG_RETURN_PCT, ip.WIN_RATE_PCT, ip.VOLATILITY_PCT, ip.SAMPLE_COUNT
        FROM STAGING.INDUSTRY_PERFORMANCE ip
        """
        params = [period_type.upper().strip()]
        if sector_code:
            sql += " JOIN STAGING.INDUSTRY_MASTER im ON ip.INDUSTRY_CODE = im.INDUSTRY_CODE WHERE UPPER(im.SECTOR_CODE) = :2 AND UPPER(ip.PERIOD_TYPE) = :1"
            params.insert(0, sector_code.upper().strip())
        else:
            sql += " WHERE UPPER(ip.PERIOD_TYPE) = :1"

        sql += " ORDER BY ip.AVG_RETURN_PCT DESC NULLS LAST"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        data = [
            PerformanceRecord(
                code=r[0],
                period_type=r[1],
                period_label=r[2],
                avg_return_pct=float(r[3]) if r[3] is not None else None,
                win_rate_pct=float(r[4]) if r[4] is not None else None,
                volatility_pct=float(r[5]) if r[5] is not None else None,
                sample_count=int(r[6]) if r[6] is not None else 0
            )
            for r in rows
        ]
        return PerformanceResponse(count=len(data), data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()
