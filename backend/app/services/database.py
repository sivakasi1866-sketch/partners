import json
import os

DATA_DIR = os.path.join(os.getcwd(), 'server', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

class MockDatabase:
    def __init__(self):
        self.telemetry = []
        self.stop_events = []
        self.trips = []
        self.users = []
        self.buses = []
        self.routes = []
        self.drivers = []
        self.system_logs = []
        self.notifications = []
        
        # Load mock data if it exists
        mock_db_path = os.path.join(DATA_DIR, 'mock_db.json')
        if os.path.exists(mock_db_path):
            try:
                with open(mock_db_path, 'r') as f:
                    data = json.load(f)
                    self.users = data.get('users', [])
                    self.buses = data.get('buses', [])
                    self.routes = data.get('routes', [])
                    self.drivers = data.get('drivers', [])
                    self.system_logs = data.get('systemLogs', [])
                    self.notifications = data.get('notifications', [])
            except Exception as e:
                print(f"Error loading mock db: {e}")

        # Load persisted data
        self.load_telemetry()
        self.load_stop_events()
        self.load_trips()

    def load_telemetry(self):
        p = os.path.join(DATA_DIR, 'telemetry.json')
        if os.path.exists(p):
            with open(p, 'r') as f:
                self.telemetry = json.load(f)

    def save_telemetry(self):
        p = os.path.join(DATA_DIR, 'telemetry.json')
        with open(p, 'w') as f:
            json.dump(self.telemetry, f, indent=2)
            
    def load_stop_events(self):
        p = os.path.join(DATA_DIR, 'stop_events.json')
        if os.path.exists(p):
            with open(p, 'r') as f:
                self.stop_events = json.load(f)

    def save_stop_events(self):
        p = os.path.join(DATA_DIR, 'stop_events.json')
        with open(p, 'w') as f:
            json.dump(self.stop_events, f, indent=2)

    def load_trips(self):
        p = os.path.join(DATA_DIR, 'trips.json')
        if os.path.exists(p):
            with open(p, 'r') as f:
                self.trips = json.load(f)

    def save_trips(self):
        p = os.path.join(DATA_DIR, 'trips.json')
        with open(p, 'w') as f:
            json.dump(self.trips, f, indent=2)

db_instance = MockDatabase()

def get_db():
    return db_instance
def save_mock_db(db):
    import json
    p = os.path.join(DATA_DIR, 'mock_db.json')
    with open(p, 'w') as f:
        json.dump({
            "users": db.users,
            "drivers": db.drivers,
            "buses": db.buses,
            "routes": db.routes,
            "systemLogs": db.system_logs,
            "notifications": getattr(db, 'notifications', [])
        }, f, indent=2)
