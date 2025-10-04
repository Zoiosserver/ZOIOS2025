import React, { useState, useEffect } from 'react';
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import ZoiosLogo from './ZoiosLogo';

const ProfessionalDashboard = ({ user, onLogout, onNavigateToCompanyManagement }) => {
  const [companySetup, setCompanySetup] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeModule, setActiveModule] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [expandedSections, setExpandedSections] = useState({ overview: true }); // Start with overview expanded
  const [dashboardData, setDashboardData] = useState({});

  // Mock business intelligence data
  const revenueData = [
    { month: 'Jan', revenue: 65000, expense: 45000, profit: 20000 },
    { month: 'Feb', revenue: 72000, expense: 48000, profit: 24000 },
    { month: 'Mar', revenue: 68000, expense: 52000, profit: 16000 },
    { month: 'Apr', revenue: 78000, expense: 55000, profit: 23000 },
    { month: 'May', revenue: 85000, expense: 58000, profit: 27000 },
    { month: 'Jun', revenue: 92000, expense: 62000, profit: 30000 },
  ];

  const expenseBreakdown = [
    { name: 'Operations', value: 35, amount: 21700 },
    { name: 'Marketing', value: 25, amount: 15500 },
    { name: 'HR & Payroll', value: 20, amount: 12400 },
    { name: 'Technology', value: 12, amount: 7440 },
    { name: 'Administration', value: 8, amount: 4960 },
  ];

  const accountsData = [
    { category: 'Assets', current: 245000, previous: 220000 },
    { category: 'Liabilities', current: 89000, previous: 95000 },
    { category: 'Equity', current: 156000, previous: 125000 },
    { category: 'Revenue', current: 92000, previous: 85000 },
    { category: 'Expenses', current: 62000, previous: 58000 },
  ];

  const kpiData = [
    { title: 'Total Revenue', value: 462000, change: 8.2, trend: 'up', color: 'green' },
    { title: 'Net Profit', value: 140000, change: 12.5, trend: 'up', color: 'blue' },
    { title: 'Total Assets', value: 245000, change: 11.4, trend: 'up', color: 'purple' },
    { title: 'Cash Flow', value: 45000, change: -2.1, trend: 'down', color: 'orange' },
  ];

  const salesData = [
    { week: 'W1', sales: 12000, target: 15000 },
    { week: 'W2', sales: 18000, target: 15000 },
    { week: 'W3', sales: 14000, target: 15000 },
    { week: 'W4', sales: 22000, target: 15000 },
  ];

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const backendUrl = window.location.origin;
      
      // Fetch business intelligence data
      const biResponse = await fetch(`${backendUrl}/api/dashboard/business-intelligence`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (biResponse.ok) {
        const biData = await biResponse.json();
        const businessData = biData.data;
        
        // Update all dashboard data with real values from API
        setDashboardData({
          currency: businessData.company_overview.primary_currency || 'USD',
          companyName: businessData.company_overview.company_name || 'Your Company',
          businessType: 'Enterprise'
        });
        
        // Update KPI data
        kpiData.splice(0, kpiData.length, ...businessData.kpis.map(kpi => ({
          ...kpi,
          change: parseFloat(kpi.change.toFixed(1))
        })));
        
        // Update revenue data
        revenueData.splice(0, revenueData.length, ...businessData.revenue_trend);
        
        // Update expense breakdown
        expenseBreakdown.splice(0, expenseBreakdown.length, ...businessData.expense_breakdown.map(item => ({
          name: item.name,
          value: item.percentage,
          amount: item.amount
        })));
        
        // Update accounts data
        accountsData.splice(0, accountsData.length, ...businessData.account_distribution.map(item => ({
          category: item.category,
          current: item.current,
          previous: Math.round(item.current * 0.9) // Mock previous value
        })));
        
        setCompanySetup({
          company_name: businessData.company_overview.company_name,
          base_currency: businessData.company_overview.primary_currency,
          business_type: businessData.company_overview.total_companies > 1 ? 'Group Company' : 'Single Company'
        });
        
      } else {
        // Fallback to company setup data only
        const companyResponse = await fetch(`${backendUrl}/api/setup/company`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });

        if (companyResponse.ok) {
          const data = await companyResponse.json();
          setCompanySetup(data);
          setDashboardData({
            currency: data.base_currency || 'USD',
            companyName: data.company_name || 'Your Company',
            businessType: data.business_type || 'Business'
          });
        }
      }
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      // Set default values on error
      setDashboardData({
        currency: 'USD',
        companyName: 'Demo Company',
        businessType: 'Business'
      });
    } finally {
      setLoading(false);
    }
  };

  const toggleSection = (sectionKey) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionKey]: !prev[sectionKey]
    }));
  };

  const formatCurrency = (amount) => {
    const symbol = dashboardData.currency === 'INR' ? '₹' : dashboardData.currency === 'EUR' ? '€' : '$';
    return `${symbol}${amount.toLocaleString()}`;
  };

  const menuSections = [
    {
      key: 'overview',
      title: 'Overview',
      icon: '📊',
      items: [
        { key: 'dashboard', label: 'Dashboard', active: true },
        { key: 'analytics', label: 'Analytics', badge: 'Pro' },
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
        { key: 'accounts-ledger', label: 'General Ledger' },
        { key: 'financial-reports', label: 'Financial Reports' },
        { key: 'currency-management', label: 'Multi-Currency' }
      ]
    },
    {
      key: 'projects',
      title: 'Project Management',
      icon: '🏗️',
      items: [
        { key: 'project-dashboard', label: 'Project Dashboard' },
        { key: 'elevator-installation', label: 'Elevator Installation', badge: 'New' },
        { key: 'elevator-maintenance', label: 'Elevator Maintenance' },
        { key: 'project-planning', label: 'Project Planning' },
        { key: 'resource-allocation', label: 'Resource Allocation' }
      ]
    },
    {
      key: 'sales',
      title: 'Sales & CRM',
      icon: '📈',
      items: [
        { key: 'crm-dashboard', label: 'CRM Dashboard', badge: 'Enhanced' },
        { key: 'leads', label: 'Lead Management' },
        { key: 'opportunities', label: 'Opportunities' },
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
        { key: 'rfq', label: 'RFQ Management' },
        { key: 'vendor-bills', label: 'Vendor Bills' }
      ]
    },
    {
      key: 'manufacturing',
      title: 'Manufacturing',
      icon: '🏭',
      items: [
        { key: 'production-planning', label: 'Production Planning' },
        { key: 'work-orders', label: 'Work Orders' },
        { key: 'quality-control', label: 'Quality Control' },
        { key: 'equipment-management', label: 'Equipment Management' },
        { key: 'production-reports', label: 'Production Reports' }
      ]
    },
    {
      key: 'inventory',
      title: 'Inventory Management',
      icon: '📦',
      items: [
        { key: 'inventory-overview', label: 'Stock Overview' },
        { key: 'products', label: 'Product Catalog' },
        { key: 'warehouses', label: 'Warehouse Management' },
        { key: 'stock-movements', label: 'Stock Movements' }
      ]
    },
    {
      key: 'hr',
      title: 'Human Resources',
      icon: '👥',
      items: [
        { key: 'employees', label: 'Employee Management' },
        { key: 'employee-checkin', label: 'Employee Check-In/Out', badge: 'New' },
        { key: 'payroll', label: 'Payroll Processing' },
        { key: 'attendance', label: 'Time & Attendance' },
        { key: 'performance', label: 'Performance Management' }
      ]
    },
    {
      key: 'academy',
      title: 'Learning Academy',
      icon: '🎓',
      items: [
        { key: 'courses', label: 'Course Library' },
        { key: 'students-data', label: 'Students Data', badge: 'New' },
        { key: 'training', label: 'Training Programs' },
        { key: 'certifications', label: 'Certifications' },
        { key: 'knowledge-base', label: 'Knowledge Base' }
      ]
    }
  ];

  const renderKPICard = (kpi, index) => (
    <div key={index} className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6 hover:shadow-2xl transition-all duration-300">
      <div className="flex items-center justify-between mb-4">
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
          kpi.color === 'green' ? 'bg-green-500' :
          kpi.color === 'blue' ? 'bg-blue-500' :
          kpi.color === 'purple' ? 'bg-purple-500' :
          'bg-orange-500'
        }`}>
          <span className="text-white text-xl">
            {kpi.color === 'green' ? '💰' : kpi.color === 'blue' ? '📊' : kpi.color === 'purple' ? '🏦' : '💸'}
          </span>
        </div>
        <div className={`flex items-center px-2 py-1 rounded-full text-xs font-medium ${
          kpi.trend === 'up' 
            ? 'bg-green-100 text-green-800' 
            : 'bg-red-100 text-red-800'
        }`}>
          <span className="mr-1">{kpi.trend === 'up' ? '↗️' : '↘️'}</span>
          {Math.abs(kpi.change)}%
        </div>
      </div>
      <div className="text-3xl font-bold text-gray-900 mb-1">
        {formatCurrency(kpi.value)}
      </div>
      <div className="text-gray-600 text-sm font-medium">{kpi.title}</div>
      <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
        <div 
          className={`h-2 rounded-full ${
            kpi.color === 'green' ? 'bg-green-500' :
            kpi.color === 'blue' ? 'bg-blue-500' :
            kpi.color === 'purple' ? 'bg-purple-500' :
            'bg-orange-500'
          }`}
          style={{ width: `${Math.min(Math.abs(kpi.change) * 10, 100)}%` }}
        ></div>
      </div>
    </div>
  );

  const handleModuleNavigation = (moduleKey) => {
    if (moduleKey === 'company-management') {
      onNavigateToCompanyManagement();
      return;
    }
    setActiveModule(moduleKey);
  };

  const renderModuleContent = () => {
    switch (activeModule) {
      case 'dashboard':
        return renderOverviewContent();
      case 'analytics':
        return renderAnalyticsContent();
      case 'reports':
        return renderReportsContent();
      case 'company-overview':
        return renderCompanyOverviewContent();
      case 'sister-companies':
        return renderSisterCompaniesContent();
      case 'user-management':
        return renderUserManagementContent();
      case 'chart-accounts':
        return renderChartAccountsContent();
      case 'accounts-ledger':
        return renderAccountsLedgerContent();
      case 'financial-reports':
        return renderFinancialReportsContent();
      case 'currency-management':
        return renderCurrencyManagementContent();
      case 'crm-dashboard':
        return renderCRMDashboardContent();
      case 'leads':
        return renderLeadsContent();
      default:
        return renderComingSoonContent(activeModule);
    }
  };

  const renderComingSoonContent = (moduleName) => (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="text-center">
        <div className="text-6xl mb-4">🚀</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Coming Soon</h2>
        <p className="text-gray-600 mb-4">The {moduleName.replace('-', ' ')} module is under development</p>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-md mx-auto">
          <p className="text-blue-800 text-sm">
            This feature will be available in the next update. We're working hard to bring you the best ERP experience.
          </p>
        </div>
      </div>
    </div>
  );

  const renderAnalyticsContent = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Advanced Analytics</h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
          <h3 className="text-lg font-semibold mb-4">Revenue Analytics</h3>
          <p className="text-gray-600">Detailed revenue analysis and forecasting tools will be available here.</p>
        </div>
        <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
          <h3 className="text-lg font-semibold mb-4">Performance Metrics</h3>
          <p className="text-gray-600">KPI tracking and performance measurement tools coming soon.</p>
        </div>
      </div>
    </div>
  );

  const renderReportsContent = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Financial Reports</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {['Profit & Loss', 'Balance Sheet', 'Cash Flow', 'Trial Balance', 'General Ledger', 'Aged Receivables'].map((report) => (
          <div key={report} className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6 hover:shadow-2xl transition-all duration-200 cursor-pointer">
            <h3 className="text-lg font-semibold mb-2">{report}</h3>
            <p className="text-gray-600 text-sm mb-4">Generate {report.toLowerCase()} report</p>
            <button className="w-full bg-gradient-to-r from-blue-500 to-indigo-500 text-white py-2 px-4 rounded-lg hover:from-blue-600 hover:to-indigo-600 transition-all duration-200">
              Generate Report
            </button>
          </div>
        ))}
      </div>
    </div>
  );

  const renderCompanyOverviewContent = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Company Overview</h2>
      <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold mb-4">Company Information</h3>
            <div className="space-y-3">
              <div><span className="font-medium">Name:</span> {dashboardData.companyName}</div>
              <div><span className="font-medium">Type:</span> {dashboardData.businessType}</div>
              <div><span className="font-medium">Currency:</span> {dashboardData.currency}</div>
              <div><span className="font-medium">Status:</span> <span className="text-green-600">Active</span></div>
            </div>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-4">Quick Stats</h3>
            <div className="space-y-3">
              <div><span className="font-medium">Users:</span> 1</div>
              <div><span className="font-medium">Modules:</span> 9</div>
              <div><span className="font-medium">Setup:</span> <span className="text-green-600">Complete</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSisterCompaniesContent = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Sister Companies</h2>
        <button className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white px-4 py-2 rounded-xl hover:from-blue-600 hover:to-indigo-600 transition-all duration-200">
          Add Sister Company
        </button>
      </div>
      <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-8 text-center">
        <div className="text-4xl mb-4">🏢</div>
        <h3 className="text-xl font-semibold mb-2">No Sister Companies Found</h3>
        <p className="text-gray-600 mb-4">Create sister companies to manage multiple entities under one group.</p>
        <button className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-6 py-3 rounded-xl hover:from-green-600 hover:to-emerald-600 transition-all duration-200">
          Create Sister Company
        </button>
      </div>
    </div>
  );

  const renderUserManagementContent = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">User Management</h2>
        <button className="bg-gradient-to-r from-purple-500 to-violet-500 text-white px-4 py-2 rounded-xl hover:from-purple-600 hover:to-violet-600 transition-all duration-200">
          Add User
        </button>
      </div>
      <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 overflow-hidden">
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Current Users</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium text-sm">
                  {user?.name?.charAt(0) || 'U'}
                </div>
                <div>
                  <div className="font-medium">{user?.name}</div>
                  <div className="text-sm text-gray-600">{user?.email}</div>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">Admin</span>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">Active</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderChartAccountsContent = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Chart of Accounts</h2>
        <button 
          onClick={onNavigateToCompanyManagement}
          className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-4 py-2 rounded-xl hover:from-green-600 hover:to-emerald-600 transition-all duration-200"
        >
          Manage Accounts
        </button>
      </div>
      <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
        <p className="text-gray-600 mb-4">
          Access the full chart of accounts management through the Company Management section.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
          {['Assets', 'Liabilities', 'Equity', 'Revenue', 'Expenses'].map((type, index) => (
            <div key={type} className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{[8, 5, 3, 4, 7][index]}</div>
              <div className="text-sm text-gray-600">{type}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderAccountsLedgerContent = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">General Ledger</h2>
      <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
        <p className="text-gray-600">General ledger functionality coming soon. This will include transaction history, account balances, and detailed financial records.</p>
      </div>
    </div>
  );

  const renderFinancialReportsContent = () => renderReportsContent();

  const renderCurrencyManagementContent = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Currency Management</h2>
      <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold mb-4">Base Currency</h3>
            <div className="text-2xl font-bold text-blue-600">{dashboardData.currency}</div>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-4">Exchange Rates</h3>
            <p className="text-gray-600">Multi-currency support and exchange rate management coming soon.</p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCRMDashboardContent = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">CRM Dashboard</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { title: 'Total Leads', value: 156, color: 'blue' },
          { title: 'Qualified Leads', value: 42, color: 'green' },
          { title: 'Active Customers', value: 78, color: 'purple' },
          { title: 'Conversion Rate', value: '27%', color: 'orange' }
        ].map((metric, index) => (
          <div key={index} className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
            <div className="text-2xl font-bold text-gray-900">{metric.value}</div>
            <div className="text-gray-600 text-sm">{metric.title}</div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderLeadsContent = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Lead Management</h2>
        <button className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white px-4 py-2 rounded-xl hover:from-blue-600 hover:to-indigo-600 transition-all duration-200">
          Add Lead
        </button>
      </div>
      <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-8 text-center">
        <div className="text-4xl mb-4">📈</div>
        <h3 className="text-xl font-semibold mb-2">Lead Management System</h3>
        <p className="text-gray-600">Comprehensive lead tracking and conversion tools coming soon.</p>
      </div>
    </div>
  );

  const renderOverviewContent = () => (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-blue-600 rounded-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              Welcome back, {user?.name || 'User'}! 👋
            </h1>
            <p className="text-blue-100 text-lg">
              {dashboardData.companyName} • {dashboardData.businessType}
            </p>
            <p className="text-blue-200 text-sm mt-1">
              Today is {new Date().toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </p>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold">{formatCurrency(462000)}</div>
            <div className="text-blue-200">Total Revenue YTD</div>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpiData.map((kpi, index) => renderKPICard(kpi, index))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Trend */}
        <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-gray-900">Revenue & Profit Trend</h3>
            <div className="flex space-x-2">
              <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">Revenue</span>
              <span className="px-3 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">Profit</span>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={revenueData}>
              <defs>
                <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1}/>
                </linearGradient>
                <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10B981" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#10B981" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" tick={{fontSize: 12}} />
              <YAxis tick={{fontSize: 12}} />
              <Tooltip 
                formatter={(value) => formatCurrency(value)}
                labelStyle={{ color: '#374151' }}
                contentStyle={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.95)', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px'
                }}
              />
              <Area type="monotone" dataKey="revenue" stroke="#3B82F6" fillOpacity={1} fill="url(#colorRevenue)" strokeWidth={3} />
              <Area type="monotone" dataKey="profit" stroke="#10B981" fillOpacity={1} fill="url(#colorProfit)" strokeWidth={3} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Expense Breakdown */}
        <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-6">Expense Breakdown</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={expenseBreakdown}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={120}
                paddingAngle={5}
                dataKey="value"
              >
                {expenseBreakdown.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value, name, props) => [
                  `${value}% (${formatCurrency(props.payload.amount)})`, 
                  props.payload.name
                ]}
              />
              <Legend 
                verticalAlign="bottom" 
                height={36}
                formatter={(value, entry) => (
                  <span style={{ color: entry.color, fontWeight: 'medium' }}>
                    {entry.payload.name} ({entry.payload.value}%)
                  </span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Additional Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Accounts Overview */}
        <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-6">Chart of Accounts Overview</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={accountsData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="category" tick={{fontSize: 12}} />
              <YAxis tick={{fontSize: 12}} />
              <Tooltip 
                formatter={(value) => formatCurrency(value)}
                contentStyle={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.95)', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Bar dataKey="current" fill="#3B82F6" name="Current Period" radius={[4, 4, 0, 0]} />
              <Bar dataKey="previous" fill="#93C5FD" name="Previous Period" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Sales Performance */}
        <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-6">Sales vs Target</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={salesData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="week" tick={{fontSize: 12}} />
              <YAxis tick={{fontSize: 12}} />
              <Tooltip 
                formatter={(value) => formatCurrency(value)}
                contentStyle={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.95)', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Line type="monotone" dataKey="sales" stroke="#10B981" strokeWidth={3} name="Actual Sales" />
              <Line type="monotone" dataKey="target" stroke="#F59E0B" strokeWidth={2} strokeDasharray="5 5" name="Target" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-6">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button 
            onClick={onNavigateToCompanyManagement}
            className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4 text-left hover:from-blue-100 hover:to-indigo-100 transition-all duration-200 group"
          >
            <div className="text-3xl mb-3 group-hover:scale-110 transition-transform">🏢</div>
            <div className="font-semibold text-blue-700">Company Management</div>
            <div className="text-blue-600 text-sm">Manage companies & accounts</div>
          </button>

          <button className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-4 text-left hover:from-green-100 hover:to-emerald-100 transition-all duration-200 group">
            <div className="text-3xl mb-3 group-hover:scale-110 transition-transform">📊</div>
            <div className="font-semibold text-green-700">Financial Reports</div>
            <div className="text-green-600 text-sm">P&L, Balance Sheet, Cash Flow</div>
          </button>

          <button className="bg-gradient-to-r from-purple-50 to-violet-50 border border-purple-200 rounded-xl p-4 text-left hover:from-purple-100 hover:to-violet-100 transition-all duration-200 group">
            <div className="text-3xl mb-3 group-hover:scale-110 transition-transform">👥</div>
            <div className="font-semibold text-purple-700">CRM Dashboard</div>
            <div className="text-purple-600 text-sm">Leads, customers, pipeline</div>
          </button>

          <button className="bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-xl p-4 text-left hover:from-orange-100 hover:to-red-100 transition-all duration-200 group">
            <div className="text-3xl mb-3 group-hover:scale-110 transition-transform">📦</div>
            <div className="font-semibold text-orange-700">Inventory Control</div>
            <div className="text-orange-600 text-sm">Stock levels & movements</div>
          </button>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
        <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-2xl p-8 text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading business intelligence...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Top Header */}
      <div className="bg-white/90 backdrop-blur-xl border-b border-gray-200/50 px-6 py-4 sticky top-0 z-50">
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
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">ZOIOS ERP</h1>
              <p className="text-sm text-gray-600">Business Intelligence Dashboard</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-right hidden sm:block">
              <div className="text-sm font-medium text-gray-900">{user?.name}</div>
              <div className="text-xs text-gray-600">{user?.role?.toUpperCase()}</div>
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
        <div className={`${sidebarCollapsed ? 'w-16' : 'w-72'} transition-all duration-300 bg-white/90 backdrop-blur-xl border-r border-gray-200/50 h-[calc(100vh-73px)] overflow-y-auto`}>
          <div className="p-4 space-y-2">
            {menuSections.map((section) => (
              <div key={section.key}>
                <div 
                  className="flex items-center justify-between px-3 py-3 text-sm font-medium text-gray-700 cursor-pointer hover:bg-gray-100 rounded-lg transition-colors"
                  onClick={() => !sidebarCollapsed && toggleSection(section.key)}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-xl">{section.icon}</span>
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
                    {section.items.map(item => (
                      <div 
                        key={item.key}
                        className={`flex items-center justify-between px-3 py-2 text-sm rounded-lg cursor-pointer transition-all duration-200 ${
                          item.key === activeModule || item.active 
                            ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg' 
                            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                        }`}
                        onClick={() => {
                          if (item.onClick) {
                            item.onClick();
                          } else {
                            handleModuleNavigation(item.key);
                          }
                        }}
                      >
                        <span>{item.label}</span>
                        {item.badge && (
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            item.badge === 'New' ? 'bg-green-100 text-green-800' :
                            item.badge === 'Pro' ? 'bg-purple-100 text-purple-800' :
                            item.badge === 'Beta' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-600'
                          }`}>
                            {item.badge}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6 overflow-y-auto h-[calc(100vh-73px)]">
          {error && (
            <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-lg mb-6">
              <span className="text-red-700 text-sm">{error}</span>
            </div>
          )}

          {renderModuleContent()}
        </div>
      </div>
    </div>
  );
};

export default ProfessionalDashboard;