import fs from 'fs';
import path from 'path';
import { apiRouter } from './server/api';
import express from 'express';
import * as http from 'http';

const DATA_DIR = path.join(process.cwd(), 'server', 'data');
if (fs.existsSync(path.join(DATA_DIR, 'telemetry.json'))) {
  fs.unlinkSync(path.join(DATA_DIR, 'telemetry.json'));
}
if (fs.existsSync(path.join(DATA_DIR, 'stop_events.json'))) {
  fs.unlinkSync(path.join(DATA_DIR, 'stop_events.json'));
}

async function startServer() {
  const app = express();
  app.use(express.json());
  // Need to force re-import or clear cache if we wanted true process restart,
  // but since we write to fs, we can just restart the express app
  // Wait, db in server/api.ts is a singleton. To really test restart, we must spawn a child process
  app.use('/api', apiRouter);
  const server = app.listen(0);
  return {
    port: (server.address() as any).port,
    close: () => new Promise(resolve => server.close(resolve))
  };
}

// We will use child_process.spawn to truly test process restart, 
// because Node module cache keeps `db` singleton alive in the same process.
