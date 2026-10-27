import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useState } from 'react';
import {
  HiOutlineHome,
  HiOutlineCube,
  HiOutlineCalendar,
  HiOutlineChartBar,
  HiOutlineUser,
  HiOutlineLogout,
  HiOutlineMenu,
  HiOutlineX,
  HiOutlineBell,
} from 'react-icons/hi';

export default function Navbar() {
  const { user, logout, isAdmin } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navLinks = [
    { to: '/dashboard', label: 'Dashboard', icon: <HiOutlineHome /> },
    { to: '/resources', label: 'Resources', icon: <HiOutlineCube /> },
    { to: '/bookings', label: 'My Bookings', icon: <HiOutlineCalendar /> },
    ...(isAdmin
      ? [{ to: '/admin', label: 'Admin Panel', icon: <HiOutlineChartBar /> }]
      : []),
  ];

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/dashboard" className="navbar-brand">
          <div className="brand-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <span>CampusBook</span>
        </Link>

        <div className={`navbar-links ${mobileOpen ? 'open' : ''}`}>
          {navLinks.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={`nav-link ${location.pathname === link.to ? 'active' : ''}`}
              onClick={() => setMobileOpen(false)}
            >
              {link.icon}
              <span>{link.label}</span>
            </Link>
          ))}
        </div>

        <div className="navbar-actions">
          <button className="icon-btn notification-btn" title="Notifications">
            <HiOutlineBell />
          </button>

          <div className="user-menu">
            <div className="user-avatar">
              {user?.name?.charAt(0)?.toUpperCase() || 'U'}
            </div>
            <div className="user-info">
              <span className="user-name">{user?.name || 'User'}</span>
              <span className="user-role">{user?.role || 'student'}</span>
            </div>
          </div>

          <button className="icon-btn logout-btn" onClick={handleLogout} title="Logout">
            <HiOutlineLogout />
          </button>

          <button
            className="icon-btn mobile-toggle"
            onClick={() => setMobileOpen(!mobileOpen)}
          >
            {mobileOpen ? <HiOutlineX /> : <HiOutlineMenu />}
          </button>
        </div>
      </div>
    </nav>
  );
}
