import React, { useState } from 'react';
import { User, Bus, Driver, Route, Trip } from '../../types';
import { Bus as BusIcon, Route as RouteIcon, Users, Activity, Navigation, Settings, LayoutDashboard, BrainCircuit } from 'lucide-react';
import { LiveBusMap } from '../map/LiveBusMap';
import { UserManagement } from './UserManagement';
import { BusManagement } from './BusManagement';
import { RouteManagement } from './RouteManagement';
import { AssignmentManagement } from './AssignmentManagement';
import { DataImport } from './DataImport';
import { Database } from 'lucide-react';

interface AdminDashboardProps {
  currentUser: User;
  buses: Bus[];
  drivers: Driver[];
  routes: Route[];
  activeTrips: Trip[];
  onRefreshData: () => void;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({
  currentUser,
  buses,
  drivers,
  routes,
  activeTrips,
  onRefreshData
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'students' | 'staff' | 'drivers' | 'buses' | 'routes' | 'assignments' | 'map' | 'prediction' | 'import'>('overview');

  const delayedTrips = activeTrips.filter(t => t.delayMinutes > 2);

  return (
    <div className="space-y-6">
      
      {/* 3D Hero Dashboard Header */}
      <div className="relative overflow-hidden card-3d border-0 bg-gradient-to-br from-slate-900 to-indigo-950 p-8">
        <div className="absolute top-0 right-0 p-12 opacity-10 pointer-events-none transform translate-x-10 -translate-y-10">
          <BrainCircuit className="w-64 h-64 text-cyan-400" />
        </div>
        <div className="relative z-10">
          <h2 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400 mb-2">
            Command Center
          </h2>
          <p className="text-cyan-200/80 max-w-xl">
            Welcome, {currentUser.name}. Monitor live campus transportation, review AI travel time predictions, and manage fleet operations from this unified terminal.
          </p>
        </div>
      </div>

      {/* Navigation Tabs */}
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
          onClick={() => setActiveTab('map')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
            activeTab === 'overview' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shadow-inner' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          }`}
        >
          <LayoutDashboard className="w-4 h-4" /> Overview
        </button>
        <button
          onClick={() => setActiveTab('map')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
            activeTab === 'map' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shadow-inner' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          }`}
        >
          <Navigation className="w-4 h-4" /> Live Map
        </button>
        <button
          onClick={() => setActiveTab('prediction')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
            activeTab === 'prediction' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shadow-inner' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          }`}
        >
          <BrainCircuit className="w-4 h-4" /> AI Prediction Details
        </button>
      </div>

      {/* Tab Content */}

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

      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="card-3d p-5">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-cyan-500/10 rounded-lg">
                  <Activity className="w-5 h-5 text-cyan-400" />
                </div>
                <h3 className="font-semibold text-slate-300">Active Trips</h3>
              </div>
              <div className="text-3xl font-bold text-white">{activeTrips.length}</div>
              <div className="text-xs text-slate-400 mt-1">Live right now</div>
            </div>
            <div className="card-3d p-5">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-emerald-500/10 rounded-lg">
                  <BusIcon className="w-5 h-5 text-emerald-400" />
                </div>
                <h3 className="font-semibold text-slate-300">Total Fleet</h3>
              </div>
              <div className="text-3xl font-bold text-white">{buses.length}</div>
              <div className="text-xs text-slate-400 mt-1">Registered vehicles</div>
            </div>
            <div className="card-3d p-5">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-rose-500/10 rounded-lg">
                  <Navigation className="w-5 h-5 text-rose-400" />
                </div>
                <h3 className="font-semibold text-slate-300">Delayed</h3>
              </div>
              <div className="text-3xl font-bold text-white">{delayedTrips.length}</div>
              <div className="text-xs text-slate-400 mt-1">Trips &gt;2 min late</div>
            </div>
            <div className="card-3d p-5">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-blue-500/10 rounded-lg">
                  <RouteIcon className="w-5 h-5 text-blue-400" />
                </div>
                <h3 className="font-semibold text-slate-300">Routes</h3>
              </div>
              <div className="text-3xl font-bold text-white">{routes.length}</div>
              <div className="text-xs text-slate-400 mt-1">Active pathways</div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'map' && (
        <div className="card-3d overflow-hidden border border-slate-700/50">
          <div className="p-4 border-b border-slate-700/50 bg-slate-800/80 flex items-center justify-between">
            <h3 className="font-bold text-white flex items-center gap-2">
              <Navigation className="w-5 h-5 text-cyan-400" /> Live Fleet Tracking
            </h3>
            <span className="px-2.5 py-1 bg-emerald-500/10 text-emerald-400 text-[10px] font-bold uppercase tracking-wider rounded border border-emerald-500/20 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-ping"></span> Live
            </span>
          </div>
          <LiveBusMap routes={routes} activeTrips={activeTrips} heightClass="h-[600px]" />
        </div>
      )}

      {activeTab === 'prediction' && (
        <div className="card-3d p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-indigo-500/20 rounded-xl">
              <BrainCircuit className="w-6 h-6 text-indigo-400" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">Advanced Prediction Model</h3>
              <p className="text-sm text-slate-400">How the system estimates arrival times</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8 text-center items-center">
            <div className="p-4 bg-slate-800/80 rounded-xl border border-slate-700/50">
              <p className="text-xs font-bold text-cyan-400 mb-1">Step 1</p>
              <p className="text-sm text-slate-200">Live GPS Location</p>
            </div>
            <div className="hidden md:block text-slate-600">→</div>
            <div className="p-4 bg-slate-800/80 rounded-xl border border-slate-700/50">
              <p className="text-xs font-bold text-cyan-400 mb-1">Step 2</p>
              <p className="text-sm text-slate-200">Distance & Traffic</p>
            </div>
            <div className="hidden md:block text-slate-600">→</div>
            <div className="p-4 bg-slate-800/80 rounded-xl border border-slate-700/50">
              <p className="text-xs font-bold text-cyan-400 mb-1">Step 3</p>
              <p className="text-sm text-slate-200">AI Prediction</p>
            </div>
          </div>

          <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-700/50">
            <details className="group cursor-pointer">
              <summary className="font-semibold text-slate-300 list-none flex items-center justify-between">
                <span>View Technical Details</span>
                <span className="text-slate-500 group-open:rotate-180 transition-transform">▼</span>
              </summary>
              <div className="mt-4 pt-4 border-t border-slate-700/50 text-sm text-slate-400 space-y-2">
                <p><strong className="text-slate-200">Model Type:</strong> Advanced Travel-Time Prediction Model</p>
                <p><strong className="text-slate-200">Data Preparation:</strong> Normalizes distances, encodes time of day, and processes weather data.</p>
                <p><strong className="text-slate-200">Average Prediction Error:</strong> ~2.1 minutes</p>
                <p><strong className="text-slate-200">Prediction Fit:</strong> 94%</p>
                <p className="text-xs text-rose-400/80 italic mt-4">* Note: Current metrics represent performance on synthetic/development data.</p>
              </div>
            </details>
          </div>
        </div>
      )}

    </div>
  );
};
