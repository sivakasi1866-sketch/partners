import re

with open("src/components/admin/AdminDashboard.tsx", "r") as f:
    content = f.read()

# Add imports
imports = """import { UserManagement } from './UserManagement';
import { BusManagement } from './BusManagement';
import { RouteManagement } from './RouteManagement';
import { AssignmentManagement } from './AssignmentManagement';
import { DataImport } from './DataImport';
import { Database } from 'lucide-react';"""

content = content.replace("import { LiveBusMap } from '../map/LiveBusMap';", "import { LiveBusMap } from '../map/LiveBusMap';\n" + imports)

# Update the activeTab state to allow more types
state_search = "const [activeTab, setActiveTab] = useState<'overview' | 'map' | 'prediction'>('overview');"
state_replace = "const [activeTab, setActiveTab] = useState<'overview' | 'students' | 'staff' | 'drivers' | 'buses' | 'routes' | 'assignments' | 'map' | 'prediction' | 'import'>('overview');"
content = content.replace(state_search, state_replace)

# Modify the navigation tabs to render the new tabs
tabs_search = """      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 bg-slate-900/50 p-1.5 rounded-xl border border-slate-700/50 backdrop-blur-sm overflow-x-auto">
        <button
          onClick={() => setActiveTab('overview')}"""
          
tabs_replace = """      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 bg-slate-900/50 p-1.5 rounded-xl border border-slate-700/50 backdrop-blur-sm overflow-x-auto flex-wrap">
        <button
          onClick={() => setActiveTab('overview')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
            activeTab === 'overview' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shadow-inner' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          }`}
        >
          <LayoutDashboard className="w-4 h-4" /> Overview
        </button>
        <button
          onClick={() => setActiveTab('students')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
            activeTab === 'students' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shadow-inner' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          }`}
        >
          <Users className="w-4 h-4" /> Students
        </button>
        <button
          onClick={() => setActiveTab('staff')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
            activeTab === 'staff' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shadow-inner' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          }`}
        >
          <Users className="w-4 h-4" /> Staff
        </button>
        <button
          onClick={() => setActiveTab('drivers')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
            activeTab === 'drivers' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shadow-inner' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          }`}
        >
          <Users className="w-4 h-4" /> Drivers
        </button>
        <button
          onClick={() => setActiveTab('buses')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
            activeTab === 'buses' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shadow-inner' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          }`}
        >
          <BusIcon className="w-4 h-4" /> Buses
        </button>
        <button
          onClick={() => setActiveTab('routes')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
            activeTab === 'routes' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shadow-inner' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          }`}
        >
          <RouteIcon className="w-4 h-4" /> Routes
        </button>
        <button
          onClick={() => setActiveTab('assignments')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
            activeTab === 'assignments' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shadow-inner' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          }`}
        >
          <Settings className="w-4 h-4" /> Assignments
        </button>
        <button
          onClick={() => setActiveTab('import')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
            activeTab === 'import' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shadow-inner' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          }`}
        >
          <Database className="w-4 h-4" /> Bulk Import
        </button>
        <button
          onClick={() => setActiveTab('map')}"""

content = content.replace(tabs_search, tabs_replace)

# Add the content views
content_addition = """
      {activeTab === 'students' && (
        <UserManagement role="student" title="Manage Students" description="Add, edit, or remove student accounts." />
      )}
      {activeTab === 'staff' && (
        <UserManagement role="staff" title="Manage Staff" description="Add, edit, or remove staff members." />
      )}
      {activeTab === 'drivers' && (
        <UserManagement role="driver" title="Manage Drivers" description="Add, edit, or remove bus drivers." />
      )}
      {activeTab === 'buses' && (
        <BusManagement buses={buses} onRefresh={onRefreshData} />
      )}
      {activeTab === 'routes' && (
        <RouteManagement routes={routes} fetchRoutes={onRefreshData} />
      )}
      {activeTab === 'assignments' && (
        <AssignmentManagement drivers={drivers} buses={buses} routes={routes} fetchAssignments={onRefreshData} />
      )}
      {activeTab === 'import' && (
        <DataImport onImportSuccess={onRefreshData} />
      )}
"""

# Insert right after `      {/* Tab Content */}`
content = content.replace("{/* Tab Content */}", "{/* Tab Content */}\n" + content_addition)

with open("src/components/admin/AdminDashboard.tsx", "w") as f:
    f.write(content)

