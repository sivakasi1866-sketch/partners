import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';

export const AssignmentManagement = ({ drivers, buses, routes, fetchAssignments }: any) => {
  const [assignments, setAssignments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [selectedDriver, setSelectedDriver] = useState('');
  const [selectedBus, setSelectedBus] = useState('');
  const [selectedRoute, setSelectedRoute] = useState('');
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  const loadAssignments = async () => {
    try {
      setLoading(true);
      const res = await api.authFetch('/api/assignments');
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || 'Failed to load assignments');
      setAssignments(data.assignments || []);
      setError('');
    } catch (err: any) {
      setError(err.message || 'Failed to load assignments');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAssignments();
  }, []);

  const handleAssign = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDriver || !selectedBus || !selectedRoute) return;
    try {
      setError('');
      const res = await api.authFetch('/api/assignments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          driverId: selectedDriver,
          busId: selectedBus,
          routeId: selectedRoute
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || 'Failed to create assignment');

      setSelectedDriver('');
      setSelectedBus('');
      setSelectedRoute('');
      loadAssignments();
      if (fetchAssignments) fetchAssignments();
    } catch (err: any) {
      setError(err.message || 'Failed to create assignment');
    }
  };

  const handleRemove = async (driverId: string) => {
    try {
      setError('');
      const res = await api.authFetch(`/api/assignments/${driverId}`, { method: 'DELETE' });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || 'Failed to remove assignment');
      loadAssignments();
      if (fetchAssignments) fetchAssignments();
      setDeleteConfirmId(null);
    } catch (err: any) {
      setError(err.message || 'Failed to remove assignment');
      setDeleteConfirmId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="card-3d p-6">
        <h3 className="text-xl font-bold text-white mb-4">Operational Assignments</h3>
        {error && <div className="mb-4 bg-rose-500/10 text-rose-400 p-3 rounded-xl border border-rose-500/20 text-xs font-mono">{error}</div>}
        
        <form onSubmit={handleAssign} className="flex flex-wrap gap-4 items-end mb-6 bg-slate-800/80 p-5 rounded-xl border border-slate-700/50">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-xs text-slate-600 mb-1">Driver</label>
            <select value={selectedDriver} onChange={(e) => setSelectedDriver(e.target.value)} className="w-full bg-white border border-gray-200 text-slate-800 rounded p-2 text-sm" required>
              <option value="">Select Driver</option>
              {drivers.map((d: any) => (
                <option key={d.id} value={d.id}>{d.name} ({d.email})</option>
              ))}
            </select>
          </div>
          <div className="flex-1 min-w-[200px]">
            <label className="block text-xs text-slate-600 mb-1">Bus</label>
            <select value={selectedBus} onChange={(e) => setSelectedBus(e.target.value)} className="w-full bg-white border border-gray-200 text-slate-800 rounded p-2 text-sm" required>
              <option value="">Select Bus</option>
              {buses.map((b: any) => (
                <option key={b.id} value={b.id}>{b.busNumber} {b.status !== 'idle' ? `(${b.status})` : ''}</option>
              ))}
            </select>
          </div>
          <div className="flex-1 min-w-[200px]">
            <label className="block text-xs text-slate-600 mb-1">Route</label>
            <select value={selectedRoute} onChange={(e) => setSelectedRoute(e.target.value)} className="w-full bg-white border border-gray-200 text-slate-800 rounded p-2 text-sm" required>
              <option value="">Select Route</option>
              {routes.map((r: any) => (
                <option key={r.id} value={r.id}>{r.routeNumber} - {r.name}</option>
              ))}
            </select>
          </div>
          <button type="submit" className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-4 py-2 rounded text-sm transition-colors h-[38px]">
            Assign
          </button>
        </form>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm border-collapse">
            <thead>
              <tr className="border-b border-slate-700/50 text-slate-600 font-semibold">
                <th className="py-2 px-3">Driver</th>
                <th className="py-2 px-3">Bus</th>
                <th className="py-2 px-3">Route</th>
                <th className="py-2 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {assignments.length === 0 && (
                <tr><td colSpan={4} className="py-4 text-center text-slate-400">No active assignments</td></tr>
              )}
              {assignments.map(a => (
                <tr key={a.driverId} className="hover:bg-white/40">
                  <td className="py-3 px-3 text-slate-800 font-bold">{a.driverName}</td>
                  <td className="py-3 px-3 text-slate-700">{buses.find((b: any) => b.id === a.busId)?.busNumber || a.busId}</td>
                  <td className="py-3 px-3 text-slate-700">{routes.find((r: any) => r.id === a.routeId)?.name || a.routeId}</td>
                  <td className="py-3 px-3 text-right">
                    <button onClick={() => setDeleteConfirmId(a.driverId)} className="text-rose-400 hover:text-rose-300 text-xs font-bold bg-rose-500/10 px-2 py-1 rounded">
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {deleteConfirmId && (
        <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <h3 className="text-xl font-bold text-white mb-2">Remove Assignment?</h3>
            <p className="text-slate-300 mb-6">
              You are about to remove this assignment. This action cannot be undone. Are you sure you want to proceed?
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDeleteConfirmId(null)}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors font-medium text-sm"
              >
                Cancel
              </button>
              <button
                onClick={() => handleRemove(deleteConfirmId)}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg transition-colors font-medium text-sm"
              >
                Remove Assignment
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
