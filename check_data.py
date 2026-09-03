import json
with open('server/data/mock_db.json') as f:
    db = json.load(f)

trips = db.get("trips", [])
buses = {b["id"] for b in db.get("buses", [])}
routes = {r["id"] for r in db.get("routes", [])}
drivers = {d["id"] for d in db.get("drivers", [])}
users = {u["id"] for u in db.get("users", [])}

for t in trips:
    if t.get("busId") not in buses:
        print(f"Trip {t['id']} has invalid busId {t.get('busId')}")
    if t.get("routeId") not in routes:
        print(f"Trip {t['id']} has invalid routeId {t.get('routeId')}")
    if t.get("driverId") not in drivers and t.get("driverId") not in users:
        print(f"Trip {t['id']} has invalid driverId {t.get('driverId')}")
print("Check done")
