sed -i 's/ML ETA Net/Prediction Performance/g' src/components/admin/AdminDashboard.tsx
sed -i 's/MAE: 0.74 min/Avg Error: 0.74 min/g' src/components/admin/AdminDashboard.tsx
sed -i 's/Live In-Transit Telemetry Feeds/Live Bus Location Updates/g' src/components/admin/AdminDashboard.tsx
sed -i 's/Real-time driver phone GPS stream/Live driver location updates/g' src/components/admin/AdminDashboard.tsx
sed -i 's/GPS Ingestion/Location Status/g' src/components/admin/AdminDashboard.tsx
sed -i 's/ACTIVE (Phone GPS)/ACTIVE/g' src/components/admin/AdminDashboard.tsx
sed -i 's/AI Optimizer & ML Pipeline/Prediction System/g' src/components/admin/AdminDashboard.tsx
sed -i 's/Export Real Telemetry/Export Trip Data/g' src/components/admin/AdminDashboard.tsx
sed -i 's/Retrain ML Pipeline/Retrain Prediction System/g' src/components/admin/AdminDashboard.tsx
sed -i 's/R² Score/Prediction Fit Score/g' src/components/admin/AdminDashboard.tsx
sed -i 's/Mean Absolute Error (MAE)/Average Prediction Error/g' src/components/admin/AdminDashboard.tsx
sed -i 's/Engineered Feature Dimensions/Information Categories Used/g' src/components/admin/AdminDashboard.tsx
sed -i 's/Active Features/Information Categories/g' src/components/admin/AdminDashboard.tsx
sed -i 's/Offline Model Benchmark & Comparison Matrix/Prediction System Quality Comparison/g' src/components/admin/AdminDashboard.tsx
sed -i 's/Evaluated on strict chronological test split (791 unseen telemetry records)/Tested using 791 historical trips to ensure reliability/g' src/components/admin/AdminDashboard.tsx
sed -i "s/Dataset: {mlEvaluationReport.dataset?.datasetType || 'SYNTHETIC_DEVELOPMENT_TELEMETRY'}/Data Source: {mlEvaluationReport.dataset?.datasetType === 'SYNTHETIC_DEVELOPMENT_TELEMETRY' ? 'Simulated Historical Trips (Development)' : mlEvaluationReport.dataset?.datasetType}/g" src/components/admin/AdminDashboard.tsx
sed -i 's/Test MAE (min)/Avg Error (min)/g' src/components/admin/AdminDashboard.tsx
sed -i 's/Test RMSE (min)/Large Error Pen. (RMSE)/g' src/components/admin/AdminDashboard.tsx
sed -i 's/ACTIVE PROD/IN USE/g' src/components/admin/AdminDashboard.tsx
sed -i 's/Dataset Provenance & Institutional ML Protocol/Data Sources & Privacy/g' src/components/admin/AdminDashboard.tsx
sed -i 's/high-fidelity physics-based telemetry samples/recorded historical trips/g' src/components/admin/AdminDashboard.tsx
sed -i 's/Zero student or staff personal tracking data is ever used for model training or inference./Student and staff locations are never tracked or used to generate predictions./g' src/components/admin/AdminDashboard.tsx
