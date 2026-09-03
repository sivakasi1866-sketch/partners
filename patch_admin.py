with open("src/components/admin/AdminDashboard.tsx", "r") as f:
    code = f.read()

code = code.replace(
    "import { RouteManagement } from './RouteManagement';",
    "import { RouteManagement } from './RouteManagement';\nimport { AssignmentManagement } from './AssignmentManagement';"
)

code = code.replace(
    "<button\n            id=\"admin-tab-drivers\"\n            onClick={() => setActiveTab('drivers')}",
    """<button
            id="admin-tab-assignments"
            onClick={() => setActiveTab('assignments')}
            className={`px-3.5 py-2 rounded-xl font-bold transition-all ${
              activeTab === 'assignments'
                ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/50'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white'
            }`}
          >
            Assignments
          </button>
          <button
            id="admin-tab-drivers"
            onClick={() => setActiveTab('drivers')}"""
)

code = code.replace(
    "{/* TAB 4: ROUTES & STOPS */}",
    """{/* TAB 3.5: ASSIGNMENTS */}
      {activeTab === 'assignments' && (
        <AssignmentManagement drivers={drivers} buses={buses} routes={routes} fetchAssignments={onRefreshData} />
      )}
      
      {/* TAB 4: ROUTES & STOPS */}"""
)

with open("src/components/admin/AdminDashboard.tsx", "w") as f:
    f.write(code)
