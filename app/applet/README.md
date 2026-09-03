# Elite Bus Prediction System

## Overview
Elite Bus Prediction is a zero-cost, privacy-first smart bus tracking and ETA prediction system designed for educational institutions. It features role-based dashboards, Haversine-based stop detection, and a machine learning pipeline for real-time ETA predictions. 

## Key Features
* **Role-Based Dashboards**: Distinct, securely segregated views for Admins, Drivers, Staff, and Students.
* **Privacy-First GPS**: 
  * Student and Staff GPS tracking is **never** collected.
  * Driver GPS tracking is **only** active during an explicitly started, assigned trip.
* **Smart Stop Detection**: Backend-authoritative Haversine stop detection (50-meter threshold).
* **Machine Learning ETA**: Uses a RandomForest model for ETA predictions based on historical telemetry, falling back to heuristics if required.
* **Zero Cost**: Runs entirely on local JSON persistence without the need for paid cloud databases, maps, or messaging services.

## BLOCKED COMPONENTS
The following components are formally **BLOCKED** to strictly adhere to the ₹0 / $0 additional cost constraint and infrastructure sandbox limitations:
* **AGENT 3 (PostgreSQL)** — Blocked (Zero-cost requirement)
* **AGENT 11 (Firebase)** — Blocked (Zero-cost requirement)
* **AGENT 14 (FCM)** — Blocked (Zero-cost requirement)
* **AGENT 16 (Flutter App)** — Blocked (Flutter SDK unavailable in environment)

## Quick Start
See `docs/DEPLOYMENT.md` for local deployment instructions.
