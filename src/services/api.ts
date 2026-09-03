import {
  User,
  Bus,
  Driver,
  Route,
  Trip,
  StopETA,
  GPSUpdatePayload,
  NotificationItem,
  SystemLog,
  MLPredictionModelStats,
  PrivacyReport
} from '../types';

const API_BASE = '/api';

export const api = {
  getToken() {
    return localStorage.getItem('auth_token');
  },
  
  setToken(token: string) {
    localStorage.setItem('auth_token', token);
  },
  
  clearToken() {
    localStorage.removeItem('auth_token');
  },

  async authFetch(url: string, options: RequestInit = {}) {
    const token = this.getToken();
    const headers = new Headers(options.headers || {});
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
    const res = await fetch(url, { ...options, headers });
    if (res.status === 401) {
      this.clearToken();
      window.location.reload();
    }
    return res;
  },

  // Health
  async getHealth() {
    const res = await this.authFetch(`${API_BASE}/health`);
    return res.json();
  },

  // Auth & Persona
  async login(identifier: string, password: string = "password123"): Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ identifier, password })
    });
    if (!res.ok) throw new Error("Login failed");
    const data = await res.json();
    if (data.access_token) {
      this.setToken(data.access_token);
    }
    return data;
  },

  async getCurrentUser(): Promise<{ user: User; allAvailableUsers: User[] }> {
    const res = await this.authFetch(`${API_BASE}/auth/me`);
    if (!res.ok) throw new Error("Not authenticated");
    return res.json();
  },

  async switchRole(userId: string, role?: string): Promise<{ success: boolean; user: User }> {
    const res = await fetch(`${API_BASE}/auth/switch-role`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId, role })
    });
    const data = await res.json();
    if (data.access_token) {
      this.setToken(data.access_token);
    }
    return data;
  },

  // Full State & Bootstrap
  async getState() {
    try {
      const [auth, buses, drivers, routes, activeTrips, notifications, logs] = await Promise.all([
        this.getCurrentUser().catch(() => ({ user: null as any, allAvailableUsers: [] })),
        this.getBuses().catch(() => ({ buses: [] })),
        this.getDrivers().catch(() => ({ drivers: [] })),
        this.getRoutes().catch(() => ({ routes: [] })),
        this.getActiveTrips().catch(() => ({ activeTrips: [] })),
        this.getNotifications().catch(() => ({ notifications: [] })),
        this.getLogs().catch(() => ({ logs: [] }))
      ]);

      return {
        currentUser: auth.user,
        users: auth.allAvailableUsers || [],
        buses: buses.buses || [],
        drivers: drivers.drivers || [],
        routes: routes.routes || [],
        activeTrips: activeTrips.activeTrips || [],
        notifications: notifications.notifications || [],
        logs: logs.logs || []
      };
    } catch (err) {
      console.error('Failed to get full state:', err);
      return null;
    }
  },

  async switchUser(userId: string) {
    return this.switchRole(userId);
  },

  // Buses
  async getBuses(): Promise<{ buses: Bus[] }> {
    const res = await this.authFetch(`${API_BASE}/buses`);
    return res.json();
  },

  async createBus(busData: Partial<Bus>): Promise<{ success: boolean; bus: Bus }> {
    const res = await this.authFetch(`${API_BASE}/buses`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(busData)
    });
    return res.json();
  },

  async updateBus(id: string, busData: Partial<Bus>): Promise<{ success: boolean; bus: Bus }> {
    const res = await this.authFetch(`${API_BASE}/buses/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(busData)
    });
    return res.json();
  },

  async deleteBus(id: string): Promise<{ success: boolean; removedBus: Bus }> {
    const res = await this.authFetch(`${API_BASE}/buses/${id}`, {
      method: 'DELETE'
    });
    return res.json();
  },

  // Drivers
  async getDrivers(): Promise<{ drivers: Driver[] }> {
    const res = await this.authFetch(`${API_BASE}/drivers`);
    return res.json();
  },

  async updateDriver(id: string, driverData: Partial<Driver>): Promise<{ success: boolean; driver: Driver }> {
    const res = await this.authFetch(`${API_BASE}/drivers/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(driverData)
    });
    return res.json();
  },

  // Routes
  async getRoutes(): Promise<{ routes: Route[] }> {
    const res = await this.authFetch(`${API_BASE}/routes`);
    return res.json();
  },

  async createRoute(routeData: Partial<Route>): Promise<{ success: boolean; route: Route }> {
    const res = await this.authFetch(`${API_BASE}/routes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(routeData)
    });
    return res.json();
  },

  // Trips & Live GPS
  async getTrips(): Promise<{ trips: Trip[] }> {
    const res = await this.authFetch(`${API_BASE}/trips`);
    return res.json();
  },

  async getActiveTrips(): Promise<{ activeTrips: Trip[] }> {
    const res = await this.authFetch(`${API_BASE}/trips/active`);
    return res.json();
  },

  async startTrip(driverId: string, busId: string, routeId: string): Promise<{ success: boolean; trip: Trip }> {
    const res = await this.authFetch(`${API_BASE}/trips/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ driverId, busId, routeId })
    });
    return res.json();
  },

  async updateGPS(payload: GPSUpdatePayload & { passengerCount?: number; trafficLevel?: string; delayMinutes?: number; delayReason?: string }): Promise<any> {
    const res = await this.authFetch(`${API_BASE}/trips/update-gps`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return res.json();
  },

  async stopTrip(tripId: string, driverId: string): Promise<{ success: boolean; message: string; trip: Trip }> {
    const res = await this.authFetch(`${API_BASE}/trips/stop`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tripId, driverId })
    });
    return res.json();
  },

  async getTripETA(tripId: string, weather: string = 'clear'): Promise<{
    tripId: string;
    busNumber: string;
    routeId: string;
    routeName: string;
    tripStatus: string;
    currentSpeedKmH: number;
    trafficLevel: string;
    delayMinutes: number;
    lastUpdate: string;
    stopEtas: StopETA[];
  }> {
    const res = await this.authFetch(`${API_BASE}/trips/${tripId}/eta?weather=${weather}`);
    return res.json();
  },

  // Notifications
  async getNotifications(): Promise<{ notifications: NotificationItem[] }> {
    const res = await this.authFetch(`${API_BASE}/notifications`);
    return res.json();
  },

  async broadcastNotification(data: Partial<NotificationItem>): Promise<{ success: boolean; notification: NotificationItem }> {
    const res = await this.authFetch(`${API_BASE}/notifications`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  async markNotificationRead(id: string): Promise<{ success: boolean }> {
    const res = await this.authFetch(`${API_BASE}/notifications/${id}/read`, {
      method: 'PUT'
    });
    return res.json();
  },

  // Logs & Privacy
  async getLogs(): Promise<{ logs: SystemLog[] }> {
    const res = await this.authFetch(`${API_BASE}/logs`);
    return res.json();
  },

  async getPrivacyReport(): Promise<PrivacyReport> {
    const res = await this.authFetch(`${API_BASE}/privacy/report`);
    return res.json();
  },

  // ML & AI
  async getMLStats(): Promise<{ stats: MLPredictionModelStats }> {
    const res = await this.authFetch(`${API_BASE}/ml/stats`);
    return res.json();
  },

  async getMLEvaluationReport(): Promise<{ success: boolean; report: any }> {
    const res = await this.authFetch(`${API_BASE}/ml/evaluation`);
    return res.json();
  },

  async retrainMLModel(): Promise<{ success: boolean; selectedModel: string; evaluations: any[]; split: any }> {
    const res = await this.authFetch(`${API_BASE}/ml/train`, {
      method: 'POST'
    });
    return res.json();
  },

  async getAIInsights(tripId: string): Promise<{
    success: boolean;
    insights: {
      summary: string;
      delayAnalysis: string;
      recommendation: string;
      anomalyDetected: boolean;
    };
  }> {
    const res = await this.authFetch(`${API_BASE}/ai/insights`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tripId })
    });
    return res.json();
  },

  async askAIAssistant(query: string, role: string): Promise<{ success: boolean; reply: string }> {
    const res = await this.authFetch(`${API_BASE}/ai/assistant`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, role })
    });
    return res.json();
  },

  async optimizeRoute(routeId: string): Promise<{
    success: boolean;
    optimization: {
      analysis: string;
      recommendedHeadwayMinutes: number;
      congestionHotspots: string[];
      energyEfficiencyScore: number;
    };
  }> {
    const res = await this.authFetch(`${API_BASE}/ai/optimize-route`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ routeId })
    });
    return res.json();
  },

  // Automated Test Suite
  async runPrivacyTests(): Promise<any> {
    const res = await this.authFetch(`${API_BASE}/tests/run-privacy-test`, {
      method: 'POST'
    });
    return res.json();
  }
,
  // Image Generation
  async generateImage(prompt: string): Promise<{ success: boolean; image?: string; error?: string }> {
    const res = await this.authFetch(`${API_BASE}/ai/image`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt })
    });
    return res.json();
  }
};
