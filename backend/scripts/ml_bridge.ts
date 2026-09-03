const originalLog = console.log; const originalWarn = console.warn; console.log = console.error; console.warn = console.error;
import { mlPredictor } from "../../server/ml-predictor.js";
import { runFullMLTrainingPipeline } from "../../server/ml/train-and-evaluate.js";
import { mlInferenceEngine } from "../../server/ml/inference-engine.js";
import fs from 'fs';
import path from 'path';
const action = process.argv[2];
if (action === 'eta') {
    const tripId = process.argv[3];
    const weather = process.argv[4] || 'clear';
    const tripsPath = path.join(process.cwd(), "server", "data", "trips.json");
    let trips: any[] = [];
    try { trips = fs.existsSync(tripsPath) ? JSON.parse(fs.readFileSync(tripsPath, "utf8")) : []; } catch(e) {}
    const trip = trips.find(t => t.id === tripId) || {};
    
    const mockDbPath = path.join(process.cwd(), "server", "data", "mock_db.json");
    let routes: any[] = [];
    try { 
        const db = fs.existsSync(mockDbPath) ? JSON.parse(fs.readFileSync(mockDbPath, "utf8")) : {};
        routes = db.routes || [];
    } catch(e) {}
    
    const route = routes.find(r => r.id === trip.routeId) || {stops:[]};
    originalLog(JSON.stringify(mlPredictor.predictTripStopETAs(trip, route, weather as any)));
} else if (action === 'stats') {
    originalLog(JSON.stringify(mlPredictor.getModelStats()));
} else if (action === 'retrain') {
    try {
        const result = runFullMLTrainingPipeline();
        mlInferenceEngine.loadModelArtifact();
        originalLog(JSON.stringify(result));
    } catch (e) {
        console.error(e);
        process.exit(1);
    }
}
