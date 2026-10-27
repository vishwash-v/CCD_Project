import { useState, useEffect } from 'react';
import { bookingsAPI } from '../services/api';
import toast from 'react-hot-toast';
import { HiOutlineX, HiOutlineClock, HiOutlineCalendar, HiOutlineCheckCircle } from 'react-icons/hi';

const timeSlots = [];
for (let h = 6; h < 22; h++) {
  timeSlots.push(`${String(h).padStart(2, '0')}:00`);
  timeSlots.push(`${String(h).padStart(2, '0')}:30`);
}

export default function BookingModal({ resource, onClose, onSuccess }) {
  const [date, setDate] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [purpose, setPurpose] = useState('');
  const [bookedSlots, setBookedSlots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [checkingAvailability, setCheckingAvailability] = useState(false);

  // Get today's date in YYYY-MM-DD format
  const today = new Date().toISOString().split('T')[0];

  useEffect(() => {
    if (date && resource) {
      checkAvailability();
    }
  }, [date]);

  const checkAvailability = async () => {
    setCheckingAvailability(true);
    try {
      const response = await bookingsAPI.checkAvailability(resource.id, date);
      setBookedSlots(response.data.booked_slots || []);
    } catch (error) {
      console.error('Failed to check availability:', error);
    } finally {
      setCheckingAvailability(false);
    }
  };

  const isSlotBooked = (time) => {
    return bookedSlots.some(
      (slot) => time >= slot.start_time && time < slot.end_time
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!date || !startTime || !endTime) {
      toast.error('Please fill in all required fields');
      return;
    }

    if (startTime >= endTime) {
      toast.error('End time must be after start time');
      return;
    }

    setLoading(true);
    try {
      await bookingsAPI.create({
        resource_id: resource.id,
        date,
        start_time: startTime,
        end_time: endTime,
        purpose,
      });
      toast.success('Booking request submitted successfully!');
      onSuccess?.();
      onClose();
    } catch (error) {
      const msg = error.response?.data?.detail || 'Failed to create booking';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Book Resource</h2>
          <button className="icon-btn" onClick={onClose}>
            <HiOutlineX />
          </button>
        </div>

        <div className="modal-resource-info">
          <h3>{resource.name}</h3>
          <p>{resource.location}</p>
        </div>

        <form onSubmit={handleSubmit} className="booking-form">
          <div className="form-group">
            <label htmlFor="booking-date">
              <HiOutlineCalendar /> Date
            </label>
            <input
              id="booking-date"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              min={today}
              required
            />
          </div>

          {date && (
            <>
              {checkingAvailability ? (
                <div className="loading-slots">Checking availability...</div>
              ) : bookedSlots.length > 0 ? (
                <div className="booked-slots-info">
                  <p className="slots-label">Already booked slots:</p>
                  <div className="booked-slots-list">
                    {bookedSlots.map((slot, i) => (
                      <span key={i} className="booked-slot-tag">
                        {slot.start_time} - {slot.end_time}
                        <span className={`slot-status ${slot.status}`}>
                          {slot.status}
                        </span>
                      </span>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="all-clear">
                  <HiOutlineCheckCircle />
                  <span>All time slots are available</span>
                </div>
              )}

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="start-time">
                    <HiOutlineClock /> Start Time
                  </label>
                  <select
                    id="start-time"
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    required
                  >
                    <option value="">Select...</option>
                    {timeSlots.map((slot) => (
                      <option
                        key={slot}
                        value={slot}
                        disabled={isSlotBooked(slot)}
                      >
                        {slot} {isSlotBooked(slot) ? '(Booked)' : ''}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="end-time">
                    <HiOutlineClock /> End Time
                  </label>
                  <select
                    id="end-time"
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                    required
                  >
                    <option value="">Select...</option>
                    {timeSlots
                      .filter((slot) => !startTime || slot > startTime)
                      .map((slot) => (
                        <option
                          key={slot}
                          value={slot}
                          disabled={isSlotBooked(slot)}
                        >
                          {slot} {isSlotBooked(slot) ? '(Booked)' : ''}
                        </option>
                      ))}
                  </select>
                </div>
              </div>
            </>
          )}

          <div className="form-group">
            <label htmlFor="purpose">Purpose (optional)</label>
            <textarea
              id="purpose"
              value={purpose}
              onChange={(e) => setPurpose(e.target.value)}
              placeholder="E.g., Workshop on Cloud Computing, Lab session..."
              rows={3}
            />
          </div>

          <div className="modal-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !date || !startTime || !endTime}
            >
              {loading ? 'Submitting...' : 'Submit Booking'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
