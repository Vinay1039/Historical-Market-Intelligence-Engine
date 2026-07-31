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

from routers import metadata_router, history_router, technical_router, market_structure_router, evidence_router, strategy_router, system_router

app.include_router(metadata_router.router, prefix="/api/v1", tags=["Metadata"])
app.include_router(history_router.router, prefix="/api/v1", tags=["Raw History"])
app.include_router(technical_router.router, prefix="/api/v1", tags=["Technical & Dashboard"])
app.include_router(market_structure_router.router, prefix="/api/v1", tags=["Market Structure"])
app.include_router(evidence_router.router, prefix="/api/v1", tags=["Evidence Engine"])
app.include_router(strategy_router.router, prefix="/api/v1", tags=["Strategy & Research"])
app.include_router(system_router.router)

from fastapi.staticfiles import StaticFiles
STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.exists():
    app.mount("/dashboard", StaticFiles(directory=str(STATIC_DIR), html=True), name="dashboard")

from fastapi.responses import FileResponse
@app.get("/", tags=["Dashboard"])
def serve_dashboard():
    return FileResponse(str(STATIC_DIR / "index.html"))

@app.get("/event.html", tags=["Dashboard"])
def serve_event_page():
    return FileResponse(str(STATIC_DIR / "event.html"))

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
