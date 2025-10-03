import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from '@/components/ui/sonner';
import Dashboard from './components/Dashboard';
import Contacts from './components/Contacts';
import Companies from './components/Companies';
import CallLogs from './components/CallLogs';
import EmailResponses from './components/EmailResponses';
import Sidebar from './components/Sidebar';
import './App.css';

function App() {
  return (
    <div className="App">
      <Router>
        <div className="flex min-h-screen bg-gray-50">
          <Sidebar />
          <main className="flex-1 ml-64 p-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/contacts" element={<Contacts />} />
              <Route path="/companies" element={<Companies />} />
              <Route path="/call-logs" element={<CallLogs />} />
              <Route path="/email-responses" element={<EmailResponses />} />
            </Routes>
          </main>
        </div>
        <Toaster position="top-right" />
      </Router>
    </div>
  );
}

export default App;
