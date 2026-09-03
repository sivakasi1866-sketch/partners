import os

app_tsx = """import React, { useState, useEffect } from 'react';
import { Login } from './components/Login';
import { AdminDashboard } from './components/admin/AdminDashboard';
import { DriverDashboard } from './components/driver/DriverDashboard';
import { StudentDashboard } from './components/student/StudentDashboard';
import { StaffDashboard } from './components/staff/StaffDashboard';
import { User, Trip, Route as RouteType, Bus, Driver, SystemNotification } from './types';
import { api } from './services/api';
import { Bus as BusIcon, LogOut, Bell, ShieldCheck, MapPin } from 'lucide-react';

export default function App() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [buses, setBuses] = useState<Bus[]>([]);
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [routes, setRoutes] = useState<RouteType[]>([]);
  const [activeTrips, setActiveTrips] = useState<Trip[]>([]);
  const [notifications, setNotifications] = useState<SystemNotification[]>([]);
  const [isPrivacyModalOpen, setIsPrivacyModalOpen] = useState(false);

  useEffect(() => {
    const initAuth = async () => {
      try {
        if (!api.getToken()) return;
        const res = await api.getCurrentUser();
        if (res && res.user) {
          setCurrentUser(res.user);
          setIsAuthenticated(true);
        }
      } catch (e: any) {
        if (e.message !== "Not authenticated") {
          console.error("Auth check failed:", e);
        }
      }
    };
    initAuth();
  }, []);

  useEffect(() => {
    if (!isAuthenticated) return;
    fetchFullState();
    const interval = setInterval(fetchFullState, 15000);
    return () => clearInterval(interval);
  }, [isAuthenticated]);

  const fetchFullState = async () => {
    try {
      const [bRes, dRes, rRes, tRes, nRes] = await Promise.all([
        api.getBuses(),
        api.getDrivers(),
        api.getRoutes(),
        api.getActiveTrips(),
        api.getNotifications()
      ]);
      if (bRes.buses) setBuses(bRes.buses);
      if (dRes.drivers) setDrivers(dRes.drivers);
      if (rRes.routes) setRoutes(rRes.routes);
      if (tRes.activeTrips) setActiveTrips(tRes.activeTrips);
      if (nRes.notifications) setNotifications(nRes.notifications);
    } catch (e) {
      console.error(e);
    }
  };

  const handleLogin = (user: User) => {
    setCurrentUser(user);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentUser(null);
  };

  if (!isAuthenticated || !currentUser) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-[#030712] text-slate-200 font-sans flex flex-col selection:bg-cyan-500/30 selection:text-cyan-100">
      
      {/* Premium Dark Header */}
      <header className="glass-panel sticky top-0 z-50 border-b-0 border-slate-800 shadow-cyan-900/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 p-[1px] shadow-lg shadow-cyan-500/20">
              <div className="w-full h-full bg-slate-900 rounded-xl flex items-center justify-center">
                <BusIcon className="w-5 h-5 text-cyan-400" />
              </div>
            </div>
            <div>
              <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400 tracking-tight leading-none">
                Partners Bus Prediction
              </h1>
              <p className="text-[10px] text-cyan-200/60 font-semibold uppercase tracking-widest hidden sm:block mt-0.5">
                Smart Campus Transportation
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsPrivacyModalOpen(true)}
              className="hidden sm:flex px-3 py-1.5 bg-slate-800/50 hover:bg-slate-700/50 text-cyan-200/80 rounded-lg text-xs font-semibold items-center gap-1.5 border border-slate-700/50 transition-colors"
            >
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Privacy Guaranteed</span>
            </button>
            <div className="flex items-center gap-3 border-l border-slate-700 pl-4 ml-2">
              <div className="text-right hidden sm:block">
                <div className="text-sm font-bold text-slate-200">{currentUser.name}</div>
                <div className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider">{currentUser.role}</div>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 text-slate-400 hover:text-cyan-400 bg-slate-800/30 hover:bg-slate-800 rounded-lg transition-colors border border-transparent hover:border-slate-700"
                title="Sign out"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Dashboard Container */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {currentUser.role === 'admin' && (
          <AdminDashboard
            currentUser={currentUser}
            buses={buses}
            drivers={drivers}
            routes={routes}
            activeTrips={activeTrips}
            onRefreshData={fetchFullState}
          />
        )}
        {currentUser.role === 'driver' && (
          <DriverDashboard
            currentUser={currentUser}
            buses={buses}
            routes={routes}
            activeTrips={activeTrips}
            onRefreshData={fetchFullState}
          />
        )}
        {currentUser.role === 'student' && (
          <StudentDashboard
            currentUser={currentUser}
            routes={routes}
            activeTrips={activeTrips}
            onRefreshData={fetchFullState}
          />
        )}
        {currentUser.role === 'staff' && (
          <StaffDashboard
            currentUser={currentUser}
            routes={routes}
            activeTrips={activeTrips}
            onRefreshData={fetchFullState}
          />
        )}
      </main>

      {isPrivacyModalOpen && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="card-3d max-w-md w-full p-6 text-slate-200">
            <h3 className="text-xl font-bold text-white flex items-center gap-2 mb-4">
              <ShieldCheck className="w-6 h-6 text-emerald-400" />
              GPS Privacy Policy
            </h3>
            <div className="space-y-4 text-sm text-slate-300">
              <p><strong className="text-emerald-400">Student & Staff Privacy:</strong> We NEVER collect or track your location. Your privacy is absolutely guaranteed.</p>
              <p><strong className="text-cyan-400">Driver Privacy:</strong> GPS location is ONLY collected during an active trip. When a trip is stopped, all tracking immediately ceases. No background tracking is performed.</p>
            </div>
            <button onClick={() => setIsPrivacyModalOpen(false)} className="w-full mt-6 btn-primary">
              Understood
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
"""
with open("src/App.tsx", "w") as f:
    f.write(app_tsx)
print("App.tsx updated")
