import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses (token expired)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ── Auth API ────────────────────────────────────────────
export const authAPI = {
  signup: (data) => api.post('/api/auth/signup', data),
  login: (data) => api.post('/api/auth/login', data),
  getProfile: () => api.get('/api/auth/me'),
  updateProfile: (data) => api.put('/api/auth/me', data),
};

// ── Resources API ───────────────────────────────────────
export const resourcesAPI = {
  list: (params) => api.get('/api/resources/', { params }),
  get: (id) => api.get(`/api/resources/${id}`),
  create: (data) => api.post('/api/resources/', data),
  update: (id, data) => api.put(`/api/resources/${id}`, data),
  delete: (id) => api.delete(`/api/resources/${id}`),
};

// ── Bookings API ────────────────────────────────────────
export const bookingsAPI = {
  list: (params) => api.get('/api/bookings/', { params }),
  listAll: (params) => api.get('/api/bookings/all', { params }),
  get: (id) => api.get(`/api/bookings/${id}`),
  create: (data) => api.post('/api/bookings/', data),
  checkAvailability: (resourceId, date) =>
    api.get(`/api/bookings/availability/${resourceId}`, { params: { date } }),
  approve: (id, data) => api.put(`/api/bookings/${id}/approve`, data),
  cancel: (id) => api.put(`/api/bookings/${id}/cancel`),
  getNotifications: () => api.get('/api/bookings/notifications/mine'),
  markNotificationsRead: () => api.put('/api/bookings/notifications/read'),
};

// ── Analytics API ───────────────────────────────────────
export const analyticsAPI = {
  dashboard: () => api.get('/api/analytics/dashboard'),
  utilization: (days = 30) => api.get('/api/analytics/utilization', { params: { days } }),
  recentActivity: (limit = 10) => api.get('/api/analytics/recent-activity', { params: { limit } }),
};

export default api;
