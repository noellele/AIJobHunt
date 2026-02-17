import { createContext, useState, useContext, useEffect, useCallback } from 'react';
import { Toast, ToastContainer } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState({ show: false, message: '', variant: 'success' });
  const navigate = useNavigate();

  const checkAuth = useCallback(async () => {
    const token = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    if (token && storedUser && storedUser !== "undefined") {
      try {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        setUser(JSON.parse(storedUser));
        const res = await api.get('/auth/me');
        setUser(res.data);
      } catch (error) {
        console.error("Auth initialization failed:", error);
        logout();
      }
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = (token, userData, shouldNavigate = false) => {
    setUser(userData);
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    if (shouldNavigate) navigate('/dashboard');
  };

  const notify = (message, variant = 'success') => {
    setToast({ show: true, message, variant });
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
    navigate('/login');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading, notify }}>
    {children}

    {/* 3. Render the Global ToastContainer here */}
    <ToastContainer position="top-end" className="p-3" style={{ zIndex: 9999, position: 'fixed' }}>
      <Toast
        onClose={() => setToast({ ...toast, show: false })}
        show={toast.show}
        delay={4000}
        autohide
        bg={toast.variant}
      >
        <Toast.Header><strong className="me-auto">System Notification</strong></Toast.Header>
        <Toast.Body className={toast.variant === 'success' ? 'text-white' : ''}>
          {toast.message}
        </Toast.Body>
      </Toast>
    </ToastContainer>
  </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);