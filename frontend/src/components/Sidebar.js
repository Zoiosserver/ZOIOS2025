import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  BarChart3, 
  Users, 
  Building2, 
  Phone, 
  Mail,
  Home,
  Settings,
  LogOut,
  Shield,
  User,
  DollarSign,
  FileText,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import { Button } from '@/components/ui/button';

const Sidebar = () => {
  const location = useLocation();
  const { user, logout, isAdmin } = useAuth();
  const [companySetup, setCompanySetup] = React.useState(null);
  const [crmMenuOpen, setCrmMenuOpen] = React.useState(
    ['/contacts', '/companies', '/call-logs', '/email-responses'].includes(location.pathname)
  );
  
  React.useEffect(() => {
    const fetchCompanySetup = async () => {
      try {
        const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
        const response = await fetch(`${BACKEND_URL}/api/setup/company`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        if (response.ok) {
          const data = await response.json();
          setCompanySetup(data);
        }
      } catch (error) {
        console.error('Error fetching company setup:', error);
      }
    };

    if (user && user.onboarding_completed) {
      fetchCompanySetup();
    }
  }, [user]);
  
  const menuItems = [
    { path: '/', label: 'Dashboard', icon: Home },
    { 
      label: 'CRM', 
      icon: BarChart3, 
      isSubmenu: true,
      submenuItems: [
        { path: '/contacts', label: 'Contacts', icon: Users },
        { path: '/companies', label: 'Companies', icon: Building2 },
        { path: '/call-logs', label: 'Call Logs', icon: Phone },
        { path: '/email-responses', label: 'Email Responses', icon: Mail },
      ]
    },
    { path: '/currency', label: 'Currency Management', icon: DollarSign },
  ];

  // Add consolidated accounts for group companies
  if (companySetup && companySetup.business_type === 'Group Company') {
    menuItems.push({ path: '/consolidated-accounts', label: 'Consolidated Accounts', icon: FileText });
  }

  // Add admin-only menu items
  if (isAdmin()) {
    menuItems.push({ path: '/users', label: 'User Management', icon: Shield });
  }
  
  return (
    <div className="fixed left-0 top-0 h-full w-64 bg-white border-r border-gray-200 shadow-sm z-10">
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-center">
          <img 
            src="https://customer-assets.emergentagent.com/job_outreach-pulse-3/artifacts/5adajuhk_Zoios.png" 
            alt="ZOIOS Logo" 
            className="object-contain"
            style={{width: '150px', height: '150px'}}
          />
        </div>
      </div>
      
      <nav className="mt-6">
        <ul className="space-y-1 px-4">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path;
            const Icon = item.icon;
            
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                      : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                  data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
                >
                  <Icon className={`w-5 h-5 ${isActive ? 'text-blue-700' : 'text-gray-500'}`} />
                  <span>{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
      
      <div className="absolute bottom-6 left-4 right-4 space-y-4">
        {/* User Info */}
        <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg ${user?.role === 'admin' ? 'bg-purple-100' : 'bg-blue-100'}`}>
              {user?.role === 'admin' ? (
                <Shield className="w-4 h-4 text-purple-600" />
              ) : (
                <User className="w-4 h-4 text-blue-600" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{user?.name}</p>
              <p className="text-xs text-gray-600 truncate">{user?.email}</p>
            </div>
          </div>
          <Button
            onClick={logout}
            variant="outline"
            size="sm"
            className="w-full mt-3 text-xs"
            data-testid="logout-btn"
          >
            <LogOut className="w-3 h-3 mr-1" />
            Logout
          </Button>
        </div>

        {/* Brand Info */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-100">
          <p className="text-sm font-medium text-blue-900 mb-1">ZOIOS ERP</p>
          <p className="text-xs text-blue-700">Streamline your business operations and grow efficiently</p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
