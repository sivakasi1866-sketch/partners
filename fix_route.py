import re

with open("src/components/admin/RouteManagement.tsx", "r") as f:
    content = f.read()

# Replace window.confirm with state-based modals
state_addition = """  const [showAddRoute, setShowAddRoute] = useState(false);
  const [deleteRouteConfirmId, setDeleteRouteConfirmId] = useState<string | null>(null);
  const [deleteStopConfirm, setDeleteStopConfirm] = useState<{routeId: string, stopId: string} | null>(null);"""
content = content.replace("  const [showAddRoute, setShowAddRoute] = useState(false);", state_addition)

# Replace handleDeleteRoute
old_handleDeleteRoute = """  const handleDeleteRoute = async (id: string) => {
    if (!window.confirm("Delete this route?")) return;
    try {
      await api.authFetch(`/api/routes/${id}`, { method: 'DELETE' });
      fetchRoutes();
    } catch (err: any) {
      alert("Failed to delete route");
    }
  };"""
new_handleDeleteRoute = """  const handleDeleteRoute = async (id: string) => {
    try {
      await api.authFetch(`/api/routes/${id}`, { method: 'DELETE' });
      fetchRoutes();
      setDeleteRouteConfirmId(null);
    } catch (err: any) {
      alert("Failed to delete route");
    }
  };"""
content = content.replace(old_handleDeleteRoute, new_handleDeleteRoute)

# Update onClick to trigger modal
content = content.replace("onClick={() => handleDeleteRoute(route.id)}", "onClick={() => setDeleteRouteConfirmId(route.id)}")

# Same for stop
old_handleDeleteStop = """  const handleDeleteStop = async (routeId: string, stopId: string) => {
    if (!window.confirm("Delete this stop?")) return;
    try {
      await api.authFetch(`/api/routes/${routeId}/stops/${stopId}`, { method: 'DELETE' });
      fetchRoutes();
    } catch (err: any) {
      alert("Failed to delete stop");
    }
  };"""
new_handleDeleteStop = """  const handleDeleteStop = async (routeId: string, stopId: string) => {
    try {
      await api.authFetch(`/api/routes/${routeId}/stops/${stopId}`, { method: 'DELETE' });
      fetchRoutes();
      setDeleteStopConfirm(null);
    } catch (err: any) {
      alert("Failed to delete stop");
    }
  };"""
content = content.replace(old_handleDeleteStop, new_handleDeleteStop)
content = content.replace("onClick={() => handleDeleteStop(route.id, stop.id!)}", "onClick={() => setDeleteStopConfirm({routeId: route.id, stopId: stop.id!})}")

# Add modals at the bottom before last closing div
modals = """      {deleteRouteConfirmId && (
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
"""
content = content.replace("    </div>\n  );\n};", modals + "    </div>\n  );\n};")

with open("src/components/admin/RouteManagement.tsx", "w") as f:
    f.write(content)
