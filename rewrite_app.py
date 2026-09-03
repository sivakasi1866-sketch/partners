import os

with open('src/App.tsx', 'r') as f:
    app_tsx = f.read()

# We need to inject isAuthenticated state and the Login component.
# Let's replace the whole App component.

new_app = """import React, { useState, useEffect } from 'react';
import {
  User,
  Bus,
  Driver,
  Route,
  Trip,
  Notification
} from './types';
import { api } from './services/api';
import { AdminDashboard } from './components/admin/AdminDashboard';
import { DriverDashboard } from './components/driver/DriverDashboard';
import { StudentDashboard } from './components/student/StudentDashboard';
import { StaffDashboard } from './components/staff/StaffDashboard';
import { PrivacyModal } from './components/modals/PrivacyModal';
import { AIAssistantModal } from './components/modals/AIAssistantModal';
import { TestRunnerModal } from './components/modals/TestRunnerModal';
import { NotificationsModal } from './components/modals/NotificationsModal';
import { Login } from './components/Login';
import {
  Bus as BusIcon,
  ShieldCheck,
  Bell,
  LogOut,
  HelpCircle
} from 'lucide-react';

const DEFAULT_INITIAL_USER: User = {
  id: 'usr-student-1',
  name: 'Sophia Patel',
  email: 'sophia.patel@student.elite.edu',
  role: 'student',
  studentId: 'ST-2024-8841',
  department: 'Computer Science & AI',
  favoriteStopIds: ['stop-1-3', 'stop-1-5']
};

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState<User>(DEFAULT_INITIAL_USER);
  const [users, setUsers] = useState<User[]>([DEFAULT_INITIAL_USER]);

  const [buses, setBuses] = useState<Bus[]>([]);
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [routes, setRoutes] = useState<Route[]>([]);
  const [activeTrips, setActiveTrips] = useState<Trip[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const [isPrivacyModalOpen, setIsPrivacyModalOpen] = useState(false);
  const [isAIAssistantOpen, setIsAIAssistantOpen] = useState(false);
  const [isTestRunnerOpen, setIsTestRunnerOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);

  useEffect(() => {
    fetchUsers();
    fetchFullState();
    const interval = setInterval(fetchFullState, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchUsers = async () => {
    try {
      const res = await api.getUsers();
      if (res.success && res.users) {
        setUsers(res.users);
        if (!isAuthenticated) {
            const student = res.users.find(u => u.role === 'student');
            if (student) setCurrentUser(student);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchFullState = async () => {
    try {
      const [bRes, dRes, rRes, tRes, nRes] = await Promise.all([
        api.getBuses(),
        api.getDrivers(),
        api.getRoutes(),
        api.getActiveTrips(),
        api.getNotifications()
      ]);
      if (bRes.success) setBuses(bRes.buses || []);
      if (dRes.success) setDrivers(dRes.drivers || []);
      if (rRes.success) setRoutes(rRes.routes || []);
      if (tRes.success) setActiveTrips(tRes.trips || []);
      if (nRes.success) setNotifications(nRes.notifications || []);
    } catch (e) {
      console.error(e);
    }
  };

  const unreadNotifications = notifications.filter(n => !n.read).length;

  const handleLogin = (user: User) => {
    setCurrentUser(user);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} availableUsers={users} />;
  }

  return (
    <div className="min-h-screen bg-gray-50 text-slate-900 font-sans flex flex-col selection:bg-blue-600 selection:text-white">
      {/* Top Application Header - Clean Institutional Shell */}
      <header className="bg-white border-b border-gray-200 px-4 sm:px-6 py-3 shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm">
              <BusIcon className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-900 tracking-tight leading-tight">Partners Bus Prediction</h1>
              <p className="text-[11px] text-slate-500 font-medium uppercase tracking-wider hidden sm:block">
                Campus Transportation System
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-4">
            <button
              onClick={() => setIsPrivacyModalOpen(true)}
              className="hidden sm:flex px-3 py-1.5 bg-gray-50 hover:bg-gray-100 text-slate-600 rounded-md text-xs font-semibold items-center gap-1.5 border border-gray-200 transition-colors"
              title="View Institutional Privacy Policy"
            >
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Zero Tracking Policy</span>
            </button>

            <button
              onClick={() => setIsAIAssistantOpen(true)}
              className="hidden sm:flex px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-md text-xs font-semibold items-center gap-1.5 border border-blue-200 transition-colors"
            >
              <HelpCircle className="w-4 h-4" />
              <span>Help & Support</span>
            </button>

            <button
              onClick={() => setIsNotificationsOpen(true)}
              className="relative p-2 text-slate-500 hover:text-slate-900 hover:bg-gray-100 rounded-md transition-colors"
              title="Notifications"
            >
              <Bell className="w-5 h-5" />
              {unreadNotifications > 0 && (
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full ring-2 ring-white"></span>
              )}
            </button>

            <div className="h-6 w-px bg-gray-300 hidden sm:block"></div>

            <div className="flex items-center gap-3">
              <div className="text-right hidden sm:block">
                <div className="text-sm font-bold text-slate-900">{currentUser.name}</div>
                <div className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">{currentUser.role}</div>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-md transition-colors"
                title="Sign out"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Dashboard Container */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {currentUser.role === 'admin' && (
          <AdminDashboard
            currentUser={currentUser}
            buses={buses}
            drivers={drivers}
            routes={routes}
            activeTrips={activeTrips}
            onRefreshData={fetchFullState}
            onOpenTestRunner={() => setIsTestRunnerOpen(true)}
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
            onOpenAIAssistant={() => setIsAIAssistantOpen(true)}
            onRefreshData={fetchFullState}
          />
        )}
        {currentUser.role === 'staff' && (
          <StaffDashboard
            currentUser={currentUser}
            routes={routes}
            activeTrips={activeTrips}
            onOpenAIAssistant={() => setIsAIAssistantOpen(true)}
            onRefreshData={fetchFullState}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-6 px-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-700">Partners Bus Prediction</span>
            <span className="hidden sm:inline">•</span>
            <span className="hidden sm:inline">Campus Transportation System</span>
          </div>
          <div className="flex items-center gap-4">
            <button onClick={() => setIsPrivacyModalOpen(true)} className="hover:text-slate-900 transition-colors">
              Privacy Policy
            </button>
            <span>•</span>
            <button onClick={() => setIsTestRunnerOpen(true)} className="hover:text-slate-900 transition-colors">
              System Diagnostics
            </button>
          </div>
        </div>
      </footer>

      <PrivacyModal isOpen={isPrivacyModalOpen} onClose={() => setIsPrivacyModalOpen(false)} />
      <AIAssistantModal isOpen={isAIAssistantOpen} onClose={() => setIsAIAssistantOpen(false)} currentUser={currentUser} />
      <TestRunnerModal isOpen={isTestRunnerOpen} onClose={() => setIsTestRunnerOpen(false)} />
      <NotificationsModal
        isOpen={isNotificationsOpen}
        onClose={() => setIsNotificationsOpen(false)}
        notifications={notifications}
        onMarkAllAsRead={() => setNotifications(prev => prev.map(n => ({ ...n, read: true })))}
      />
    </div>
  );
}
"""

with open('src/App.tsx', 'w') as f:
    f.write(new_app)
