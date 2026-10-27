import { useState, useEffect } from 'react';
import { resourcesAPI } from '../services/api';
import ResourceCard from '../components/ResourceCard';
import BookingModal from '../components/BookingModal';
import toast from 'react-hot-toast';
import { HiOutlineSearch, HiOutlineFilter, HiOutlineCube } from 'react-icons/hi';

const categories = [
  { value: '', label: 'All Categories' },
  { value: 'hall', label: 'Halls' },
  { value: 'lab', label: 'Labs' },
  { value: 'classroom', label: 'Classrooms' },
  { value: 'equipment', label: 'Equipment' },
  { value: 'facility', label: 'Facilities' },
  { value: 'sports', label: 'Sports' },
];

export default function ResourceCatalog() {
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [selectedResource, setSelectedResource] = useState(null);

  useEffect(() => {
    loadResources();
  }, [category]);

  const loadResources = async () => {
    setLoading(true);
    try {
      const params = {};
      if (category) params.category = category;
      if (search) params.search = search;
      const response = await resourcesAPI.list(params);
      setResources(response.data);
    } catch (error) {
      toast.error('Failed to load resources');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadResources();
  };

  const filteredResources = resources.filter((r) => {
    if (!search) return true;
    const s = search.toLowerCase();
    return (
      r.name.toLowerCase().includes(s) ||
      r.location.toLowerCase().includes(s) ||
      r.description?.toLowerCase().includes(s)
    );
  });

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Campus Resources</h1>
          <p className="page-subtitle">Browse and book available campus resources</p>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="filter-bar">
        <form onSubmit={handleSearch} className="search-box">
          <HiOutlineSearch />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search resources by name, location..."
          />
        </form>

        <div className="category-filters">
          {categories.map((cat) => (
            <button
              key={cat.value}
              className={`filter-chip ${category === cat.value ? 'active' : ''}`}
              onClick={() => setCategory(cat.value)}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Resource Grid */}
      {loading ? (
        <div className="loading-screen">
          <div className="spinner"></div>
          <p>Loading resources...</p>
        </div>
      ) : filteredResources.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">
            <HiOutlineCube />
          </div>
          <h3>No resources found</h3>
          <p>Try a different search term or category</p>
        </div>
      ) : (
        <div className="resource-grid">
          {filteredResources.map((resource) => (
            <ResourceCard
              key={resource.id}
              resource={resource}
              onBook={setSelectedResource}
            />
          ))}
        </div>
      )}

      {/* Booking Modal */}
      {selectedResource && (
        <BookingModal
          resource={selectedResource}
          onClose={() => setSelectedResource(null)}
          onSuccess={loadResources}
        />
      )}
    </div>
  );
}
