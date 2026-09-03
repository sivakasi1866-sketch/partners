sed -i 's/updating real-time telemetry/updating live bus locations/g' src/components/modals/AIAssistantModal.tsx
sed -i 's/Analyzing live telemetry/Analyzing live bus locations/g' src/components/modals/AIAssistantModal.tsx

sed -i 's/Vehicle-Specific GPS Telemetry/Vehicle-Specific GPS Location/g' src/components/modals/PrivacyModal.tsx
sed -i 's/fed into the ML ETA engine/used to estimate arrival times/g' src/components/modals/PrivacyModal.tsx
sed -i 's/Backend API rejects/System rejects/g' src/components/modals/PrivacyModal.tsx

sed -i 's/Real ML ETA Pipeline & Model Artifact Verification/Prediction System Verification/g' src/components/modals/TestRunnerModal.tsx
sed -i 's/Verify offline-trained GBDT artifact loading, feature scaling, and microsecond inference execution./Verify prediction system loading, data preparation, and execution speed./g' src/components/modals/TestRunnerModal.tsx
sed -i 's/Dataset Integrity & Synthetic Development Pipeline/Historical Data Integrity & Simulation Pipeline/g' src/components/modals/TestRunnerModal.tsx
sed -i 's/Validate synthetic development dataset generation, feature bounds, and non-negative travel times./Validate historical data simulation, value ranges, and reasonable travel times./g' src/components/modals/TestRunnerModal.tsx
sed -i 's/Stop-Level ETA Inference & Confidence Calculation/Stop-Level Arrival Prediction & Reliability Calculation/g' src/components/modals/TestRunnerModal.tsx
sed -i 's/System Compliance & ML Test Suite/System Compliance & Prediction Test Suite/g' src/components/modals/TestRunnerModal.tsx
sed -i 's/Automated verification of institutional safety rules & ML inference/Automated verification of safety rules & arrival predictions/g' src/components/modals/TestRunnerModal.tsx
sed -i 's/Runs diagnostic checks against privacy rules, GPS lifecycle, and ML engine./Runs diagnostic checks against privacy rules, GPS lifecycle, and the prediction system./g' src/components/modals/TestRunnerModal.tsx

