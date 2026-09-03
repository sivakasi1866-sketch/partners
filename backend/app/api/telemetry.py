from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict
from backend.app.services.database import get_db
from backend.app.api.deps import require_role

router = APIRouter()

@router.get("/telemetry/export")
def export_telemetry(current_user: Dict = Depends(require_role(["admin"]))):
    db = get_db()
    
    return {
        "status": "success",
        "count": len(db.telemetry),
        "datasetType": "REAL_RPSIT_BUS_TELEMETRY",
        "records": db.telemetry,
        "stopEvents": db.stop_events
    }