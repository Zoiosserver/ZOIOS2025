import React, { useState, useEffect } from 'react';
import ZoiosLogo from './ZoiosLogo';

const EnhancedDashboard = ({ user, onLogout, onNavigateToCompanyManagement }) => {
  const [companySetup, setCompanySetup] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [setupProgress, setSetupProgress] = useState(0);
  const [activeModule, setActiveModule] = useState('overview');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [expandedSections, setExpandedSections] = useState({});

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

  const toggleSection = (sectionKey) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionKey]: !prev[sectionKey]
    }));
  };

  const menuSections = [
    {
      key: 'overview',
      title: 'Overview',
      icon: '📊',
      items: [
        { key: 'dashboard', label: 'Dashboard', active: true },
        { key: 'analytics', label: 'Analytics', badge: 'Soon' },
        { key: 'reports', label: 'Reports' }
      ]
    },
    {
      key: 'company',
      title: 'Company Management',
      icon: '🏢',
      items: [
        { key: 'company-overview', label: 'Company Overview' },
        { key: 'company-management', label: 'Company Management', onClick: onNavigateToCompanyManagement },
        { key: 'sister-companies', label: 'Sister Companies' },
        { key: 'user-management', label: 'User Management' }
      ]
    },
    {
      key: 'accounting',
      title: 'Accounting & Finance',
      icon: '💰',
      items: [
        { key: 'chart-accounts', label: 'Chart of Accounts' },
        { key: 'accounts-ledger', label: 'Accounts Ledger' },
        { key: 'financial-reports', label: 'Financial Reports' },
        { key: 'currency-management', label: 'Currency Management' }
      ]
    },
    {
      key: 'sales',
      title: 'Sales & CRM',
      icon: '📈',
      items: [
        { key: 'crm-dashboard', label: 'CRM Dashboard', badge: 'New' },
        { key: 'leads', label: 'Leads Management' },
        { key: 'customers', label: 'Customer Management' },
        { key: 'sales-orders', label: 'Sales Orders' },
        { key: 'invoicing', label: 'Invoicing' }
      ]
    },
    {
      key: 'purchase',
      title: 'Purchase & Procurement',
      icon: '🛒',
      items: [
        { key: 'suppliers', label: 'Supplier Management' },
        { key: 'purchase-orders', label: 'Purchase Orders' },
        { key: 'procurement', label: 'Procurement' },
        { key: 'vendor-bills', label: 'Vendor Bills' }
      ]
    },
    {
      key: 'inventory',
      title: 'Inventory Management',
      icon: '📦',
      items: [
        { key: 'inventory-overview', label: 'Inventory Overview' },
        { key: 'stock-management', label: 'Stock Management' },
        { key: 'warehouses', label: 'Warehouse Management' },
        { key: 'stock-transfers', label: 'Stock Transfers' }
      ]
    },
    {
      key: 'hr',
      title: 'Human Resources',
      icon: '👥',
      items: [
        { key: 'employees', label: 'Employee Management' },
        { key: 'payroll', label: 'Payroll' },
        { key: 'attendance', label: 'Attendance' },
        { key: 'leave-management', label: 'Leave Management' },
        { key: 'performance', label: 'Performance' }
      ]
    },
    {
      key: 'academy',
      title: 'Learning Academy',
      icon: '🎓',
      items: [
        { key: 'courses', label: 'Course Management' },
        { key: 'training', label: 'Training Programs' },
        { key: 'certifications', label: 'Certifications' },
        { key: 'knowledge-base', label: 'Knowledge Base' }
      ]
    },
    {
      key: 'communication',
      title: 'Communication',
      icon: '📧',
      items: [
        { key: 'email-center', label: 'Email Center' },
        { key: 'notifications', label: 'Notifications' },
        { key: 'announcements', label: 'Announcements' },
        { key: 'chat', label: 'Internal Chat', badge: 'Beta' }
      ]
    }
  ];

  const renderSidebarItem = (item, sectionKey) => (
    <div 
      key={item.key}
      className={`flex items-center justify-between px-3 py-2 text-sm rounded-lg cursor-pointer transition-all duration-200 ${
        item.active 
          ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg' 
          : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
      }`}
      onClick={() => {
        if (item.onClick) {
          item.onClick();
        } else {
          setActiveModule(item.key);
        }
      }}
    >
      <span className={sidebarCollapsed ? 'hidden' : ''}>{item.label}</span>
      {item.badge && !sidebarCollapsed && (
        <span className={`px-2 py-1 text-xs rounded-full ${
          item.badge === 'New' ? 'bg-green-100 text-green-800' :
          item.badge === 'Beta' ? 'bg-purple-100 text-purple-800' :
          'bg-gray-100 text-gray-600'
        }`}>
          {item.badge}
        </span>
      )}
    </div>
  );

  const renderOverviewContent = () => (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-6 border border-blue-100">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Welcome back, {user?.name || 'User'}! 👋
        </h2>
        <p className="text-gray-600">
          {companySetup ? `Managing ${companySetup.company_name}` : 'Ready to manage your business'}
        </p>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
              <span className="text-2xl">✅</span>
            </div>
          </div>
          <div className="text-2xl font-bold text-gray-900">{setupProgress}%</div>
          <div className="text-gray-600 text-sm">Setup Progress</div>
        </div>

        <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
              <span className="text-2xl">🏢</span>
            </div>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {companySetup?.business_type === 'Group Company' ? 'Group' : 'Single'}
          </div>
          <div className="text-gray-600 text-sm">Company Type</div>
        </div>

        <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
              <span className="text-2xl">💰</span>
            </div>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {companySetup?.base_currency || 'USD'}
          </div>
          <div className="text-gray-600 text-sm">Base Currency</div>
        </div>

        <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center">
              <span className="text-2xl">🌟</span>
            </div>
          </div>
          <div className="text-2xl font-bold text-gray-900">Active</div>
          <div className="text-gray-600 text-sm">System Status</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-6">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button 
            onClick={onNavigateToCompanyManagement}
            className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4 text-left hover:from-blue-100 hover:to-indigo-100 transition-all duration-200"
          >
            <div className="text-2xl mb-2">🏢</div>
            <div className="font-semibold text-blue-700">Company Management</div>
            <div className="text-blue-600 text-sm">Manage companies & accounts</div>
          </button>

          <button className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-4 text-left hover:from-green-100 hover:to-emerald-100 transition-all duration-200">
            <div className="text-2xl mb-2">📊</div>
            <div className="font-semibold text-green-700">View Reports</div>
            <div className="text-green-600 text-sm">Financial & business reports</div>
          </button>

          <button className="bg-gradient-to-r from-purple-50 to-violet-50 border border-purple-200 rounded-xl p-4 text-left hover:from-purple-100 hover:to-violet-100 transition-all duration-200">
            <div className="text-2xl mb-2">👥</div>
            <div className="font-semibold text-purple-700">Manage Users</div>
            <div className="text-purple-600 text-sm">User roles & permissions</div>
          </button>

          <button className="bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-xl p-4 text-left hover:from-orange-100 hover:to-red-100 transition-all duration-200">
            <div className="text-2xl mb-2">⚙️</div>
            <div className="font-semibold text-orange-700">Settings</div>
            <div className="text-orange-600 text-sm">System configuration</div>
          </button>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
        <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-2xl p-8 text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Top Header */}
      <div className="bg-white/80 backdrop-blur-xl border-b border-gray-200/50 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16"/>
              </svg>
            </button>
            <ZoiosLogo />
            <div className="hidden md:block">
              <h1 className="text-xl font-bold text-gray-900">ZOIOS ERP</h1>
              <p className="text-sm text-gray-600">Enterprise Resource Planning</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-right hidden sm:block">
              <div className="text-sm font-medium text-gray-900">{user?.name}</div>
              <div className="text-xs text-gray-600">{user?.email}</div>
            </div>
            <button
              onClick={onLogout}
              className="bg-gradient-to-r from-red-500 to-pink-500 text-white px-4 py-2 rounded-xl hover:from-red-600 hover:to-pink-600 transition-all duration-200 font-medium text-sm"
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      <div className="flex">
        {/* Sidebar */}
        <div className={`${sidebarCollapsed ? 'w-16' : 'w-64'} transition-all duration-300 bg-white/80 backdrop-blur-xl border-r border-gray-200/50 h-[calc(100vh-73px)] overflow-y-auto`}>
          <div className="p-4 space-y-2">
            {menuSections.map((section) => (
              <div key={section.key}>
                <div 
                  className="flex items-center justify-between px-3 py-2 text-sm font-medium text-gray-700 cursor-pointer hover:bg-gray-100 rounded-lg transition-colors"
                  onClick={() => !sidebarCollapsed && toggleSection(section.key)}
                >
                  <div className="flex items-center space-x-2">
                    <span className="text-lg">{section.icon}</span>
                    {!sidebarCollapsed && <span>{section.title}</span>}
                  </div>
                  {!sidebarCollapsed && (
                    <svg 
                      className={`w-4 h-4 transition-transform ${expandedSections[section.key] ? 'rotate-90' : ''}`} 
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7"/>
                    </svg>
                  )}
                </div>
                
                {!sidebarCollapsed && (expandedSections[section.key] || section.key === 'overview') && (
                  <div className="ml-4 space-y-1">
                    {section.items.map(item => renderSidebarItem(item, section.key))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6">
          {error && (
            <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-lg mb-6">
              <span className="text-red-700 text-sm">{error}</span>
            </div>
          )}

          {renderOverviewContent()}
        </div>
      </div>
    </div>
  );
};

export default EnhancedDashboard;