import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { 
  Building, 
  RefreshCw, 
  BarChart3,
  TrendingUp,
  DollarSign,
  Users,
  Info,
  FileText
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ConsolidatedAccounts = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [consolidatedAccounts, setConsolidatedAccounts] = useState([]);
  const [sisterCompanies, setSisterCompanies] = useState([]);
  const [companySetup, setCompanySetup] = useState(null);

  useEffect(() => {
    fetchCompanySetup();
    fetchSisterCompanies();
    fetchConsolidatedAccounts();
  }, []);

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
    }
  };

  const fetchConsolidatedAccounts = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/company/consolidated-accounts`);
      setConsolidatedAccounts(response.data);
    } catch (error) {
      console.error('Error fetching consolidated accounts:', error);
      if (error.response?.status === 400) {
        toast.error('Only group companies have consolidated accounts');
      } else {
        toast.error('Failed to load consolidated accounts');
      }
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount, currency = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount);
  };

  const getAccountTypeColor = (type) => {
    switch (type.toLowerCase()) {
      case 'asset': return 'bg-green-100 text-green-800';
      case 'liability': return 'bg-red-100 text-red-800';
      case 'equity': return 'bg-blue-100 text-blue-800';
      case 'revenue': return 'bg-purple-100 text-purple-800';
      case 'expense': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (companySetup && companySetup.business_type !== 'Group Company') {
    return (
      <div className="p-6">
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            Consolidated accounts are only available for Group Companies. 
            Your company type is: {companySetup.business_type}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Consolidated Accounts</h1>
          <p className="text-gray-600">Group-level consolidated financial view</p>
        </div>
        <Button 
          onClick={fetchConsolidatedAccounts} 
          disabled={loading}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Group Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Group Company</CardTitle>
            <Building className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{companySetup?.company_name}</div>
            <p className="text-xs text-muted-foreground">
              Base Currency: {companySetup?.base_currency}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sister Companies</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{sisterCompanies.length}</div>
            <p className="text-xs text-muted-foreground">
              Active subsidiaries
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Account Categories</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{consolidatedAccounts.length}</div>
            <p className="text-xs text-muted-foreground">
              Consolidated accounts
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Sister Companies List */}
      {sisterCompanies.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Sister Companies</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {sisterCompanies.map(company => (
                <div key={company.id} className="p-4 border rounded-lg">
                  <h3 className="font-semibold text-gray-900">{company.company_name}</h3>
                  <p className="text-sm text-gray-600">{company.business_type}</p>
                  <p className="text-sm text-gray-600">{company.industry}</p>
                  <div className="mt-2 flex items-center justify-between">
                    <Badge variant="outline">{company.base_currency}</Badge>
                    <span className="text-xs text-gray-500">
                      {company.ownership_percentage}% owned
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Consolidated Accounts */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Consolidated Chart of Accounts
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading consolidated accounts...</p>
            </div>
          ) : consolidatedAccounts.length === 0 ? (
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                No consolidated accounts available. Make sure you have set up sister companies and their chart of accounts.
              </AlertDescription>
            </Alert>
          ) : (
            <div className="space-y-4">
              {consolidatedAccounts.map(account => (
                <div key={account.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {account.account_code} - {account.account_name}
                      </h3>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge className={getAccountTypeColor(account.account_type)}>
                          {account.account_type}
                        </Badge>
                        <span className="text-sm text-gray-600">{account.category}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-semibold text-gray-900">
                        {formatCurrency(account.consolidated_balance, companySetup?.base_currency)}
                      </div>
                      <div className="text-sm text-gray-500">Consolidated</div>
                    </div>
                  </div>

                  {/* Sister Company Breakdown */}
                  {account.sister_companies_data.length > 0 && (
                    <div className="mt-4 space-y-2">
                      <h4 className="text-sm font-medium text-gray-700">Company Breakdown:</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                        {account.sister_companies_data.map((companyData, index) => (
                          <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                            <span className="text-sm text-gray-700">{companyData.company_name}</span>
                            <div className="text-right">
                              <div className="text-sm font-medium">
                                {formatCurrency(companyData.balance, companySetup?.base_currency)}
                              </div>
                              <div className="text-xs text-gray-500">
                                {companyData.ownership_percentage}% owned
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {sisterCompanies.length === 0 && (
        <Alert>
          <Building className="h-4 w-4" />
          <AlertDescription>
            You haven't added any sister companies yet. Go to Company Setup to add sister companies for consolidated reporting.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default ConsolidatedAccounts;