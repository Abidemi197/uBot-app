import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import Chat from './components/Chat/Chat';
import KnowledgeBase from './components/KnowledgeBase/KnowledgeBase';
import About from './components/About/About';
import styles from './App.module.css';

function PrivateRoute({ children }) {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" />;
}

function Navigation() {
  const { user, logout } = useAuth();
  const location = useLocation();

  return (
    <nav className={styles.nav}>
      <ul className={styles.navList}>
        <li className={styles.navItem}>
          <Link to="/about" className={`${styles.navLink} ${location.pathname === '/about' ? styles.activeLink : ''}`}>About</Link>
        </li>
        {user ? (
          <>
            <li className={styles.navItem}>
              <Link to="/chat" className={`${styles.navLink} ${location.pathname === '/chat' ? styles.activeLink : ''}`}>Chat</Link>
            </li>
            <li className={styles.navItem}>
              <button onClick={logout} className={styles.logoutButton}>Logout</button>
            </li>
          </>
        ) : (
          <>
            <li className={styles.navItem}>
              <Link to="/login" className={`${styles.navLink} ${location.pathname === '/login' ? styles.activeLink : ''}`}>Login</Link>
            </li>
            <li className={styles.navItem}>
              <Link to="/register" className={`${styles.navLink} ${location.pathname === '/register' ? styles.activeLink : ''}`}>Register</Link>
            </li>
          </>
        )}
      </ul>
    </nav>
  );
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/chat" element={<PrivateRoute><Chat /></PrivateRoute>} />
      <Route path="/knowledge-base" element={<PrivateRoute><KnowledgeBase /></PrivateRoute>} />
      <Route path="/about" element={<About />} />
      <Route path="/" element={<Navigate to="/about" />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className={styles.app}>
          <Navigation />
          <main className={styles.content}>
            <AppRoutes />
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;