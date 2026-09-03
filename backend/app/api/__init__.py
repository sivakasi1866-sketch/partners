from fastapi import APIRouter
from backend.app.api import auth, buses, routes, trips, telemetry, users, logs, ml, import_data, assignments, ai

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(buses.router, prefix="/buses", tags=["buses"])
router.include_router(routes.router, prefix="/routes", tags=["routes"])
router.include_router(trips.router, prefix="/trips", tags=["trips"])
router.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
router.include_router(telemetry.router, tags=["telemetry"])
router.include_router(users.router, tags=["users"])
router.include_router(logs.router, tags=["logs"])
router.include_router(ml.router, prefix="/ml", tags=["ml"])
router.include_router(import_data.router, prefix="/import", tags=["import"])
router.include_router(ai.router, prefix="/ai", tags=["ai"])

@router.get("/health")
def health_check():
    from backend.app.services.database import get_db
    db = get_db()
    active_trips_count = len([t for t in db.trips if t.get("status") == "in_progress"])
    return {
        "status": "healthy",
        "systemName": "Elite Bus Prediction Core",
        "privacyStatus": {
            "studentGpsTracking": "DISABLED_PERMANENTLY",
            "staffGpsTracking": "DISABLED_PERMANENTLY",
            "driverGpsTracking": "ACTIVE_ONLY_DURING_TRIPS"
        },
        "activeTrips": active_trips_count
    }