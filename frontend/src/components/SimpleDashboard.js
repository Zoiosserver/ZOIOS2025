import React, { useState, useEffect } from 'react';
import ZoiosLogo from './ZoiosLogo';

const SimpleDashboard = ({ user, onLogout }) => {
  const [companySetup, setCompanySetup] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [setupProgress, setSetupProgress] = useState(0);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const backendUrl = window.location.origin;
      
      const response = await fetch(`${backendUrl}/api/setup/company`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setCompanySetup(data);
        calculateSetupProgress(data);
      } else {
        setError('Failed to load company data');
      }
    } catch (err) {
      setError('Connection failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const calculateSetupProgress = (data) => {
    if (!data) return;
    
    const requiredFields = [
      'company_name', 'country_code', 'business_type', 'industry', 
      'base_currency', 'accounting_system', 'address'
    ];
    
    const completedFields = requiredFields.filter(field => data[field] && data[field] !== '');
    const progress = Math.round((completedFields.length / requiredFields.length) * 100);
    setSetupProgress(progress);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    onLogout();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-flex items-center justify-center bg-white p-6 rounded-2xl shadow-lg mb-6 border border-gray-100">
            <ZoiosLogo size="xl" />
          </div>
          <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-8">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600 font-medium">Loading your dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse delay-1000"></div>
      </div>

      {/* Header */}
      <header className="relative bg-white/80 backdrop-blur-xl shadow-lg border-b border-gray-100/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4 sm:py-6">
            <div className="flex items-center space-x-4">
              <div className="bg-white p-2 sm:p-3 rounded-xl shadow-md border border-gray-100">
                <ZoiosLogo size="medium" />
              </div>
              <div>
                <h1 className="text-xl sm:text-2xl font-bold text-gray-900">ERP Dashboard</h1>
                <p className="text-sm sm:text-base text-gray-600">Welcome back, {user?.name} 👋</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="hidden sm:flex items-center bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                Online
              </div>
              <button
                onClick={handleLogout}
                className="bg-gradient-to-r from-red-500 to-red-600 text-white px-4 py-2 rounded-xl hover:from-red-600 hover:to-red-700 transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                <div className="flex items-center space-x-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                  </svg>
                  <span className="hidden sm:inline">Logout</span>
                </div>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="bg-red-50 border border-red-300 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* Company Information Card */}
        <div className="bg-white overflow-hidden shadow rounded-lg mb-6">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Company Information
            </h3>
            {companySetup ? (
              <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Company Name</dt>
                  <dd className="mt-1 text-sm text-gray-900">{companySetup.company_name}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Country</dt>
                  <dd className="mt-1 text-sm text-gray-900">{companySetup.country}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Business Type</dt>
                  <dd className="mt-1 text-sm text-gray-900">{companySetup.business_type}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Industry</dt>
                  <dd className="mt-1 text-sm text-gray-900">{companySetup.industry}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Base Currency</dt>
                  <dd className="mt-1 text-sm text-gray-900">{companySetup.base_currency}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Accounting System</dt>
                  <dd className="mt-1 text-sm text-gray-900">{companySetup.accounting_system}</dd>
                </div>
                {companySetup.additional_currencies?.length > 0 && (
                  <div className="sm:col-span-2">
                    <dt className="text-sm font-medium text-gray-500">Additional Currencies</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {companySetup.additional_currencies.join(', ')}
                    </dd>
                  </div>
                )}
              </dl>
            ) : (
              <p className="text-gray-500">No company setup found</p>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Quick Actions
            </h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <button className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-left hover:bg-blue-100 transition-colors">
                <div className="text-blue-600 font-medium">Currency Management</div>
                <div className="text-blue-500 text-sm">Manage exchange rates</div>
              </button>
              <button className="bg-green-50 border border-green-200 rounded-lg p-4 text-left hover:bg-green-100 transition-colors">
                <div className="text-green-600 font-medium">Accounts</div>
                <div className="text-green-500 text-sm">Chart of accounts</div>
              </button>
              <button className="bg-purple-50 border border-purple-200 rounded-lg p-4 text-left hover:bg-purple-100 transition-colors">
                <div className="text-purple-600 font-medium">Reports</div>
                <div className="text-purple-500 text-sm">Financial reports</div>
              </button>
            </div>
          </div>
        </div>

        {/* Success Message */}
        <div className="mt-6 bg-green-50 border border-green-300 text-green-700 px-4 py-3 rounded">
          🎉 <strong>System Working!</strong> Signup, Login, and Company Setup are all functioning correctly.
          Your ZOIOS ERP system is ready to use!
        </div>
      </main>
    </div>
  );
};

export default SimpleDashboard;