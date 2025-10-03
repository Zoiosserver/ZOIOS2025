import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { usePermissions } from '../hooks/usePermissions';
import { 
  BarChart3, 
  Users, 
  Building2, 
  Building,
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
  const { permissions, hasPermission, hasAnyPermission } = usePermissions();
  const [companySetup, setCompanySetup] = React.useState(null);
  const [crmMenuOpen, setCrmMenuOpen] = React.useState(
    ['/contacts', '/companies', '/call-logs', '/email-responses'].includes(location.pathname)
  );
  const [companyMenuOpen, setCompanyMenuOpen] = React.useState(
    ['/currency', '/consolidated-accounts', '/company-accounts', '/users', '/user-assignments'].includes(location.pathname)
  );
  
  React.useEffect(() => {
    const fetchCompanySetup = async () => {
      try {
        const BACKEND_URL = window.location.origin.replace(':3000', '');
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
  
  // Build Company submenu items with dynamic currency icon
  const getCurrencyIcon = () => {
    const currencyIcons = {
      'INR': () => <span className="w-5 h-5 flex items-center justify-center text-base">₹</span>,
      'USD': DollarSign,
      'EUR': () => <span className="w-5 h-5 flex items-center justify-center text-base">€</span>,
      'GBP': () => <span className="w-5 h-5 flex items-center justify-center text-base">£</span>,
      'JPY': () => <span className="w-5 h-5 flex items-center justify-center text-base">¥</span>,
      'CNY': () => <span className="w-5 h-5 flex items-center justify-center text-base">¥</span>
    };
    
    return currencyIcons[companySetup?.base_currency] || DollarSign;
  };

  const companySubmenuItems = [];

  // Add currency management if user has permission
  if (hasPermission('currency_management')) {
    companySubmenuItems.push({
      path: '/currency',
      label: 'Currency Management',
      icon: getCurrencyIcon()
    });
  }

  // Add group company specific items if user has permissions
  if (companySetup && companySetup.business_type === 'Group Company') {
    if (hasPermission('consolidated_accounts')) {
      companySubmenuItems.push({
        path: '/consolidated-accounts',
        label: 'Consolidated Accounts',
        icon: FileText
      });
    }
    if (hasPermission('company_accounts')) {
      companySubmenuItems.push({
        path: '/company-accounts',
        label: 'Company Accounts',
        icon: Building
      });
    }
  }

  // Add admin-only company items if user has permissions
  if (hasPermission('user_management')) {
    companySubmenuItems.push({
      path: '/users',
      label: 'User Management',
      icon: Shield
    });
  }
  if (hasPermission('company_assignments')) {
    companySubmenuItems.push({
      path: '/user-assignments',
      label: 'Company Assignments',
      icon: Users
    });
  }

  // Build CRM submenu items based on permissions
  const crmSubmenuItems = [];
  if (hasPermission('crm_contacts')) {
    crmSubmenuItems.push({ path: '/contacts', label: 'Contacts', icon: Users });
  }
  if (hasPermission('crm_companies')) {
    crmSubmenuItems.push({ path: '/companies', label: 'Companies', icon: Building2 });
  }
  if (hasPermission('crm_call_logs')) {
    crmSubmenuItems.push({ path: '/call-logs', label: 'Call Logs', icon: Phone });
  }
  if (hasPermission('crm_email_responses')) {
    crmSubmenuItems.push({ path: '/email-responses', label: 'Email Responses', icon: Mail });
  }

  const menuItems = [];

  // Add Dashboard if user has permission
  if (hasPermission('dashboard')) {
    menuItems.push({ path: '/', label: 'Dashboard', icon: Home });
  }

  // Add CRM menu if user has any CRM permissions
  if (crmSubmenuItems.length > 0) {
    menuItems.push({ 
      label: 'CRM', 
      icon: BarChart3, 
      isSubmenu: true,
      submenuItems: crmSubmenuItems
    });
  }

  // Add Company menu if user has any company permissions
  if (companySubmenuItems.length > 0) {
    menuItems.push({ 
      label: 'Company', 
      icon: Building, 
      isSubmenu: true,
      submenuItems: companySubmenuItems
    });
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
            if (item.isSubmenu) {
              // Handle submenu items (CRM, Company, etc.)
              const isAnySubmenuActive = item.submenuItems.some(subItem => location.pathname === subItem.path);
              const Icon = item.icon;
              
              // Determine which submenu state to use
              const isMenuOpen = item.label === 'CRM' ? crmMenuOpen : companyMenuOpen;
              const toggleMenu = item.label === 'CRM' 
                ? () => setCrmMenuOpen(!crmMenuOpen)
                : () => setCompanyMenuOpen(!companyMenuOpen);
              
              return (
                <li key={item.label}>
                  <button
                    onClick={toggleMenu}
                    className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                      isAnySubmenuActive
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <Icon className={`w-5 h-5 ${isAnySubmenuActive ? 'text-blue-700' : 'text-gray-500'}`} />
                      <span>{item.label}</span>
                    </div>
                    {isMenuOpen ? (
                      <ChevronDown className="w-4 h-4" />
                    ) : (
                      <ChevronRight className="w-4 h-4" />
                    )}
                  </button>
                  
                  {/* Submenu items */}
                  {isMenuOpen && (
                    <ul className="mt-1 space-y-1 ml-8">
                      {item.submenuItems.map((subItem) => {
                        const isActive = location.pathname === subItem.path;
                        const SubIcon = subItem.icon;
                        
                        return (
                          <li key={subItem.path}>
                            <Link
                              to={subItem.path}
                              className={`flex items-center space-x-3 px-3 py-2 rounded-lg text-sm transition-all duration-200 ${
                                isActive
                                  ? 'bg-blue-100 text-blue-700 border-r-2 border-blue-700'
                                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                              }`}
                              data-testid={`nav-${subItem.label.toLowerCase().replace(' ', '-')}`}
                            >
                              <SubIcon className={`w-4 h-4 ${isActive ? 'text-blue-700' : 'text-gray-400'}`} />
                              <span>{subItem.label}</span>
                            </Link>
                          </li>
                        );
                      })}
                    </ul>
                  )}
                </li>
              );
            } else {
              // Handle regular menu items
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
            }
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
