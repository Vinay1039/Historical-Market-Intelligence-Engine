import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core import config
from core.database import init_db_pool, close_db_pool
from routers import metadata_router, history_router, technical_router, market_structure_router, evidence_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Oracle DB Connection Pool on startup
    init_db_pool()
    yield
    # Close Oracle DB Connection Pool on shutdown
    close_db_pool()

app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description="""
    ## Historical Market Intelligence Engine (HMIE) REST API
    
    Thin, high-performance, read-only data service backed by Oracle 23c XE.
    
    ### Authoritative Price Data Policy (ADR-001):
    - **/api/v1/history/{symbol}**: Queries `STAGING.RAW_STOCK_HISTORY` (Original Unadjusted Raw OHLCV).
    - **/api/v1/technical/{symbol}**: Queries `STAGING.STOCK_HIST_DATA` (Authoritative Analytical Adjusted Series with 40+ pre-calculated indicators).
    - **/api/v1/dashboard/{symbol}**: Queries `STAGING.STOCK_HIST_DATA` for MIT UI Dashboard presentation.
    - **/api/v1/market-structure/**: Market Structure Foundation (Sectors, Industries, Daily Aggregations, Performance, Rotation, Rankings, Themes, Regimes).
    - **/api/v1/evidence/**: Stage 4 Historical Evidence Engine (Corrections, Recoveries, Macro Events, Union Budgets, Elections).
    """,
    lifespan=lifespan
)

# Enable CORS for local SPA clients and agents
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import metadata_router, history_router, technical_router, market_structure_router, evidence_router, strategy_router

from fastapi.staticfiles import StaticFiles
import os

# Register routers with /api/v1 prefix
app.include_router(metadata_router.router, prefix="/api/v1", tags=["Metadata"])
app.include_router(history_router.router, prefix="/api/v1", tags=["Raw History (ADR-001 Rule 1)"])
app.include_router(technical_router.router, prefix="/api/v1", tags=["Technical & Dashboard (ADR-001 Rule 2 & 3)"])
app.include_router(market_structure_router.router, prefix="/api/v1", tags=["Stage 3 Market Structure"])
app.include_router(evidence_router.router, prefix="/api/v1", tags=["Stage 4 Historical Evidence Engine"])
app.include_router(strategy_router.router, prefix="/api/v1", tags=["Stage 6 Quantitative Strategy Lab"])

# Mount Stage 5 Research Explorer UI
# Mount HMIE 2.3 Dashboard UI
STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.exists():
    app.mount("/dashboard", StaticFiles(directory=str(STATIC_DIR), html=True), name="dashboard")

from fastapi.responses import FileResponse
@app.get("/", tags=["Dashboard"])
def serve_dashboard():
    """Serves HMIE 2.3 Single-Page Governed Evidence Dashboard UI."""
    return FileResponse(str(STATIC_DIR / "index.html"))

@app.get("/api/v1/health", tags=["Health"])
def health_check():
    """Health check endpoint returning API status and version."""
    return {
        "status": "healthy",
        "service": config.API_TITLE,
        "version": config.API_VERSION,
        "oracle_db": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host=config.API_HOST, port=config.API_PORT, reload=True)

