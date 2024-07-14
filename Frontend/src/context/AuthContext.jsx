import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const verifyToken = async (token) => {
    try {
      const response = await fetch('http://localhost:5000/verify-token', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
      });

      return response.ok;
    } catch (error) {
      console.error('Token verification error:', error);
      return false;
    }
  };

  useEffect(() => {
    const checkToken = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        const isValid = await verifyToken(token);
        if (isValid) {
          setUser({ token });
        } else {
          localStorage.removeItem('token');
          setUser(null);
        }
      }
      setLoading(false);
    };

    checkToken();

    // Set up periodic token verification
    const intervalId = setInterval(checkToken, 1 * 60 * 1000); // Check every  minutes

    return () => clearInterval(intervalId);
  }, []);

  const login = async (username, password) => {
    try {
      const response = await fetch('http://localhost:5000/login', {
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) throw new Error('Login failed');

      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      setUser({ token: data.access_token });
      return true;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const register = async (username, email, password) => {
    try {
      const response = await fetch('http://localhost:5000/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password }),
      });

      if (!response.ok) throw new Error('Registration failed');
      return true;
    } catch (error) {
      console.error('Registration error:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  const isAuthenticated = () => {
    return !!user;
  };

  if (loading) {
    return <div>Loading...</div>; // or some loading indicator
  }

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);