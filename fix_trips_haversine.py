import re
with open('backend/app/api/trips.py', 'r') as f:
    code = f.read()

stop_detection = """
    # Haversine stop detection
    route = next((r for r in db.routes if r.get("id") == trip.get("routeId")), None)
    if route:
        stops = route.get("stops", [])
        next_index = trip.get("nextStopIndex", 0)
        if next_index < len(stops):
            next_stop = stops[next_index]
            try:
                slat = float(next_stop.get("latitude"))
                slon = float(next_stop.get("longitude"))
                dist = haversine(req.latitude, req.longitude, slat, slon)
                if dist < 50:  # 50 meters threshold
                    trip["currentStopIndex"] = next_index
                    trip["nextStopIndex"] = next_index + 1
                    
                    if not hasattr(db, "system_logs"):
                        db.system_logs = []
                    
                    existing_event = next((e for e in db.system_logs if e.get("type") == "stop_arrival" and e.get("tripId") == trip["id"] and e.get("stopId") == next_stop.get("id")), None)
                    if not existing_event:
                        import time
                        db.system_logs.append({
                            "id": f"evt-{int(time.time()*1000)}",
                            "type": "stop_arrival",
                            "tripId": trip["id"],
                            "routeId": route["id"],
                            "stopId": next_stop.get("id"),
                            "timestamp": incoming_timestamp,
                            "message": f"Arrived at stop {next_stop.get('name') or next_stop.get('stopName') or 'Unknown'}"
                        })
            except Exception as e:
                print("Error calculating haversine:", e)
"""

code = re.sub(
    r'trip\["lastLocationUpdateTime"\] = incoming_timestamp\s*# Distance approximation placeholder, skipping actual haversine in basic mock',
    'trip["lastLocationUpdateTime"] = incoming_timestamp\n' + stop_detection + '\n        # Distance approximation placeholder, skipping actual haversine in basic mock',
    code
)

with open('backend/app/api/trips.py', 'w') as f:
    f.write(code)
