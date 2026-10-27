import {
  HiOutlineLocationMarker,
  HiOutlineUsers,
  HiOutlineClock,
  HiOutlineCube,
  HiOutlineOfficeBuilding,
  HiOutlineDesktopComputer,
} from 'react-icons/hi';
import { FiCpu, FiActivity, FiBookOpen } from 'react-icons/fi';

const categoryColors = {
  hall: '#6366f1',
  lab: '#06b6d4',
  equipment: '#f59e0b',
  facility: '#10b981',
  classroom: '#8b5cf6',
  sports: '#ef4444',
};

const getCategoryIcon = (category) => {
  switch (category) {
    case 'hall':
      return <HiOutlineOfficeBuilding />;
    case 'lab':
      return <FiCpu />;
    case 'equipment':
      return <HiOutlineDesktopComputer />;
    case 'facility':
      return <HiOutlineOfficeBuilding />;
    case 'classroom':
      return <FiBookOpen />;
    case 'sports':
      return <FiActivity />;
    default:
      return <HiOutlineCube />;
  }
};

export default function ResourceCard({ resource, onBook }) {
  const color = categoryColors[resource.category] || '#6366f1';

  return (
    <div className="resource-card" style={{ '--accent': color }}>
      <div className="resource-card-header">
        <div className="resource-icon">{getCategoryIcon(resource.category)}</div>
        <span className={`resource-badge ${resource.available ? 'available' : 'unavailable'}`}>
          {resource.available ? 'Available' : 'Unavailable'}
        </span>
      </div>

      <h3 className="resource-name">{resource.name}</h3>
      <span className="resource-category">{resource.category}</span>

      {resource.description && (
        <p className="resource-description">{resource.description}</p>
      )}

      <div className="resource-details">
        <div className="detail-item">
          <HiOutlineLocationMarker />
          <span>{resource.location}</span>
        </div>
        {resource.capacity > 0 && (
          <div className="detail-item">
            <HiOutlineUsers />
            <span>Capacity: {resource.capacity}</span>
          </div>
        )}
      </div>

      {resource.amenities?.length > 0 && (
        <div className="resource-amenities">
          {resource.amenities.map((amenity, i) => (
            <span key={i} className="amenity-tag">
              {amenity}
            </span>
          ))}
        </div>
      )}

      <button
        className="btn btn-primary book-btn"
        onClick={() => onBook(resource)}
        disabled={!resource.available}
      >
        <HiOutlineClock />
        Book Now
      </button>
    </div>
  );
}
