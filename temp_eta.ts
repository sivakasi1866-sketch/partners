
import { mlPredictor } from "./server/ml-predictor";
import { MockDatabase } from "./server/db";
const db = new MockDatabase();
const tripsPath = require("path").join(process.cwd(), "server", "data", "trips.json");
let trips = [];
try { trips = require("fs").existsSync(tripsPath) ? JSON.parse(require("fs").readFileSync(tripsPath, "utf8")) : []; } catch(e) {}
const trip = trips.find(t => t.id === "trip-1788168627780") || {};
const route = db.routes.find(r => r.id === trip.routeId) || {stops:[]};
console.log(JSON.stringify(mlPredictor.predictTripStopETAs(trip, route, "clear")));
        