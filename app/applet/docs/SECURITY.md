# Security Architecture

## Authentication & Authorization
* **JWT Identity**: Authentication relies strictly on signed JSON Web Tokens (JWT). The backend explicitly extracts identity and role from the JWT, outright ignoring any client-provided identity assertions.
* **RBAC (Role-Based Access Control)**:
  * **Students**: Read-only access to buses, routes, and ETAs.
  * **Staff**: Read-only access.
  * **Drivers**: Read/Write access strictly bounded to their actively assigned trips. Cannot access administrative endpoints.
  * **Admin**: Unrestricted read/write capabilities including telemetry export, ML retraining, and assignments.

## Data & Assignment Protection
* **Driver Ownership**: Telemetry (`/api/trips/update-gps`) automatically overwrites the `driverId` payload with the authorized JWT subject. 
* **Duplicate Protection**: Trip start, stop, and telemetry collection are safeguarded against duplicates via backend validation to ensure absolute state integrity.
* **Import System**: The Excel/Data import system validates files up to a 5MB threshold, restricting file extensions directly, and performs a full structural validation before atomic commits.

## Threat Model

| Threat | Impact | Mitigation | Status |
|---|---|---|---|
| Student/Staff GPS tracking | Severe Privacy Breach | UI logic prevents collection. API blocks non-driver roles entirely. | Mitigated |
| Driver Impersonation | Moderate Security Breach | Endpoints derive authoritative identity from the verified JWT, completely overriding payload values. | Mitigated |
| Unauthorized Telemetry | Corrupt ML Data | Updates are rejected if the trip is inactive, completed, or not assigned to the authenticated driver. | Mitigated |
| Malicious Excel Upload | Backend Crash / Remote Execution | 5MB limit. Restrictive MIME/extension checks. Backend logic gracefully handles malformed rows. | Mitigated |
| Secret Leakage | Critical Compromise | JWT keys are injected via environment variables. Dummy keys are strictly for sandbox defaults. | Mitigated |

## Known Secrets
A dummy fallback JWT secret (`fallback_secret_for_development_only_12345`) is present in `config.py` for sandbox deployments. Production environments **must** override this via the `JWT_SECRET_KEY` environment variable.
