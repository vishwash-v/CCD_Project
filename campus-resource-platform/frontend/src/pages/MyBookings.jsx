import { useState, useEffect } from 'react';
import { bookingsAPI } from '../services/api';
import toast from 'react-hot-toast';
import { HiOutlineCalendar, HiOutlineClock, HiOutlineLocationMarker, HiOutlineXCircle } from 'react-icons/hi';

const statusFilters = [
  { value: '', label: 'All' },
  { value: 'pending', label: 'Pending' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'cancelled', label: 'Cancelled' },
];

export default function MyBookings() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    loadBookings();
  }, [statusFilter]);

  const loadBookings = async () => {
    setLoading(true);
    try {
      const params = {};
      if (statusFilter) params.status = statusFilter;
      const response = await bookingsAPI.list(params);
      setBookings(response.data);
    } catch (error) {
      toast.error('Failed to load bookings');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (bookingId) => {
    if (!confirm('Are you sure you want to cancel this booking?')) return;
    try {
      await bookingsAPI.cancel(bookingId);
      toast.success('Booking cancelled');
      loadBookings();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to cancel');
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>My Bookings</h1>
          <p className="page-subtitle">View and manage your resource bookings</p>
        </div>
      </div>

      {/* Status Filters */}
      <div className="filter-bar">
        <div className="category-filters">
          {statusFilters.map((f) => (
            <button
              key={f.value}
              className={`filter-chip ${statusFilter === f.value ? 'active' : ''}`}
              onClick={() => setStatusFilter(f.value)}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Bookings List */}
      {loading ? (
        <div className="loading-screen">
          <div className="spinner"></div>
          <p>Loading bookings...</p>
        </div>
      ) : bookings.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">
            <HiOutlineCalendar />
          </div>
          <h3>No bookings found</h3>
          <p>You haven't made any bookings yet. Browse resources to get started!</p>
        </div>
      ) : (
        <div className="bookings-list">
          {bookings.map((booking) => (
            <div key={booking.id} className={`booking-card ${booking.status}`}>
              <div className="booking-card-left">
                <div className="booking-date-badge">
                  <span className="date-day">
                    {new Date(booking.date + 'T00:00:00').getDate()}
                  </span>
                  <span className="date-month">
                    {new Date(booking.date + 'T00:00:00').toLocaleString('default', { month: 'short' })}
                  </span>
                </div>
              </div>

              <div className="booking-card-content">
                <h3 className="booking-resource">{booking.resource_name}</h3>
                <div className="booking-details">
                  <span className="booking-detail">
                    <HiOutlineClock />
                    {booking.start_time} - {booking.end_time}
                  </span>
                  <span className="booking-detail">
                    <HiOutlineCalendar />
                    {booking.date}
                  </span>
                </div>
                {booking.purpose && (
                  <p className="booking-purpose">{booking.purpose}</p>
                )}
                {booking.rejection_reason && (
                  <p className="booking-rejection">
                    Reason: {booking.rejection_reason}
                  </p>
                )}
              </div>

              <div className="booking-card-right">
                <span className={`status-badge ${booking.status}`}>
                  {booking.status}
                </span>
                {(booking.status === 'pending' || booking.status === 'approved') && (
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handleCancel(booking.id)}
                  >
                    <HiOutlineXCircle /> Cancel
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
