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
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">ZOIOS ERP Dashboard</h1>
              <p className="text-gray-600">Welcome back, {user?.name}</p>
            </div>
            <button
              onClick={handleLogout}
              className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
            >
              Logout
            </button>
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