with open("backend/app/api/__init__.py", "r") as f:
    content = f.read()

content = content.replace("from app.api import auth, buses, routes, trips, telemetry, users, logs", "from app.api import auth, buses, routes, trips, telemetry, users, logs, ml")
content = content.replace("router.include_router(logs.router, tags=[\"logs\"])", "router.include_router(logs.router, tags=[\"logs\"])\nrouter.include_router(ml.router, prefix=\"/ml\", tags=[\"ml\"])")

with open("backend/app/api/__init__.py", "w") as f:
    f.write(content)
