import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { analyticsAPI } from '../services/api';
import { CategoryPieChart } from '../components/UtilizationChart';
import { HiOutlineCube, HiOutlineCalendar, HiOutlineUsers, HiOutlineClock, HiOutlineCheckCircle, HiOutlineXCircle } from 'react-icons/hi';

export default function Dashboard() {
  const { user, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const [dashRes, actRes] = await Promise.all([
        analyticsAPI.dashboard(),
        analyticsAPI.recentActivity(8),
      ]);
      setStats(dashRes.data);
      setActivity(actRes.data.activities || []);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const statusColors = {
    pending: '#f59e0b',
    approved: '#10b981',
    rejected: '#ef4444',
    cancelled: '#94a3b8',
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-screen">
          <div className="spinner"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Welcome back, {user?.name?.split(' ')[0]}</h1>
          <p className="page-subtitle">Here's an overview of your campus resource activity</p>
        </div>
        <button className="btn btn-primary" onClick={() => navigate('/resources')}>
          <HiOutlineCube /> Browse Resources
        </button>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card" style={{ '--accent': '#6366f1' }}>
          <div className="stat-icon"><HiOutlineCube /></div>
          <div className="stat-info">
            <span className="stat-value">{stats?.total_resources || 0}</span>
            <span className="stat-label">Total Resources</span>
          </div>
        </div>

        <div className="stat-card" style={{ '--accent': '#06b6d4' }}>
          <div className="stat-icon"><HiOutlineCalendar /></div>
          <div className="stat-info">
            <span className="stat-value">{stats?.my_bookings || 0}</span>
            <span className="stat-label">My Bookings</span>
          </div>
        </div>

        <div className="stat-card" style={{ '--accent': '#f59e0b' }}>
          <div className="stat-icon"><HiOutlineClock /></div>
          <div className="stat-info">
            <span className="stat-value">{stats?.pending_bookings || 0}</span>
            <span className="stat-label">Pending</span>
          </div>
        </div>

        <div className="stat-card" style={{ '--accent': '#10b981' }}>
          <div className="stat-icon"><HiOutlineCheckCircle /></div>
          <div className="stat-info">
            <span className="stat-value">{stats?.approved_bookings || 0}</span>
            <span className="stat-label">Approved</span>
          </div>
        </div>

        {isAdmin && (
          <div className="stat-card" style={{ '--accent': '#8b5cf6' }}>
            <div className="stat-icon"><HiOutlineUsers /></div>
            <div className="stat-info">
              <span className="stat-value">{stats?.total_users || 0}</span>
              <span className="stat-label">Total Users</span>
            </div>
          </div>
        )}
      </div>

      {/* Charts + Activity */}
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <CategoryPieChart data={stats?.resource_categories} />
        </div>

        <div className="dashboard-card">
          <h3 className="chart-title">Recent Activity</h3>
          <div className="activity-list">
            {activity.length === 0 ? (
              <div className="empty-state">
                <p>No recent activity</p>
                <button className="btn btn-primary" onClick={() => navigate('/resources')}>
                  Make your first booking
                </button>
              </div>
            ) : (
              activity.map((item) => (
                <div key={item.id} className="activity-item">
                  <div className="activity-dot" style={{ background: statusColors[item.status] || '#94a3b8' }}></div>
                  <div className="activity-content">
                    <span className="activity-resource">{item.resource_name}</span>
                    <span className="activity-meta">
                      {item.date} · {item.start_time}-{item.end_time}
                    </span>
                  </div>
                  <span className={`status-badge ${item.status}`}>{item.status}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
