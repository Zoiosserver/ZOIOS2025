import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Users, 
  RefreshCw, 
  Shield,
  Eye,
  Edit,
  Info,
  Building,
  Mail,
  Trash2,
  Settings,
  Check,
  X
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = window.location.origin.replace(':3000', '');
const API = `${BACKEND_URL}/api`;

const UserAssignments = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [userAssignments, setUserAssignments] = useState(null);
  const [updatingRole, setUpdatingRole] = useState(null);
  const [editingPermissions, setEditingPermissions] = useState(null);
  const [tempPermissions, setTempPermissions] = useState({});

  useEffect(() => {
    fetchUserAssignments();
  }, []);

  const fetchUserAssignments = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/users/company-assignments`);
      setUserAssignments(response.data);
    } catch (error) {
      console.error('Error fetching user assignments:', error);
      if (error.response?.status === 403) {
        toast.error('Access denied. Admin role required.');
      } else {
        toast.error('Failed to load user assignments');
      }
    } finally {
      setLoading(false);
    }
  };

  const updateUserRole = async (userId, newRole) => {
    try {
      setUpdatingRole(userId);
      await axios.post(`${API}/users/${userId}/role`, { role: newRole });
      toast.success('User role updated successfully');
      fetchUserAssignments();
    } catch (error) {
      console.error('Error updating user role:', error);
      toast.error('Failed to update user role');
    } finally {
      setUpdatingRole(null);
    }
  };

  const deleteUser = async (userId, userEmail) => {
    if (userEmail === 'admin@2mholding.com') {
      toast.error('Cannot delete super admin user');
      return;
    }
    
    if (window.confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      try {
        await axios.delete(`${API}/users/${userId}`);
        toast.success('User deleted successfully');
        fetchUserAssignments();
      } catch (error) {
        console.error('Error deleting user:', error);
        toast.error(error.response?.data?.detail || 'Failed to delete user');
      }
    }
  };

  const updateUserPermissions = async (userId, permissions) => {
    try {
      await axios.post(`${API}/users/${userId}/permissions`, { permissions });
      toast.success('User permissions updated successfully');
      fetchUserAssignments();
      setEditingPermissions(null);
    } catch (error) {
      console.error('Error updating permissions:', error);
      toast.error('Failed to update permissions');
    }
  };

  const handlePermissionToggle = (permission, value) => {
    setTempPermissions(prev => ({
      ...prev,
      [permission]: value
    }));
  };

  const startEditingPermissions = (userId, currentPermissions) => {
    setEditingPermissions(userId);
    setTempPermissions(currentPermissions || {});
  };

  const getRoleBadgeColor = (role) => {
    switch (role.toLowerCase()) {
      case 'admin': return 'bg-red-100 text-red-800 border-red-200';
      case 'user': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'viewer': return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getRoleIcon = (role) => {
    switch (role.toLowerCase()) {
      case 'admin': return <Shield className="w-4 h-4" />;
      case 'user': return <Edit className="w-4 h-4" />;
      case 'viewer': return <Eye className="w-4 h-4" />;
      default: return <Users className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">User & Company Assignments</h1>
          <p className="text-gray-600">Manage user access and roles for different companies</p>
        </div>
        <Button 
          onClick={fetchUserAssignments} 
          disabled={loading}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading user assignments...</p>
        </div>
      ) : userAssignments ? (
        <div className="space-y-6">
          {/* Companies Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building className="w-5 h-5" />
                Companies Overview
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {userAssignments.companies.map(company => (
                  <div key={company.id} className="p-4 border rounded-lg">
                    <h3 className="font-semibold text-gray-900">{company.company_name}</h3>
                    <p className="text-sm text-gray-600">{company.business_type}</p>
                    <div className="mt-2 flex items-center gap-2">
                      <Badge variant="outline">{company.base_currency}</Badge>
                      <Badge variant={company.id === userAssignments.companies[0]?.id ? "default" : "secondary"}>
                        {company.id === userAssignments.companies[0]?.id ? "Main" : "Sister"}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* User Management */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                User Management ({userAssignments.users.length} users)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {userAssignments.users.map(userData => (
                  <div key={userData.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <Mail className="w-4 h-4 text-blue-600" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900">{userData.full_name}</h3>
                          <p className="text-sm text-gray-600">{userData.email}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => deleteUser(userData.id, userData.email)}
                          disabled={userData.email === 'admin@2mholding.com'}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                        <Select 
                          value={userData.role} 
                          onValueChange={(newRole) => updateUserRole(userData.id, newRole)}
                          disabled={updatingRole === userData.id}
                        >
                          <SelectTrigger className="w-32">
                            <SelectValue>
                              <div className="flex items-center gap-2">
                                {getRoleIcon(userData.role)}
                                <span className="capitalize">{userData.role}</span>
                              </div>
                            </SelectValue>
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="admin">
                              <div className="flex items-center gap-2">
                                <Shield className="w-4 h-4" />
                                Admin
                              </div>
                            </SelectItem>
                            <SelectItem value="user">
                              <div className="flex items-center gap-2">
                                <Edit className="w-4 h-4" />
                                User
                              </div>
                            </SelectItem>
                            <SelectItem value="viewer">
                              <div className="flex items-center gap-2">
                                <Eye className="w-4 h-4" />
                                Viewer
                              </div>
                            </SelectItem>
                          </SelectContent>
                        </Select>
                        <Badge className={getRoleBadgeColor(userData.role)}>
                          {userData.role.toUpperCase()}
                        </Badge>
                        {!userData.is_active && (
                          <Badge variant="destructive">Inactive</Badge>
                        )}
                      </div>
                    </div>

                    {/* Menu Permissions */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="text-sm font-medium text-gray-700">Menu Permissions:</h4>
                        {editingPermissions !== userData.id && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => startEditingPermissions(userData.id, userData.permissions)}
                          >
                            <Settings className="w-4 h-4 mr-1" />
                            Edit
                          </Button>
                        )}
                      </div>

                      {editingPermissions === userData.id ? (
                        <div className="space-y-2">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                            {[
                              { key: 'dashboard', label: 'Dashboard' },
                              { key: 'crm_contacts', label: 'CRM - Contacts' },
                              { key: 'crm_companies', label: 'CRM - Companies' },
                              { key: 'crm_call_logs', label: 'CRM - Call Logs' },
                              { key: 'crm_email_responses', label: 'CRM - Email Responses' },
                              { key: 'currency_management', label: 'Currency Management' },
                              { key: 'consolidated_accounts', label: 'Consolidated Accounts' },
                              { key: 'company_accounts', label: 'Company Accounts' },
                              { key: 'user_management', label: 'User Management' },
                              { key: 'company_assignments', label: 'Company Assignments' }
                            ].map(permission => (
                              <div key={permission.key} className="flex items-center justify-between p-2 bg-white border rounded">
                                <span className="text-sm text-gray-700">{permission.label}</span>
                                <div className="flex items-center gap-2">
                                  <Button
                                    size="sm"
                                    variant={tempPermissions[permission.key] ? "default" : "outline"}
                                    onClick={() => handlePermissionToggle(permission.key, !tempPermissions[permission.key])}
                                    className="h-6 w-16"
                                  >
                                    {tempPermissions[permission.key] ? 
                                      <><Check className="w-3 h-3 mr-1" />Yes</> : 
                                      <><X className="w-3 h-3 mr-1" />No</>
                                    }
                                  </Button>
                                </div>
                              </div>
                            ))}
                          </div>
                          <div className="flex gap-2 pt-2">
                            <Button
                              size="sm"
                              onClick={() => updateUserPermissions(userData.id, tempPermissions)}
                              className="bg-green-600 hover:bg-green-700"
                            >
                              Save Permissions
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => setEditingPermissions(null)}
                            >
                              Cancel
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-1">
                          {[
                            { key: 'dashboard', label: 'Dashboard' },
                            { key: 'crm_contacts', label: 'CRM - Contacts' },
                            { key: 'crm_companies', label: 'CRM - Companies' },
                            { key: 'crm_call_logs', label: 'CRM - Call Logs' },
                            { key: 'crm_email_responses', label: 'CRM - Email Responses' },
                            { key: 'currency_management', label: 'Currency Management' },
                            { key: 'consolidated_accounts', label: 'Consolidated Accounts' },
                            { key: 'company_accounts', label: 'Company Accounts' },
                            { key: 'user_management', label: 'User Management' },
                            { key: 'company_assignments', label: 'Company Assignments' }
                          ].map(permission => (
                            <div key={permission.key} className="flex items-center justify-between text-xs p-1">
                              <span className="text-gray-600">{permission.label}</span>
                              <Badge variant={userData.permissions?.[permission.key] ? "default" : "secondary"} className="text-xs">
                                {userData.permissions?.[permission.key] ? 'Yes' : 'No'}
                              </Badge>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Role Descriptions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Info className="w-5 h-5" />
                Role Descriptions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-3 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Shield className="w-4 h-4 text-red-600" />
                    <span className="font-semibold text-red-600">Admin</span>
                  </div>
                  <p className="text-sm text-gray-600">
                    Full access to all features, can manage users, create/edit companies, and access all financial data.
                  </p>
                </div>
                <div className="p-3 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Edit className="w-4 h-4 text-blue-600" />
                    <span className="font-semibold text-blue-600">User</span>
                  </div>
                  <p className="text-sm text-gray-600">
                    Can view and edit company data, manage accounts, but cannot manage other users or system settings.
                  </p>
                </div>
                <div className="p-3 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Eye className="w-4 h-4 text-gray-600" />
                    <span className="font-semibold text-gray-600">Viewer</span>
                  </div>
                  <p className="text-sm text-gray-600">
                    Read-only access to view company information and financial reports. Cannot make any changes.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            Failed to load user assignments. Please ensure you have admin privileges.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default UserAssignments;