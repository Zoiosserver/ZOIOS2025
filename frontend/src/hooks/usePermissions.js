import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

export const usePermissions = () => {
  const { user } = useAuth();
  const [permissions, setPermissions] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      // Get permissions from user object
      const userPermissions = user.permissions || {};
      
      // Set default permissions for admin users
      const defaultPermissions = {
        dashboard: true,
        crm_contacts: true,
        crm_companies: true,
        crm_call_logs: true,
        crm_email_responses: true,
        currency_management: true,
        consolidated_accounts: true,
        company_accounts: true,
        user_management: user.role === 'admin',
        company_assignments: user.role === 'admin'
      };

      // Merge user permissions with defaults (user permissions take priority)
      const finalPermissions = { ...defaultPermissions, ...userPermissions };
      
      setPermissions(finalPermissions);
      setLoading(false);
    } else {
      setPermissions({});
      setLoading(false);
    }
  }, [user]);

  // Check if user has permission for a specific menu
  const hasPermission = (permissionKey) => {
    // Admin users have all permissions by default
    if (user?.role === 'admin' && !permissions.hasOwnProperty(permissionKey)) {
      return true;
    }
    return permissions[permissionKey] === true;
  };

  // Check if user has permission for any of the given permissions
  const hasAnyPermission = (permissionKeys) => {
    return permissionKeys.some(key => hasPermission(key));
  };

  return {
    permissions,
    hasPermission,
    hasAnyPermission,
    loading
  };
};