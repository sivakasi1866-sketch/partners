import os

student_tsx = """import React, { useState } from 'react';
import { User, Trip, Route } from '../../types';
import { MapPin, Navigation, Clock, Bell, Info } from 'lucide-react';
import { LiveBusMap } from '../map/LiveBusMap';

interface StudentDashboardProps {
  currentUser: User;
  routes: Route[];
  activeTrips: Trip[];
  onRefreshData: () => void;
}

export const StudentDashboard: React.FC<StudentDashboardProps> = ({
  currentUser,
  routes,
  activeTrips,
}) => {
  const [selectedRouteId, setSelectedRouteId] = useState<string>('');

  const displayedTrips = selectedRouteId 
    ? activeTrips.filter(t => t.routeId === selectedRouteId)
    : activeTrips;

  return (
    <div className="space-y-6">
      <div className="card-3d p-6 bg-gradient-to-br from-slate-900 to-indigo-950/50">
        <h2 className="text-2xl font-bold text-white mb-2">My Transit</h2>
        <p className="text-slate-400 text-sm mb-6">Select a route to track its live location and estimated arrival time.</p>
        
        <select
          value={selectedRouteId}
          onChange={e => setSelectedRouteId(e.target.value)}
          className="w-full md:max-w-md bg-slate-800/80 border border-slate-700/50 rounded-xl px-4 py-3 text-slate-200 focus:outline-none focus:ring-2 focus:ring-cyan-500"
        >
          <option value="">All Routes</option>
          {routes.map(r => (
            <option key={r.id} value={r.id}>{r.routeNumber} - {r.name}</option>
          ))}
        </select>
      </div>

      {displayedTrips.length === 0 ? (
        <div className="card-3d p-12 text-center text-slate-400">
          <Navigation className="w-12 h-12 mx-auto mb-4 opacity-50 text-slate-500" />
          <h3 className="text-lg font-semibold text-slate-300">No Active Buses</h3>
          <p className="text-sm mt-1">There are no buses currently broadcasting on this route.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-4">
            <h3 className="font-bold text-slate-300 text-lg">Active Buses</h3>
            {displayedTrips.map(trip => {
              const route = routes.find(r => r.id === trip.routeId);
              const nextStop = route?.stops[trip.nextStopIndex]?.stopName || 'End of Route';
              const etaMinutes = trip.delayMinutes > 0 ? trip.delayMinutes + 5 : 5; // Simplified ETA display

              return (
                <div key={trip.id} className="card-3d p-5 border-slate-700/50 hover:border-cyan-500/50">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h4 className="text-xl font-bold text-white text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">
                        {trip.busNumber}
                      </h4>
                      <p className="text-xs text-slate-400">{route?.routeNumber}</p>
                    </div>
                    <span className="px-2 py-1 bg-cyan-500/10 text-cyan-400 text-xs font-bold uppercase rounded border border-cyan-500/20">
                      Live
                    </span>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex items-start gap-3">
                      <MapPin className="w-4 h-4 text-emerald-400 mt-0.5" />
                      <div>
                        <p className="text-xs text-slate-400">Next Stop</p>
                        <p className="text-sm font-semibold text-slate-200">{nextStop}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-start gap-3">
                      <Clock className="w-4 h-4 text-cyan-400 mt-0.5" />
                      <div>
                        <p className="text-xs text-slate-400">Arriving In</p>
                        <p className="text-sm font-semibold text-cyan-400">{etaMinutes} min</p>
                      </div>
                    </div>
                  </div>
                  
                  <details className="mt-4 group text-xs text-slate-400">
                    <summary className="cursor-pointer hover:text-slate-300 list-none flex items-center gap-1">
                      <Info className="w-3 h-3" /> How is this estimated?
                    </summary>
                    <div className="mt-2 p-3 bg-slate-800/50 rounded-lg border border-slate-700/30">
                      The system estimates arrival time using the bus's current location, speed, remaining route distance, traffic conditions, and historical travel patterns.
                    </div>
                  </details>
                </div>
              );
            })}
          </div>
          <div className="lg:col-span-2">
            <div className="card-3d overflow-hidden h-[600px] border border-slate-700/50">
              <LiveBusMap 
                routes={routes} 
                activeTrips={activeTrips} 
                selectedRouteId={selectedRouteId} 
                heightClass="h-full"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
"""
with open("src/components/student/StudentDashboard.tsx", "w") as f:
    f.write(student_tsx)
print("StudentDashboard updated")
