import React, { useState, useEffect } from 'react';
import ZoiosLogo from './ZoiosLogo';

const SimpleDashboard = ({ user, onLogout, onNavigateToCompanyManagement }) => {
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
      <main className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-lg animate-shake mb-6">
            <div className="flex">
              <svg className="w-5 h-5 text-red-400 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd"/>
              </svg>
              <span className="text-red-700 text-sm">{error}</span>
            </div>
          </div>
        )}

        {/* Dashboard Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Setup Progress Card */}
          <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm font-medium text-gray-600">Setup Progress</p>
                <p className="text-2xl font-bold text-gray-900">{setupProgress}%</p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${setupProgress}%` }}
              ></div>
            </div>
          </div>

          {/* Company Status */}
          <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm font-medium text-gray-600">Company Status</p>
                <p className="text-xl font-bold text-green-600">
                  {companySetup ? 'Active' : 'Setup Required'}
                </p>
              </div>
              <div className={`w-12 h-12 ${companySetup ? 'bg-gradient-to-r from-green-500 to-emerald-500' : 'bg-gradient-to-r from-yellow-500 to-orange-500'} rounded-xl flex items-center justify-center`}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
                </svg>
              </div>
            </div>
          </div>

          {/* Currency Info */}
          <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm font-medium text-gray-600">Base Currency</p>
                <p className="text-xl font-bold text-gray-900">
                  {companySetup?.base_currency || 'Not Set'}
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
                </svg>
              </div>
            </div>
            {companySetup?.additional_currencies?.length > 0 && (
              <p className="text-sm text-gray-500">+{companySetup.additional_currencies.length} additional</p>
            )}
          </div>

          {/* System Status */}
          <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm font-medium text-gray-600">System Health</p>
                <p className="text-xl font-bold text-green-600">Excellent</p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-lime-500 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
                </svg>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Company Information - Left Column */}
          <div className="lg:col-span-2 space-y-6">
            {/* Company Details Card */}
            <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6 sm:p-8">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900">Company Information</h3>
                </div>
                {setupProgress < 100 && (
                  <button className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white px-4 py-2 rounded-xl hover:from-blue-600 hover:to-indigo-600 transition-all duration-200 transform hover:scale-105 text-sm font-medium shadow-lg">
                    Complete Setup
                  </button>
                )}
              </div>
              
              {companySetup ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <dt className="text-sm font-medium text-gray-500 mb-1">Company Name</dt>
                      <dd className="text-base font-semibold text-gray-900 bg-gray-50 p-3 rounded-lg">
                        {companySetup.company_name}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500 mb-1">Business Type</dt>
                      <dd className="text-base font-semibold text-gray-900 bg-gray-50 p-3 rounded-lg">
                        {companySetup.business_type}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500 mb-1">Industry</dt>
                      <dd className="text-base font-semibold text-gray-900 bg-gray-50 p-3 rounded-lg">
                        {companySetup.industry}
                      </dd>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <dt className="text-sm font-medium text-gray-500 mb-1">Country</dt>
                      <dd className="text-base font-semibold text-gray-900 bg-gray-50 p-3 rounded-lg">
                        {companySetup.country_code || companySetup.country}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500 mb-1">Base Currency</dt>
                      <dd className="text-base font-semibold text-gray-900 bg-gray-50 p-3 rounded-lg">
                        {companySetup.base_currency}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500 mb-1">Accounting System</dt>
                      <dd className="text-base font-semibold text-gray-900 bg-gray-50 p-3 rounded-lg">
                        {companySetup.accounting_system}
                      </dd>
                    </div>
                  </div>
                  
                  {/* Address Information */}
                  {companySetup.address && (
                    <div className="md:col-span-2 mt-6 pt-6 border-t border-gray-200">
                      <h4 className="text-lg font-semibold text-gray-900 mb-4">Business Address</h4>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <p className="text-gray-900">
                          {companySetup.address}
                          {companySetup.city && `, ${companySetup.city}`}
                          {companySetup.state && `, ${companySetup.state}`}
                          {companySetup.postal_code && ` ${companySetup.postal_code}`}
                        </p>
                      </div>
                    </div>
                  )}
                  
                  {/* Additional Currencies */}
                  {companySetup.additional_currencies?.length > 0 && (
                    <div className="md:col-span-2 mt-6 pt-6 border-t border-gray-200">
                      <h4 className="text-lg font-semibold text-gray-900 mb-4">Additional Currencies</h4>
                      <div className="flex flex-wrap gap-2">
                        {companySetup.additional_currencies.map((currency, index) => (
                          <span key={index} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                            {currency}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Complete Company Setup</h3>
                  <p className="text-gray-600 mb-4">Set up your company information to get started with ZOIOS ERP</p>
                  <button className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white px-6 py-3 rounded-xl hover:from-blue-600 hover:to-indigo-600 transition-all duration-200 transform hover:scale-105 font-medium shadow-lg">
                    Start Setup
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Quick Actions & Tools */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z"/>
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-gray-900">Quick Actions</h3>
              </div>
              
              <div className="space-y-3">
                <button className="w-full bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4 text-left hover:from-blue-100 hover:to-indigo-100 transition-all duration-200 transform hover:scale-[1.02] group">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
                      </svg>
                    </div>
                    <div className="flex-1">
                      <div className="text-blue-700 font-semibold">Currency Management</div>
                      <div className="text-blue-600 text-sm">Manage exchange rates</div>
                    </div>
                  </div>
                </button>
                
                <button 
                  onClick={onNavigateToCompanyManagement}
                  className="w-full bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-4 text-left hover:from-green-100 hover:to-emerald-100 transition-all duration-200 transform hover:scale-[1.02] group"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
                      </svg>
                    </div>
                    <div className="flex-1">
                      <div className="text-green-700 font-semibold">Company Management</div>
                      <div className="text-green-600 text-sm">Manage companies & chart of accounts</div>
                    </div>
                  </div>
                </button>
                
                <button className="w-full bg-gradient-to-r from-purple-50 to-violet-50 border border-purple-200 rounded-xl p-4 text-left hover:from-purple-100 hover:to-violet-100 transition-all duration-200 transform hover:scale-[1.02] group">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                      </svg>
                    </div>
                    <div className="flex-1">
                      <div className="text-purple-700 font-semibold">Financial Reports</div>
                      <div className="text-purple-600 text-sm">View analytics & reports</div>
                    </div>
                  </div>
                </button>

                <button className="w-full bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-xl p-4 text-left hover:from-orange-100 hover:to-red-100 transition-all duration-200 transform hover:scale-[1.02] group">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
                      </svg>
                    </div>
                    <div className="flex-1">
                      <div className="text-orange-700 font-semibold">User Management</div>
                      <div className="text-orange-600 text-sm">Manage users & permissions</div>
                    </div>
                  </div>
                </button>
              </div>
            </div>

            {/* System Status */}
            <div className="bg-gradient-to-r from-green-500 to-emerald-500 rounded-2xl shadow-xl p-6 text-white">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                  </svg>
                </div>
                <h3 className="text-lg font-bold">System Status</h3>
              </div>
              <p className="text-green-100 text-sm mb-4">
                🎉 <strong>All Systems Operational!</strong> Your ZOIOS ERP is running smoothly with all services active.
              </p>
              <div className="flex items-center space-x-2 text-sm">
                <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                <span>Last updated: {new Date().toLocaleTimeString()}</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default SimpleDashboard;