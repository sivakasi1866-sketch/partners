with open("backend/app/api/__init__.py", "r") as f:
    code = f.read()

code = code.replace(
    "from backend.app.api import auth, buses, routes, trips, telemetry, users, logs, ml, import_data",
    "from backend.app.api import auth, buses, routes, trips, telemetry, users, logs, ml, import_data, assignments"
)

code = code.replace(
    'router.include_router(trips.router, prefix="/trips", tags=["trips"])',
    'router.include_router(trips.router, prefix="/trips", tags=["trips"])\nrouter.include_router(assignments.router, prefix="/assignments", tags=["assignments"])'
)

with open("backend/app/api/__init__.py", "w") as f:
    f.write(code)
