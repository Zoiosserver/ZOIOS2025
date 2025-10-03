import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line
} from 'recharts';
import { Users, Building2, Phone, Mail, TrendingUp, Activity } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const COLORS = {
  primary: ['#3b82f6', '#1d4ed8', '#1e40af'],
  success: ['#10b981', '#059669', '#047857'],
  warning: ['#f59e0b', '#d97706', '#b45309'],
  danger: ['#ef4444', '#dc2626', '#b91c1c'],
  info: ['#06b6d4', '#0891b2', '#0e7490'],
  purple: ['#8b5cf6', '#7c3aed', '#6d28d9']
};

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [companySetup, setCompanySetup] = useState(null);
  const [sisterCompanies, setSisterCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchDashboardStats();
    fetchCompanySetup();
    fetchSisterCompanies();
  }, []);
  
  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const fetchCompanySetup = async () => {
    try {
      const response = await axios.get(`${API}/setup/company`);
      setCompanySetup(response.data);
    } catch (error) {
      console.error('Error fetching company setup:', error);
    }
  };

  const fetchSisterCompanies = async () => {
    try {
      const response = await axios.get(`${API}/company/sister-companies`);
      setSisterCompanies(response.data);
    } catch (error) {
      console.error('Error fetching sister companies:', error);
      // This might fail for non-group companies, which is expected
    }
  };
  
  if (loading) {
    return (
      <div className="space-y-6 animate-pulse" data-testid="dashboard-loading">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-gray-200 rounded-lg h-24"></div>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-gray-200 rounded-lg h-80"></div>
          ))}
        </div>
      </div>
    );
  }
  
  if (!stats) {
    return (
      <div className="flex items-center justify-center h-64" data-testid="dashboard-error">
        <p className="text-gray-500">Failed to load dashboard data</p>
      </div>
    );
  }
  
  // Prepare chart data
  const contactStatusData = stats.contact_status.map(item => ({
    name: item._id.replace('_', ' ').toUpperCase(),
    value: item.count
  }));
  
  const callDispositionData = stats.call_disposition.map(item => ({
    name: item._id.replace('_', ' ').toUpperCase(),
    value: item.count
  }));
  
  const emailStatusData = stats.email_status.map(item => ({
    name: item._id.replace('_', ' ').toUpperCase(),
    value: item.count
  }));
  
  const activityData = stats.activity_trend.map(item => ({
    date: item._id,
    contacts: item.count
  }));
  
  const statCards = [
    {
      title: 'Total Contacts',
      value: stats.totals.contacts,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      testId: 'total-contacts'
    },
    {
      title: 'Companies',
      value: stats.totals.companies,
      icon: Building2,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      testId: 'total-companies'
    },
    {
      title: 'Total Calls',
      value: stats.totals.calls,
      icon: Phone,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      testId: 'total-calls'
    },
    {
      title: 'Email Responses',
      value: stats.totals.emails,
      icon: Mail,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      testId: 'total-emails'
    }
  ];
  
  return (
    <div className="space-y-6 animate-fade-in" data-testid="dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Overview of your business operations</p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Activity className="w-4 h-4" />
          <span>Last updated: {new Date().toLocaleDateString()}</span>
        </div>
      </div>
      
      {/* Company Information */}
      {companySetup && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="w-5 h-5" />
                Company Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h3 className="font-semibold text-lg text-gray-900">{companySetup.company_name}</h3>
                  <p className="text-gray-600">{companySetup.business_type}</p>
                  <p className="text-gray-600">{companySetup.industry}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600"><strong>Base Currency:</strong> {companySetup.base_currency}</p>
                  <p className="text-sm text-gray-600"><strong>Country:</strong> {companySetup.country_code}</p>
                  {companySetup.fiscal_year_start && (
                    <p className="text-sm text-gray-600"><strong>Fiscal Year:</strong> Starts {companySetup.fiscal_year_start}</p>
                  )}
                </div>
              </div>
              
              {companySetup.address && (
                <div className="pt-2 border-t">
                  <p className="text-sm text-gray-600">
                    <strong>Address:</strong> {companySetup.address}
                    {companySetup.city && `, ${companySetup.city}`}
                    {companySetup.state && `, ${companySetup.state}`}
                    {companySetup.postal_code && ` ${companySetup.postal_code}`}
                  </p>
                </div>
              )}
              
              <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                {companySetup.phone && <span><strong>Phone:</strong> {companySetup.phone}</span>}
                {companySetup.email && <span><strong>Email:</strong> {companySetup.email}</span>}
                {companySetup.website && <span><strong>Website:</strong> {companySetup.website}</span>}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Accounting System
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <p className="text-sm font-medium text-gray-700">System</p>
                <p className="text-gray-900">{companySetup.accounting_system || 'Standard Accounting'}</p>
              </div>
              
              <div>
                <p className="text-sm font-medium text-gray-700">Multi-Currency</p>
                <p className="text-gray-900">
                  {companySetup.additional_currencies?.length > 0 ? 'Enabled' : 'Disabled'}
                </p>
                {companySetup.additional_currencies?.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs text-gray-600">Additional Currencies:</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {companySetup.additional_currencies.map(currency => (
                        <span key={currency} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                          {currency}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {companySetup.business_type === 'Group Company' && (
                <div>
                  <p className="text-sm font-medium text-gray-700">Sister Companies</p>
                  <p className="text-gray-900">{sisterCompanies.length} companies</p>
                  {sisterCompanies.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {sisterCompanies.slice(0, 3).map(company => (
                        <div key={company.id} className="text-xs text-gray-600">
                          • {company.company_name}
                        </div>
                      ))}
                      {sisterCompanies.length > 3 && (
                        <div className="text-xs text-gray-500">
                          +{sisterCompanies.length - 3} more...
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title} className="hover:shadow-md transition-shadow" data-testid={stat.testId}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">{stat.value}</p>
                  </div>
                  <div className={`${stat.bgColor} p-3 rounded-lg`}>
                    <Icon className={`w-6 h-6 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
      
      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Contact Status Distribution */}
        <Card data-testid="contact-status-chart">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              <span>Contact Status Distribution</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={contactStatusData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({name, percent}) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {contactStatusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS.primary[index % COLORS.primary.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        
        {/* Call Disposition */}
        <Card data-testid="call-disposition-chart">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Phone className="w-5 h-5 text-green-600" />
              <span>Call Outcomes</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={callDispositionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="name" 
                  tick={{fontSize: 12}}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill={COLORS.success[0]} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        
        {/* Email Status */}
        <Card data-testid="email-status-chart">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Mail className="w-5 h-5 text-purple-600" />
              <span>Email Response Status</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={emailStatusData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="name" 
                  tick={{fontSize: 12}}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill={COLORS.purple[0]} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        
        {/* Activity Trend */}
        <Card data-testid="activity-trend-chart">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-orange-600" />
              <span>Contacts Added (Last 30 Days)</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={activityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tick={{fontSize: 12}}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis />
                <Tooltip labelFormatter={(value) => `Date: ${value}`} />
                <Line 
                  type="monotone" 
                  dataKey="contacts" 
                  stroke={COLORS.info[0]} 
                  strokeWidth={3}
                  dot={{ fill: COLORS.info[0], r: 4 }}
                  activeDot={{ r: 6, fill: COLORS.info[1] }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
