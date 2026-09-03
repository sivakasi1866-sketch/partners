import os

driver_tsx = """import React, { useState } from 'react';
import { User, Trip, Route as RouteType, Bus } from '../../types';
import { Navigation, Play, Square, MapPin, Bus as BusIcon, ShieldAlert } from 'lucide-react';
import { api } from '../../services/api';

interface DriverDashboardProps {
  currentUser: User;
  buses: Bus[];
  routes: RouteType[];
  activeTrips: Trip[];
  onRefreshData: () => void;
}

export const DriverDashboard: React.FC<DriverDashboardProps> = ({
  currentUser,
  buses,
  routes,
  activeTrips,
  onRefreshData
}) => {
  const [selectedRouteId, setSelectedRouteId] = useState('');
  const [selectedBusId, setSelectedBusId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // A driver can only have one active trip at a time
  const activeTrip = activeTrips.find(t => t.driverId === currentUser.id);

  const handleStartTrip = async () => {
    if (!selectedRouteId || !selectedBusId) return;
    setIsLoading(true);
    try {
      await api.startTrip({
        routeId: selectedRouteId,
        busId: selectedBusId
      });
      await onRefreshData();
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStopTrip = async () => {
    if (!activeTrip) return;
    setIsLoading(true);
    try {
      await api.completeTrip(activeTrip.id);
      await onRefreshData();
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNextStop = async () => {
    if (!activeTrip) return;
    setIsLoading(true);
    try {
      const route = routes.find(r => r.id === activeTrip.routeId);
      if (!route) return;
      const nextIndex = activeTrip.currentStopIndex + 1;
      if (nextIndex < route.stops.length) {
        await api.updateTripProgress(activeTrip.id, nextIndex, nextIndex < route.stops.length - 1 ? nextIndex + 1 : nextIndex);
      } else {
        await handleStopTrip();
      }
      await onRefreshData();
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-slate-100">Driver Console</h2>
        <p className="text-slate-400 text-sm">Manage your current route and GPS broadcasting</p>
      </div>

      {!activeTrip ? (
        <div className="card-3d p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-blue-500/20 rounded-xl">
              <BusIcon className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">Start New Trip</h3>
              <p className="text-sm text-slate-400">Select route and vehicle to begin broadcasting</p>
            </div>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Select Route</label>
              <select
                value={selectedRouteId}
                onChange={e => setSelectedRouteId(e.target.value)}
                className="w-full bg-slate-800/80 border border-slate-700/50 rounded-xl px-4 py-3 text-slate-200 focus:outline-none focus:ring-2 focus:ring-cyan-500"
              >
                <option value="">-- Choose Route --</option>
                {routes.map(r => (
                  <option key={r.id} value={r.id}>{r.routeNumber} - {r.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Select Vehicle</label>
              <select
                value={selectedBusId}
                onChange={e => setSelectedBusId(e.target.value)}
                className="w-full bg-slate-800/80 border border-slate-700/50 rounded-xl px-4 py-3 text-slate-200 focus:outline-none focus:ring-2 focus:ring-cyan-500"
              >
                <option value="">-- Choose Bus --</option>
                {buses.map(b => (
                  <option key={b.id} value={b.id}>{b.busNumber} ({b.capacity} seats)</option>
                ))}
              </select>
            </div>
            
            <button
              onClick={handleStartTrip}
              disabled={!selectedRouteId || !selectedBusId || isLoading}
              className="w-full py-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold rounded-xl flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-emerald-900/20 mt-6"
            >
              <Play className="w-5 h-5" /> START TRIP & ENABLE GPS
            </button>
          </div>
        </div>
      ) : (
        <div className="card-3d p-6 border-emerald-500/30 shadow-emerald-900/10">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-emerald-500/20 rounded-xl border border-emerald-500/30">
                <Navigation className="w-6 h-6 text-emerald-400 animate-pulse" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">Active Trip</h3>
                <p className="text-sm text-emerald-400 font-medium">GPS Broadcasting Live</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-white">{activeTrip.busNumber}</div>
              <div className="text-sm text-slate-400">{activeTrip.routeNumber}</div>
            </div>
          </div>
          
          <div className="bg-slate-900/50 rounded-xl p-4 mb-6 border border-slate-700/50">
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="text-slate-400">Current Stop</span>
              <span className="font-bold text-slate-200">
                {routes.find(r => r.id === activeTrip.routeId)?.stops[activeTrip.currentStopIndex]?.stopName || 'Unknown'}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm pt-2 border-t border-slate-700/50">
              <span className="text-slate-400">Next Stop</span>
              <span className="font-bold text-cyan-400">
                {routes.find(r => r.id === activeTrip.routeId)?.stops[activeTrip.nextStopIndex]?.stopName || 'End of Route'}
              </span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 gap-4">
            <button
              onClick={handleNextStop}
              disabled={isLoading}
              className="w-full py-5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg"
            >
              <MapPin className="w-6 h-6" /> ARRIVED AT NEXT STOP
            </button>
            
            <button
              onClick={handleStopTrip}
              disabled={isLoading}
              className="w-full py-4 bg-slate-800 hover:bg-rose-900/40 text-rose-400 hover:text-rose-300 font-bold rounded-xl flex items-center justify-center gap-2 transition-all border border-slate-700 hover:border-rose-500/50"
            >
              <Square className="w-5 h-5" /> STOP TRIP & DISABLE GPS
            </button>
          </div>
        </div>
      )}
      
      <div className="bg-amber-900/20 border border-amber-700/30 rounded-xl p-4 flex gap-3 text-amber-200/80 text-sm">
        <ShieldAlert className="w-5 h-5 shrink-0 text-amber-500" />
        <p>
          <strong>Privacy Notice:</strong> Your location is only tracked while a trip is active. When you press "Stop Trip", all GPS broadcasting immediately terminates.
        </p>
      </div>
    </div>
  );
};
"""
with open("src/components/driver/DriverDashboard.tsx", "w") as f:
    f.write(driver_tsx)
print("DriverDashboard updated")
