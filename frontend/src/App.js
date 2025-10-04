import React, { useState, useEffect } from 'react';
import SimpleLogin from './components/SimpleLogin';
import SimpleSignup from './components/SimpleSignup';
import WorkingCompanySetup from './components/WorkingCompanySetup';
import SimpleDashboard from './components/SimpleDashboard';
import DemoCompanySetup from './components/DemoCompanySetup';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('login');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const backendUrl = window.location.origin;
      const response = await fetch(`${backendUrl}/api/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        
        if (!userData.onboarding_completed) {
          setCurrentView('company-setup');
        } else {
          setCurrentView('dashboard');
        }
      } else {
        localStorage.removeItem('token');
      }
    } catch (err) {
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userData) => {
    setUser(userData);
    if (!userData.onboarding_completed) {
      setCurrentView('company-setup');
    } else {
      setCurrentView('dashboard');
    }
  };

  const handleSignup = (userData) => {
    setUser(userData);
    setCurrentView('company-setup');
  };

  const handleCompanySetupComplete = () => {
    setUser(prev => ({ ...prev, onboarding_completed: true }));
    setCurrentView('dashboard');
  };

  const handleLogout = () => {
    setUser(null);
    setCurrentView('login');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2">Loading...</p>
        </div>
      </div>
    );
  }

  if (currentView === 'login') {
    return (
      <SimpleLogin 
        onLogin={handleLogin} 
        onSwitchToSignup={() => setCurrentView('signup')}
      />
    );
  }

  if (currentView === 'signup') {
    return (
      <SimpleSignup 
        onSignup={handleSignup}
        onSwitchToLogin={() => setCurrentView('login')}
      />
    );
  }

  if (currentView === 'company-setup') {
    return (
      <WorkingCompanySetup 
        user={user}
        onComplete={handleCompanySetupComplete}
      />
    );
  }

  if (currentView === 'dashboard') {
    return (
      <SimpleDashboard 
        user={user}
        onLogout={handleLogout}
      />
    );
  }

  return null;
}

export default App;
