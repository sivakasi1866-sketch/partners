import React, { useState } from 'react';
import { Route, RouteStop } from '../../types';
import { api } from '../../services/api';
import { Navigation, Plus, Edit, Trash2, MapPin, Save, X } from 'lucide-react';

interface Props {
  routes: Route[];
  fetchRoutes: () => void;
}

export const RouteManagement: React.FC<Props> = ({ routes, fetchRoutes }) => {
  const [showAddRoute, setShowAddRoute] = useState(false);
  const [deleteRouteConfirmId, setDeleteRouteConfirmId] = useState<string | null>(null);
  const [deleteStopConfirm, setDeleteStopConfirm] = useState<{routeId: string, stopId: string} | null>(null);
  const [newRouteName, setNewRouteName] = useState('');
  
  const [editingRouteId, setEditingRouteId] = useState<string | null>(null);
  const [editRouteName, setEditRouteName] = useState('');

  const [expandedRouteId, setExpandedRouteId] = useState<string | null>(null);

  const [showAddStop, setShowAddStop] = useState<string | null>(null);
  const [newStop, setNewStop] = useState({ name: '', lat: '', lng: '' });

  const handleCreateRoute = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRouteName) return;
    try {
      await api.authFetch('/api/routes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newRouteName, routeNumber: newRouteName })
      });
      setNewRouteName('');
      setShowAddRoute(false);
      fetchRoutes();
    } catch (err) {
      alert("Failed to create route: " + err);
    }
  };

  const handleDeleteRoute = async (id: string) => {
    if (!window.confirm("Delete this route?")) return;
    try {
      await api.authFetch(`/api/routes/${id}`, { method: 'DELETE' });
      fetchRoutes();
    } catch (err) {
      alert("Failed to delete route (it may be in use).");
    }
  };

  const handleCreateStop = async (routeId: string) => {
    if (!newStop.name || !newStop.lat || !newStop.lng) return;
    try {
      await api.authFetch(`/api/routes/${routeId}/stops`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          stopName: newStop.name,
          name: newStop.name,
          latitude: parseFloat(newStop.lat),
          longitude: parseFloat(newStop.lng)
        })
      });
      setNewStop({ name: '', lat: '', lng: '' });
      setShowAddStop(null);
      fetchRoutes();
    } catch (err) {
      alert("Failed to create stop: " + err);
    }
  };

  const handleDeleteStop = async (routeId: string, stopId: string) => {
    if (!window.confirm("Delete this stop?")) return;
    try {
      await api.authFetch(`/api/routes/${routeId}/stops/${stopId}`, { method: 'DELETE' });
      fetchRoutes();
    } catch (err) {
      alert("Failed to delete stop");
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-bold text-base text-slate-900">Campus Routes & Waypoint Stops</h3>
          <p className="text-xs text-slate-600">Geometry and scheduled timetable sequences</p>
        </div>
        <button
          onClick={() => setShowAddRoute(!showAddRoute)}
          className="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all shadow-md shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>New Route</span>
        </button>
      </div>

      {showAddRoute && (
        <form onSubmit={handleCreateRoute} className="bg-white/50 p-4 rounded-xl border border-gray-200/50 space-y-3">
          <h4 className="text-sm font-bold text-slate-900 mb-2">Create New Route</h4>
          <div>
            <label className="text-xs text-slate-600 mb-1 block">Route Name</label>
            <input 
              type="text" 
              value={newRouteName} 
              onChange={e => setNewRouteName(e.target.value)}
              placeholder="e.g. Campus Loop A"
              className="w-full bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm text-slate-900"
              required
            />
          </div>
          <div className="flex justify-end gap-2">
            <button type="button" onClick={() => setShowAddRoute(false)} className="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-900">Cancel</button>
            <button type="submit" className="px-3 py-1.5 bg-emerald-500 text-slate-950 rounded-lg text-xs font-bold">Save Route</button>
          </div>
        </form>
      )}

      <div className="space-y-6">
        {routes.map(route => (
          <div key={route.id} className="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-3">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2 cursor-pointer" onClick={() => setExpandedRouteId(expandedRouteId === route.id ? null : route.id)}>
                <span className="w-3 h-3 rounded-full" style={{ backgroundColor: route.color || '#34d399' }}></span>
                <h4 className="font-bold text-sm text-slate-900">{route.routeNumber || route.name}</h4>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-mono text-xs text-slate-600">
                  {route.stops?.length || 0} Stops
                </span>
                <button onClick={() => setDeleteRouteConfirmId(route.id)} className="text-rose-400 hover:text-rose-300 p-1">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Stop sequence tags */}
            <div className="flex flex-wrap gap-2 pt-1">
              {route.stops?.map(stop => (
                <div key={stop.id} className="bg-white border border-gray-200 px-2.5 py-1 rounded-xl text-xs flex items-center gap-1.5 text-slate-700 font-mono group">
                  <span className="text-emerald-400 font-bold">#{stop.sequence}</span>
                  <span>{stop.stopName || stop.name}</span>
                  <button onClick={() => handleDeleteStop(route.id, stop.id)} className="opacity-0 group-hover:opacity-100 text-rose-400 ml-1">
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
              
              <button 
                onClick={() => setShowAddStop(route.id)} 
                className="bg-white hover:bg-gray-50 border border-gray-200 border-dashed px-2.5 py-1 rounded-xl text-xs flex items-center gap-1 text-slate-600"
              >
                <Plus className="w-3 h-3" /> Add Stop
              </button>
            </div>

            {showAddStop === route.id && (
              <div className="mt-3 bg-white border border-gray-200 rounded-xl p-3 grid grid-cols-4 gap-2 items-end">
                <div className="col-span-2">
                  <label className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1">Stop Name</label>
                  <input type="text" value={newStop.name} onChange={e => setNewStop({...newStop, name: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg px-2 py-1 text-xs text-slate-900" placeholder="Library" />
                </div>
                <div>
                  <label className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1">Lat</label>
                  <input type="number" step="any" value={newStop.lat} onChange={e => setNewStop({...newStop, lat: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg px-2 py-1 text-xs text-slate-900" placeholder="10.5" />
                </div>
                <div>
                  <label className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1">Lng</label>
                  <input type="number" step="any" value={newStop.lng} onChange={e => setNewStop({...newStop, lng: e.target.value})} className="w-full bg-gray-50 border border-gray-200 rounded-lg px-2 py-1 text-xs text-slate-900" placeholder="20.5" />
                </div>
                <div className="col-span-4 flex justify-end gap-2 mt-1">
                  <button onClick={() => setShowAddStop(null)} className="px-2 py-1 text-[10px] text-slate-600 hover:text-slate-900">Cancel</button>
                  <button onClick={() => handleCreateStop(route.id)} className="px-3 py-1 bg-emerald-500 text-slate-950 rounded-md text-[10px] font-bold">Save Stop</button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
      {deleteRouteConfirmId && (
        <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <h3 className="text-xl font-bold text-white mb-2">Delete Route?</h3>
            <p className="text-slate-300 mb-6">
              You are about to remove this route. This action cannot be undone. Are you sure you want to proceed?
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDeleteRouteConfirmId(null)}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors font-medium text-sm"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDeleteRoute(deleteRouteConfirmId)}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg transition-colors font-medium text-sm"
              >
                Delete Route
              </button>
            </div>
          </div>
        </div>
      )}

      {deleteStopConfirm && (
        <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <h3 className="text-xl font-bold text-white mb-2">Delete Stop?</h3>
            <p className="text-slate-300 mb-6">
              You are about to remove this stop from the route. This action cannot be undone. Are you sure you want to proceed?
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDeleteStopConfirm(null)}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors font-medium text-sm"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDeleteStop(deleteStopConfirm.routeId, deleteStopConfirm.stopId)}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg transition-colors font-medium text-sm"
              >
                Delete Stop
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
