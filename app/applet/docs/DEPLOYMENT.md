# Deployment Guide

This application is strictly designed to operate within a ₹0 / $0 environment footprint, utilizing local infrastructure.

## Requirements
* Python 3.10+
* Node.js (via Bun/npm)
* Vite

## Environment Variables
Create a `.env` file in the root if custom configurations are required (the backend will fall back to safe sandbox defaults):
```env
JWT_SECRET_KEY=<generate_secure_random_key>
ENVIRONMENT=production
```

## Running the Application Locally

1. **Install Dependencies and Start Servers (Single Command)**
   The backend and frontend are mapped to a combined start command utilizing `vite` and `uvicorn`.

   To run the production-ready unified build:
   ```bash
   npm run build
   npm run start
   ```

   To run in development mode (hot-reloading enabled):
   ```bash
   npm run dev
   ```

2. **Accessing the Application**
   * **Frontend**: `http://localhost:3000`
   * **API Docs**: `http://localhost:3000/docs` (Swagger UI)

## Backup and Recovery Limitations
Because the system employs local JSON persistence to satisfy the zero-cost requirement:
* **Durability**: High concurrency writes may experience slight performance limitations.
* **Backup**: Administrators should periodically copy the contents of `server/data/*.json` to an external backup location to prevent data loss.
* **Restore**: Replace the `.json` files and restart the server.
