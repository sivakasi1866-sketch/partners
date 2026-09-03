import re

with open("src/components/admin/AssignmentManagement.tsx", "r") as f:
    content = f.read()

# Replace confirm with state-based modals
state_addition = """  const [selectedRoute, setSelectedRoute] = useState('');
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);"""
content = content.replace("  const [selectedRoute, setSelectedRoute] = useState('');", state_addition)

old_handleRemove = """  const handleRemove = async (driverId: string) => {
    if (!confirm('Are you sure you want to remove this assignment?')) return;
    try {
      setError('');
      const res = await api.authFetch(`/api/assignments/${driverId}`, { method: 'DELETE' });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || 'Failed to remove assignment');
      loadAssignments();
      if (fetchAssignments) fetchAssignments();
    } catch (err: any) {
      setError(err.message || 'Failed to remove assignment');
    }
  };"""
new_handleRemove = """  const handleRemove = async (driverId: string) => {
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
  };"""
content = content.replace(old_handleRemove, new_handleRemove)

content = content.replace("onClick={() => handleRemove(a.driverId)}", "onClick={() => setDeleteConfirmId(a.driverId)}")

# Add modal at the bottom
modal = """
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
"""
content = content.replace("    </div>\n  );\n};", modal + "    </div>\n  );\n};")

# Fix UI color mismatch (it was white/gray instead of slate) in AssignmentManagement
# Actually, I'll just change the main class
content = content.replace("bg-white border border-gray-200 rounded-lg p-5 shadow-sm", "card-3d p-6")
content = content.replace("font-bold text-slate-900", "text-xl font-bold text-white")
content = content.replace("bg-gray-50 p-4 rounded-xl border border-gray-200", "bg-slate-800/80 p-5 rounded-xl border border-slate-700/50")
content = content.replace("text-gray-700", "text-slate-400")
content = content.replace("bg-white border border-gray-300", "bg-slate-900 border border-slate-700 text-white")
content = content.replace("text-slate-500", "text-slate-400")
content = content.replace("border-b border-gray-200", "border-b border-slate-700/50")
content = content.replace("text-gray-900", "text-white")
content = content.replace("text-gray-600", "text-slate-300")
content = content.replace("bg-gray-50", "bg-slate-800/50")

with open("src/components/admin/AssignmentManagement.tsx", "w") as f:
    f.write(content)
