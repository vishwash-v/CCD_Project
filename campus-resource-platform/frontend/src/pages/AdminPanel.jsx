import { useState, useEffect } from 'react';
import { bookingsAPI, analyticsAPI, resourcesAPI } from '../services/api';
import { PeakHoursChart, UtilizationChart } from '../components/UtilizationChart';
import toast from 'react-hot-toast';
import {
  HiOutlineCheckCircle,
  HiOutlineXCircle,
  HiOutlinePlus,
  HiOutlineTrash,
  HiOutlineClock,
  HiOutlineCalendar,
  HiOutlineX,
} from 'react-icons/hi';

export default function AdminPanel() {
  const [activeTab, setActiveTab] = useState('approvals');
  const [pendingBookings, setPendingBookings] = useState([]);
  const [utilization, setUtilization] = useState(null);
  const [loading, setLoading] = useState(true);

  // Resource management state
  const [showAddResource, setShowAddResource] = useState(false);
  const [newResource, setNewResource] = useState({
    name: '', category: 'classroom', location: '', capacity: 0, amenities: '', description: '',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [bookingsRes, utilRes] = await Promise.all([
        bookingsAPI.listAll({ status: 'pending' }),
        analyticsAPI.utilization(30).catch(() => ({ data: null })),
      ]);
      setPendingBookings(bookingsRes.data);
      setUtilization(utilRes.data);
    } catch (error) {
      console.error('Failed to load admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id) => {
    try {
      await bookingsAPI.approve(id, { status: 'approved' });
      toast.success('Booking approved!');
      loadData();
    } catch (error) {
      toast.error('Failed to approve');
    }
  };

  const handleReject = async (id) => {
    const reason = prompt('Rejection reason (optional):');
    try {
      await bookingsAPI.approve(id, { status: 'rejected', reason });
      toast.success('Booking rejected');
      loadData();
    } catch (error) {
      toast.error('Failed to reject');
    }
  };

  const handleAddResource = async (e) => {
    e.preventDefault();
    try {
      await resourcesAPI.create({
        ...newResource,
        amenities: newResource.amenities.split(',').map((a) => a.trim()).filter(Boolean),
        capacity: parseInt(newResource.capacity) || 0,
      });
      toast.success('Resource added!');
      setShowAddResource(false);
      setNewResource({ name: '', category: 'classroom', location: '', capacity: 0, amenities: '', description: '' });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add resource');
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-screen"><div className="spinner"></div><p>Loading admin panel...</p></div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Admin Panel</h1>
          <p className="page-subtitle">Manage bookings, resources, and view analytics</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowAddResource(true)}>
          <HiOutlinePlus /> Add Resource
        </button>
      </div>

      {/* Tabs */}
      <div className="admin-tabs">
        {[
          { id: 'approvals', label: `Pending Approvals (${pendingBookings.length})` },
          { id: 'analytics', label: 'Analytics' },
        ].map((tab) => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Approvals Tab */}
      {activeTab === 'approvals' && (
        <div className="approvals-section">
          {pendingBookings.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">
                <HiOutlineCheckCircle />
              </div>
              <h3>All caught up!</h3>
              <p>No pending booking requests</p>
            </div>
          ) : (
            <div className="bookings-list">
              {pendingBookings.map((booking) => (
                <div key={booking.id} className="booking-card pending">
                  <div className="booking-card-left">
                    <div className="booking-date-badge">
                      <span className="date-day">{new Date(booking.date + 'T00:00:00').getDate()}</span>
                      <span className="date-month">{new Date(booking.date + 'T00:00:00').toLocaleString('default', { month: 'short' })}</span>
                    </div>
                  </div>
                  <div className="booking-card-content">
                    <h3 className="booking-resource">{booking.resource_name}</h3>
                    <p className="booking-user">Requested by: <strong>{booking.user_name}</strong></p>
                    <div className="booking-details">
                      <span className="booking-detail">
                        <HiOutlineClock /> {booking.start_time} - {booking.end_time}
                      </span>
                      <span className="booking-detail">
                        <HiOutlineCalendar /> {booking.date}
                      </span>
                    </div>
                    {booking.purpose && <p className="booking-purpose">{booking.purpose}</p>}
                  </div>
                  <div className="booking-card-right">
                    <button className="btn btn-success btn-sm" onClick={() => handleApprove(booking.id)}>
                      <HiOutlineCheckCircle /> Approve
                    </button>
                    <button className="btn btn-danger btn-sm" onClick={() => handleReject(booking.id)}>
                      <HiOutlineXCircle /> Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && utilization && (
        <div className="analytics-section">
          <div className="analytics-grid">
            <PeakHoursChart data={utilization.peak_hours} />
            <UtilizationChart data={utilization.resource_utilization} />
          </div>
          <div className="analytics-summary">
            <div className="summary-card">
              <span className="summary-value">{utilization.total_bookings}</span>
              <span className="summary-label">Total Bookings (30 days)</span>
            </div>
            <div className="summary-card">
              <span className="summary-value">{utilization.total_resources}</span>
              <span className="summary-label">Total Resources</span>
            </div>
          </div>
        </div>
      )}

      {/* Add Resource Modal */}
      {showAddResource && (
        <div className="modal-overlay" onClick={() => setShowAddResource(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Add New Resource</h2>
              <button className="icon-btn" onClick={() => setShowAddResource(false)}>
                <HiOutlineX />
              </button>
            </div>
            <form onSubmit={handleAddResource} className="booking-form">
              <div className="form-group">
                <label>Resource Name</label>
                <input type="text" value={newResource.name} onChange={(e) => setNewResource({ ...newResource, name: e.target.value })} placeholder="e.g., Seminar Hall B" required />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Category</label>
                  <select value={newResource.category} onChange={(e) => setNewResource({ ...newResource, category: e.target.value })}>
                    <option value="classroom">Classroom</option>
                    <option value="lab">Lab</option>
                    <option value="hall">Hall</option>
                    <option value="equipment">Equipment</option>
                    <option value="facility">Facility</option>
                    <option value="sports">Sports</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Capacity</label>
                  <input type="number" value={newResource.capacity} onChange={(e) => setNewResource({ ...newResource, capacity: e.target.value })} min="0" />
                </div>
              </div>
              <div className="form-group">
                <label>Location</label>
                <input type="text" value={newResource.location} onChange={(e) => setNewResource({ ...newResource, location: e.target.value })} placeholder="e.g., Block A, Floor 2" required />
              </div>
              <div className="form-group">
                <label>Amenities (comma separated)</label>
                <input type="text" value={newResource.amenities} onChange={(e) => setNewResource({ ...newResource, amenities: e.target.value })} placeholder="projector, AC, whiteboard" />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea value={newResource.description} onChange={(e) => setNewResource({ ...newResource, description: e.target.value })} rows={3} placeholder="Brief description..." />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowAddResource(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Add Resource</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
