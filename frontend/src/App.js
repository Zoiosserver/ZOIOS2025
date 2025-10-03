import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from '@/components/ui/sonner';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './components/Dashboard';
import Contacts from './components/Contacts';
import Companies from './components/Companies';
import CallLogs from './components/CallLogs';
import EmailResponses from './components/EmailResponses';
import UserManagement from './components/UserManagement';
import CurrencyManagement from './components/CurrencyManagement';
import ConsolidatedAccounts from './components/ConsolidatedAccounts';
import CompanyAccounts from './components/CompanyAccounts';
import ResetPassword from './components/ResetPassword';
import Sidebar from './components/Sidebar';
import './App.css';

function App() {
  return (
    <div className="App">
      <AuthProvider>
        <Router>
          <Routes>
            {/* Public route for password reset */}
            <Route path="/reset-password" element={<ResetPassword />} />
            
            {/* Protected routes */}
            <Route path="/*" element={
              <ProtectedRoute>
                <div className="flex min-h-screen bg-gray-50">
                  <Sidebar />
                  <main className="flex-1 ml-64 p-6">
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/contacts" element={<Contacts />} />
                      <Route path="/companies" element={<Companies />} />
                      <Route path="/call-logs" element={<CallLogs />} />
                      <Route path="/email-responses" element={<EmailResponses />} />
                      <Route path="/users" element={<UserManagement />} />
                      <Route path="/currency" element={<CurrencyManagement />} />
                      <Route path="/consolidated-accounts" element={<ConsolidatedAccounts />} />
                      <Route path="/company-accounts" element={<CompanyAccounts />} />
                      <Route path="/user-assignments" element={<UserManagement />} />
                    </Routes>
                  </main>
                </div>
              </ProtectedRoute>
            } />
          </Routes>
          <Toaster position="top-right" />
        </Router>
      </AuthProvider>
    </div>
  );
}

export default App;
