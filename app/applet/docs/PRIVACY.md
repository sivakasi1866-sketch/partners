# Privacy Policy & Architecture

## GPS Data Collection Lifecycle
This application enforces a strict, non-negotiable policy regarding user location data to ensure maximum privacy compliance.

### The Rules
1. **Student Location**: NEVER collected.
2. **Staff Location**: NEVER collected.
3. **Driver Location**: ONLY collected during an active trip.

### Technical Enforcement
* **Before Trip**: Client-side `watchPosition` is dormant. API rejects telemetry.
* **Trip Start**: Location tracking initiates.
* **Active Trip**: Telemetry flows securely to the FastAPI backend.
* **Trip Stop**: Backend closes the trip state. Frontend invokes `navigator.geolocation.clearWatch()`. API outright rejects any lingering incoming telemetry as `PRIVACY_POLICY_VIOLATION`.
* **Logout / Role Change**: Frontend immediately purges memory state and invokes `clearWatch()`.

## Real vs. Synthetic Telemetry
To maintain clear data provenance for Machine Learning compliance, all telemetry persists with explicit context markers:
* `SYNTHETIC_DEVELOPMENT_TELEMETRY` is applied to mock data generated for testing.
* `REAL_RPSIT_BUS_TELEMETRY` is assigned exclusively to real driver-emitted device telemetry. 

*No student or staff metadata is attached to any telemetry record under any circumstance.*

## Export Limitations
Only authenticated users possessing the `admin` role can access the `/api/telemetry/export` endpoint. The exported data solely encompasses bus positions and timestamp metrics.
