import fs from 'fs';
import { MockDatabase } from './server/db';
const db = new MockDatabase();
const data = {
  users: db.users,
  buses: db.buses,
  routes: db.routes,
  drivers: db.drivers,
  systemLogs: db.systemLogs,
  notifications: db.notifications
};
fs.writeFileSync('server/data/mock_db.json', JSON.stringify(data, null, 2));
console.log("Dumped");
