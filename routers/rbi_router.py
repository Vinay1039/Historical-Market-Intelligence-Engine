from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from pydantic import BaseModel
from services.rbi_service import RBIMonetaryService
from services.analog_service import AnalogService

router = APIRouter(prefix="/api/v1/rbi", tags=["RBI Monetary Policy Intelligence"])
rbi_service = RBIMonetaryService()
analog_service = AnalogService()

class AnalogQueryRequest(BaseModel):
    event_type: str = "RBI"
    features: Dict[str, Any]
    top_n: Optional[int] = 5

@router.get("/metrics")
def get_rbi_metrics(stance: str = Query("ALL", description="Stance filter: ALL, CUT, HIKE, PAUSE")):
    stance = stance.upper()
    if stance not in ["ALL", "CUT", "HIKE", "PAUSE"]:
        raise HTTPException(status_code=400, detail="Invalid stance parameter.")
    return rbi_service.calculate_rbi_metrics(stance)

@router.get("/comparison")
def get_rbi_cross_stance_comparison():
    return rbi_service.get_cross_stance_comparison()

@router.post("/analogs")
def find_similar_cases(req: AnalogQueryRequest):
    return analog_service.find_analogs(event_type=req.event_type, current_features=req.features, top_n=req.top_n)
