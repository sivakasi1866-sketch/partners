# System Architecture

## Overview
The system relies on a local, zero-cost architecture comprised of a React/Vite SPA frontend communicating with a FastAPI backend server, utilizing local JSON stores for persistence to avoid external database expenses.

### 1. Frontend (React + Vite + TypeScript)
* **Design**: Single Page Application (SPA).
* **Styling**: Tailwind CSS.
* **Component Architecture**: Modular component structure segregating Admin, Driver, Student, and Staff views based strictly on backend-verified roles.
* **Integrations**: Zero-cost visual map mapping.

### 2. Backend (FastAPI + Python)
* **Core API**: Manages authentication, assignment, RBAC, telemetry ingress, and system state.
* **Haversine Engine**: Handles strict backend-authoritative detection of bus stops based on a 50-meter bounding radius.
* **Persistence**: Local `.json` files (`server/data/`) managing real-time and historical states.

### 3. ML Pipeline & ETA
* **Data Flow**: Consumes historical telemetry to output predictions.
* **Architecture**: A RandomForestRegressor model stored securely within `backend/app/ml/`. 
* **Fallback**: Provides heuristic ETAs for buses actively operating without sufficient ML training data coverage.

### End-to-End Workflow (Driver)
1. Driver Phone authenticates.
2. Clicks **Start Trip**.
3. Frontend begins GPS `watchPosition`.
4. FastAPI validates JWT, sets Trip state to `in_progress`.
5. Telemetry periodically streams to FastAPI.
6. Backend calculates stop bounds via Haversine and triggers ETA inference.
7. Student/Staff clients poll the backend for visual updates.
8. Driver clicks **Stop Trip**.
9. FastAPI marks Trip `completed`.
10. Frontend permanently halts `watchPosition`.
