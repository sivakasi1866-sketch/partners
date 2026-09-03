import React, { useState } from 'react';
import { Bus } from '../../types';
import { api } from '../../services/api';
import { Plus, Edit, Trash2, Save, Search } from 'lucide-react';

interface Props {
  buses: Bus[];
  onRefresh: () => void;
}

export const BusManagement: React.FC<Props> = ({ buses, onRefresh }) => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingBusId, setEditingBusId] = useState<string | null>(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  
  const [formData, setFormData] = useState<Partial<Bus>>({});

  const filteredBuses = buses.filter(b => 
    b.busNumber.toLowerCase().includes(searchQuery.toLowerCase()) || 
    (b.registrationNumber && b.registrationNumber.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const resetForm = () => {
    setFormData({});
    setShowAddForm(false);
    setEditingBusId(null);
  };

  const handleAddClick = () => {
    resetForm();
    setShowAddForm(true);
  };

  const handleEditClick = (bus: Bus) => {
    resetForm();
    setFormData(bus);
    setEditingBusId(bus.id);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingBusId) {
        await api.authFetch(`/api/buses/${editingBusId}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        });
      } else {
        await api.authFetch(`/api/buses`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        });
      }
      onRefresh();
      resetForm();
    } catch (err: any) {
      alert(err.message || "Failed to save record");
    }
  };

  const handleDelete = async (id: string) => {
    try {
      const res = await api.authFetch(`/api/buses/${id}`, { method: 'DELETE' });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || "Failed to delete");
      onRefresh();
      setDeleteConfirmId(null);
    } catch (err: any) {
      alert(err.message || "Failed to delete record");
      setDeleteConfirmId(null);
    }
  };

  return (
    <div className="card-3d p-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
        <div>
          <h3 className="text-xl font-bold text-white">Manage Buses</h3>
          <p className="text-sm text-slate-400">Add, edit, or remove fleet vehicles.</p>
        </div>
        <div className="flex gap-2">
          {!showAddForm && !editingBusId && (
            <button
              onClick={handleAddClick}
              className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition-colors font-medium text-sm"
            >
              <Plus className="w-4 h-4" /> Add Bus
            </button>
          )}
        </div>
      </div>

      {(showAddForm || editingBusId) ? (
        <form onSubmit={handleSave} className="bg-slate-800/80 p-5 rounded-xl border border-slate-700/50 mb-6">
          <h4 className="text-lg font-semibold text-white mb-4">
            {editingBusId ? 'Edit Bus' : 'Add New Bus'}
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Bus Number</label>
              <input
                type="text"
                required
                value={formData.busNumber || ''}
                onChange={e => setFormData({...formData, busNumber: e.target.value})}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Registration Number</label>
              <input
                type="text"
                value={formData.registrationNumber || ''}
                onChange={e => setFormData({...formData, registrationNumber: e.target.value})}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Capacity</label>
              <input
                type="number"
                value={formData.capacity || 40}
                onChange={e => setFormData({...formData, capacity: parseInt(e.target.value) || 0})}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
              />
            </div>
            
            {editingBusId && (
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Status</label>
                <select
                  value={formData.status || 'idle'}
                  onChange={e => setFormData({...formData, status: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
                >
                  <option value="idle">Idle</option>
                  <option value="in_transit">In Transit</option>
                  <option value="maintenance">Maintenance</option>
                  <option value="inactive">Inactive</option>
                </select>
              </div>
            )}
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={resetForm}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors text-sm"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition-colors text-sm font-medium"
            >
              <Save className="w-4 h-4" /> Save Changes
            </button>
          </div>
        </form>
      ) : (
        <>
          <div className="mb-4 relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search buses..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-white focus:border-cyan-500 focus:outline-none text-sm"
            />
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-700/50 text-slate-400 text-sm">
                  <th className="pb-3 font-medium">Bus Number</th>
                  <th className="pb-3 font-medium">Registration</th>
                  <th className="pb-3 font-medium">Capacity</th>
                  <th className="pb-3 font-medium">Status</th>
                  <th className="pb-3 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/50">
                {filteredBuses.map(bus => (
                  <tr key={bus.id} className="text-sm">
                    <td className="py-3 text-white font-medium">{bus.busNumber}</td>
                    <td className="py-3 text-slate-300">{bus.registrationNumber || '-'}</td>
                    <td className="py-3 text-slate-300">{bus.capacity || '-'}</td>
                    <td className="py-3 text-slate-300 capitalize">{bus.status?.replace('_', ' ')}</td>
                    <td className="py-3 text-right">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => handleEditClick(bus)}
                          className="p-1.5 text-slate-400 hover:text-cyan-400 bg-slate-800 hover:bg-slate-700 rounded transition-colors"
                          title="Edit"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => setDeleteConfirmId(bus.id)}
                          className="p-1.5 text-slate-400 hover:text-rose-400 bg-slate-800 hover:bg-slate-700 rounded transition-colors"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {filteredBuses.length === 0 && (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-slate-500">
                      No buses found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirmId && (
        <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <h3 className="text-xl font-bold text-white mb-2">Delete Bus?</h3>
            <p className="text-slate-300 mb-6">
              You are about to remove this bus from the fleet. This action cannot be undone. Are you sure you want to proceed?
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDeleteConfirmId(null)}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors font-medium text-sm"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(deleteConfirmId)}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg transition-colors font-medium text-sm"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
