import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core import config
from core.database import init_db_pool, close_db_pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db_pool()
    yield
    close_db_pool()

app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description="Historical Market Intelligence Engine (HMIE) REST API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import (
    metadata_router,
    historical_data_router,
    technical_analysis_router,
    market_structure_router,
    evidence_router,
    strategy_router,
    system_router,
    compare_router,
    rbi_router
)

app.include_router(metadata_router.router, prefix="/api/v1", tags=["Metadata"])
app.include_router(historical_data_router.router, prefix="/api/v1", tags=["Raw History"])
app.include_router(technical_analysis_router.router, prefix="/api/v1", tags=["Technical & Dashboard"])
app.include_router(market_structure_router.router, prefix="/api/v1", tags=["Market Structure"])
app.include_router(evidence_router.router, prefix="/api/v1", tags=["Evidence Engine"])
app.include_router(strategy_router.router, prefix="/api/v1", tags=["Strategy & Research"])
app.include_router(system_router.router)
app.include_router(compare_router.router)
app.include_router(rbi_router.router)

from fastapi.responses import FileResponse

DASHBOARDS_DIR = BASE_DIR / "dashboards"

def _get_dashboard(filename: str):
    f = DASHBOARDS_DIR / filename
    if f.exists():
        return FileResponse(str(f))
    return FileResponse(str(DASHBOARDS_DIR / "home.html"))

@app.get("/", tags=["Dashboard"])
@app.get("/home.html", tags=["Dashboard"])
def serve_home_page():
    return _get_dashboard("home.html")

@app.get("/library.html", tags=["Dashboard"])
@app.get("/library", tags=["Dashboard"])
def serve_library_page():
    return _get_dashboard("library.html")

@app.get("/rbi.html", tags=["Dashboard"])
def serve_rbi_page():
    return _get_dashboard("rbi.html")

@app.get("/festivals.html", tags=["Dashboard"])
@app.get("/festival_research.html", tags=["Dashboard"])
def serve_festivals_page():
    return _get_dashboard("festival_research.html")

@app.get("/compare.html", tags=["Dashboard"])
@app.get("/benchmark_comparison.html", tags=["Dashboard"])
def serve_compare_page():
    return _get_dashboard("benchmark_comparison.html")

@app.get("/festive_stocks.html", tags=["Dashboard"])
@app.get("/seasonal_stock_leaders.html", tags=["Dashboard"])
def serve_festive_stocks_page():
    return _get_dashboard("seasonal_stock_leaders.html")

@app.get("/event.html", tags=["Dashboard"])
@app.get("/event_details.html", tags=["Dashboard"])
def serve_event_page():
    return _get_dashboard("event_details.html")

@app.get("/health.html", tags=["Dashboard"])
@app.get("/system_health.html", tags=["Dashboard"])
def serve_health_page():
    return _get_dashboard("system_health.html")

RESEARCH_DIR = BASE_DIR / "research"

@app.get("/research/{filename}", tags=["Research Notes"])
def serve_research_note(filename: str):
    f = RESEARCH_DIR / filename
    if f.exists():
        return FileResponse(str(f), media_type="text/markdown")
    return {"error": f"Research note '{filename}' not found."}

@app.get("/api/v1/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": config.API_TITLE,
        "version": config.API_VERSION,
        "oracle_db": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host=config.API_HOST, port=config.API_PORT, reload=True)
