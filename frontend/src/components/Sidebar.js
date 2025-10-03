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
  User
} from 'lucide-react';
import { Button } from '@/components/ui/button';

const Sidebar = () => {
  const location = useLocation();
  
  const menuItems = [
    { path: '/', label: 'Dashboard', icon: Home },
    { path: '/contacts', label: 'Contacts', icon: Users },
    { path: '/companies', label: 'Companies', icon: Building2 },
    { path: '/call-logs', label: 'Call Logs', icon: Phone },
    { path: '/email-responses', label: 'Email Responses', icon: Mail },
  ];
  
  return (
    <div className="fixed left-0 top-0 h-full w-64 bg-white border-r border-gray-200 shadow-sm z-10">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg flex items-center justify-center">
            <BarChart3 className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-xl font-bold text-gray-900">ZOIOS</h1>
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
      
      <div className="absolute bottom-6 left-4 right-4">
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-100">
          <p className="text-sm font-medium text-blue-900 mb-1">ZOIOS CRM</p>
          <p className="text-xs text-blue-700">Track your outreach efforts and grow your business</p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
