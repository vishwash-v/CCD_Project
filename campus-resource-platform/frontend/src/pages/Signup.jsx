import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { HiOutlineMail, HiOutlineLockClosed, HiOutlineUser, HiOutlineAcademicCap } from 'react-icons/hi';

export default function Signup() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('student');
  const [department, setDepartment] = useState('');
  const [loading, setLoading] = useState(false);
  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }
    setLoading(true);
    try {
      await signup({ name, email, password, role, department });
      toast.success('Account created successfully!');
      navigate('/dashboard');
    } catch (error) {
      const msg = error.response?.data?.detail || 'Signup failed';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-bg-shapes">
        <div className="shape shape-1"></div>
        <div className="shape shape-2"></div>
        <div className="shape shape-3"></div>
      </div>

      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-logo">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <h1>Join CampusBook</h1>
          <p>Create your account to start booking</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="signup-name"><HiOutlineUser /> Full Name</label>
            <input id="signup-name" type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Your full name" required autoFocus />
          </div>

          <div className="form-group">
            <label htmlFor="signup-email"><HiOutlineMail /> Email</label>
            <input id="signup-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@campus.edu" required />
          </div>

          <div className="form-group">
            <label htmlFor="signup-password"><HiOutlineLockClosed /> Password</label>
            <input id="signup-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Min 6 characters" required />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="signup-role"><HiOutlineAcademicCap /> Role</label>
              <select id="signup-role" value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="student">Student</option>
                <option value="faculty">Faculty</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="signup-dept">Department</label>
              <input id="signup-dept" type="text" value={department} onChange={(e) => setDepartment(e.target.value)} placeholder="e.g., Computer Engg" />
            </div>
          </div>

          <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <div className="auth-footer">
          <p>Already have an account? <Link to="/login" className="auth-link">Sign In</Link></p>
        </div>
      </div>
    </div>
  );
}
