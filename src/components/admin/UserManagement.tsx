import React, { useState, useEffect } from 'react';
import { User } from '../../types';
import { api } from '../../services/api';
import { Plus, Edit, Trash2, Save, Search } from 'lucide-react';

interface Props {
  role: 'student' | 'staff' | 'driver';
  title: string;
  description: string;
}

export const UserManagement: React.FC<Props> = ({ role, title, description }) => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingUserId, setEditingUserId] = useState<string | null>(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  
  const [formData, setFormData] = useState<Partial<User> & { password?: string }>({});

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await api.authFetch('/api/users');
      const data = await res.json();
      if (res.ok && data.users) {
        setUsers(data.users);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [role]);

  const filteredUsers = users.filter(u => u.role === role && 
    (u.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
     u.email.toLowerCase().includes(searchQuery.toLowerCase()) || 
     (u.studentId && u.studentId.toLowerCase().includes(searchQuery.toLowerCase())) ||
     (u.staffId && u.staffId.toLowerCase().includes(searchQuery.toLowerCase()))
    )
  );

  const resetForm = () => {
    setFormData({});
    setShowAddForm(false);
    setEditingUserId(null);
  };

  const handleAddClick = () => {
    resetForm();
    setFormData({ role });
    setShowAddForm(true);
  };

  const handleEditClick = (user: User) => {
    resetForm();
    setFormData(user);
    setEditingUserId(user.id);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      let res;
      if (editingUserId) {
        res = await api.authFetch(`/api/users/${editingUserId}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        });
      } else {
        res = await api.authFetch(`/api/users`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ...formData, role })
        });
      }
      
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || "Failed to save record");
      
      fetchUsers();
      resetForm();
    } catch (err: any) {
      alert(err.message || "Failed to save record");
    }
  };

  const handleDelete = async (id: string) => {
    try {
      const res = await api.authFetch(`/api/users/${id}`, { method: 'DELETE' });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || "Failed to delete");
      
      fetchUsers();
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
          <h3 className="text-xl font-bold text-white">{title}</h3>
          <p className="text-sm text-slate-400">{description}</p>
        </div>
        <div className="flex gap-2">
          {!showAddForm && !editingUserId && (
            <button
              onClick={handleAddClick}
              className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors font-medium text-sm"
            >
              <Plus className="w-4 h-4" /> Add {role === 'student' ? 'Student' : role === 'staff' ? 'Staff' : 'Driver'}
            </button>
          )}
        </div>
      </div>

      {(showAddForm || editingUserId) ? (
        <form onSubmit={handleSave} className="bg-slate-800/80 p-5 rounded-xl border border-slate-700/50 mb-6">
          <h4 className="text-lg font-semibold text-white mb-4">
            {editingUserId ? `Edit ${role}` : `Add New ${role}`}
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Full Name</label>
              <input
                type="text"
                required
                value={formData.name || ''}
                onChange={e => setFormData({...formData, name: e.target.value})}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Email</label>
              <input
                type="email"
                required
                value={formData.email || ''}
                onChange={e => setFormData({...formData, email: e.target.value})}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
              />
            </div>
            
            {!editingUserId && (
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={formData.password || ''}
                  onChange={e => setFormData({...formData, password: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
                />
              </div>
            )}

            {role === 'student' && (
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Student ID</label>
                <input
                  type="text"
                  required
                  value={formData.studentId || ''}
                  onChange={e => setFormData({...formData, studentId: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
                />
              </div>
            )}

            {(role === 'staff' || role === 'driver') && (
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Staff ID</label>
                <input
                  type="text"
                  required
                  value={formData.staffId || ''}
                  onChange={e => setFormData({...formData, staffId: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
                />
              </div>
            )}

            {(role === 'staff') && (
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Department</label>
                <input
                  type="text"
                  value={formData.department || ''}
                  onChange={e => setFormData({...formData, department: e.target.value})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
                />
              </div>
            )}

            {role === 'driver' && (
              <>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Phone</label>
                  <input
                    type="tel"
                    value={formData.phone || ''}
                    onChange={e => setFormData({...formData, phone: e.target.value})}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Driver License</label>
                  <input
                    type="text"
                    value={formData.driverLicense || ''}
                    onChange={e => setFormData({...formData, driverLicense: e.target.value})}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
                  />
                </div>
              </>
            )}
            
            {editingUserId && (
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Status</label>
                <select
                  value={formData.status || 'active'}
                  onChange={e => setFormData({...formData, status: e.target.value as any})}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
                >
                  <option value="active">Active</option>
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
              className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg transition-colors text-sm font-medium"
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
              placeholder={`Search ${role}s...`}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-white focus:border-cyan-500 focus:outline-none text-sm"
            />
          </div>

          <div className="overflow-x-auto">
            {loading ? (
              <div className="py-8 text-center text-slate-500">Loading...</div>
            ) : (
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-700/50 text-slate-400 text-sm">
                    <th className="pb-3 font-medium">Name</th>
                    <th className="pb-3 font-medium">Email</th>
                    <th className="pb-3 font-medium">ID</th>
                    <th className="pb-3 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/50">
                  {filteredUsers.map(user => (
                    <tr key={user.id} className="text-sm">
                      <td className="py-3 text-white">{user.name}</td>
                      <td className="py-3 text-slate-300">{user.email}</td>
                      <td className="py-3 text-slate-300">{user.studentId || user.staffId || '-'}</td>
                      <td className="py-3 text-right">
                        <div className="flex justify-end gap-2">
                          <button
                            onClick={() => handleEditClick(user)}
                            className="p-1.5 text-slate-400 hover:text-cyan-400 bg-slate-800 hover:bg-slate-700 rounded transition-colors"
                            title="Edit"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => setDeleteConfirmId(user.id)}
                            className="p-1.5 text-slate-400 hover:text-rose-400 bg-slate-800 hover:bg-slate-700 rounded transition-colors"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {filteredUsers.length === 0 && (
                    <tr>
                      <td colSpan={4} className="py-8 text-center text-slate-500">
                        No {role}s found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirmId && (
        <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <h3 className="text-xl font-bold text-white mb-2">Delete {role.charAt(0).toUpperCase() + role.slice(1)}?</h3>
            <p className="text-slate-300 mb-6">
              You are about to remove this record. This action cannot be undone. Are you sure you want to proceed?
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
