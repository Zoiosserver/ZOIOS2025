import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { 
  Building, 
  RefreshCw, 
  BarChart3,
  DollarSign,
  FileText,
  ChevronDown,
  Info,
  Globe,
  Plus,
  Edit,
  Save,
  X
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CompanyAccounts = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [companyAccounts, setCompanyAccounts] = useState(null);
  const [editingBalance, setEditingBalance] = useState(null);
  const [newBalance, setNewBalance] = useState('');
  const [showAddAccountDialog, setShowAddAccountDialog] = useState(false);
  const [newAccount, setNewAccount] = useState({
    code: '',
    name: '',
    account_type: '',
    category: '',
    opening_balance: 0
  });

  const getNextAccountCode = (accountType) => {
    if (!companyAccounts?.accounts_by_category) return '';
    
    const accountTypeRanges = {
      'Asset': { start: 1000, prefix: '1' },
      'Liability': { start: 2000, prefix: '2' },
      'Equity': { start: 3000, prefix: '3' },
      'Revenue': { start: 4000, prefix: '4' },
      'Expense': { start: 5000, prefix: '5' }
    };
    
    const range = accountTypeRanges[accountType];
    if (!range) return '';
    
    // Get all existing codes for this account type across all categories
    const existingCodes = [];
    Object.values(companyAccounts.accounts_by_category).forEach(accounts => {
      accounts.forEach(account => {
        if (account.account_type === accountType && account.code) {
          const codeNum = parseInt(account.code);
          if (!isNaN(codeNum) && codeNum >= range.start && codeNum < range.start + 1000) {
            existingCodes.push(codeNum);
          }
        }
      });
    });
    
    // Sort existing codes
    existingCodes.sort((a, b) => a - b);
    
    // Find the next available code starting from range.start
    let nextCode = range.start;
    while (existingCodes.includes(nextCode)) {
      nextCode++;
    }
    
    return nextCode.toString();
  };

  const handleAccountTypeChange = (accountType) => {
    // Add a small delay to ensure companyAccounts is loaded
    setTimeout(() => {
      const nextCode = getNextAccountCode(accountType);
      setNewAccount({
        ...newAccount, 
        account_type: accountType,
        code: nextCode
      });
    }, 100);
  };

  useEffect(() => {
    fetchCompanies();
  }, []);

  const fetchCompanies = async () => {
    try {
      const response = await axios.get(`${API}/company/list`);
      setCompanies(response.data);
      
      // Auto-select the main company
      const mainCompany = response.data.find(c => c.is_main_company);
      if (mainCompany) {
        setSelectedCompany(mainCompany);
        fetchCompanyAccounts(mainCompany.id);
      }
    } catch (error) {
      console.error('Error fetching companies:', error);
      toast.error('Failed to load companies');
    }
  };

  const fetchCompanyAccounts = async (companyId) => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/company/${companyId}/chart-of-accounts`);
      setCompanyAccounts(response.data);
    } catch (error) {
      console.error('Error fetching company accounts:', error);
      toast.error('Failed to load chart of accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleCompanyChange = (companyId) => {
    const company = companies.find(c => c.id === companyId);
    setSelectedCompany(company);
    fetchCompanyAccounts(companyId);
  };

  const updateOpeningBalance = async (accountId, balance) => {
    try {
      await axios.put(`${API}/company/${selectedCompany.id}/accounts/${accountId}/opening-balance`, {
        opening_balance: parseFloat(balance)
      });
      toast.success('Opening balance updated successfully');
      fetchCompanyAccounts(selectedCompany.id);
      setEditingBalance(null);
    } catch (error) {
      console.error('Error updating opening balance:', error);
      toast.error('Failed to update opening balance');
    }
  };

  const addNewAccount = async () => {
    try {
      await axios.post(`${API}/company/${selectedCompany.id}/accounts`, newAccount);
      toast.success('Account added successfully');
      fetchCompanyAccounts(selectedCompany.id);
      setShowAddAccountDialog(false);
      setNewAccount({
        code: '',
        name: '',
        account_type: '',
        category: '',
        opening_balance: 0
      });
    } catch (error) {
      console.error('Error adding account:', error);
      toast.error(error.response?.data?.detail || 'Failed to add account');
    }
  };

  const formatCurrency = (amount, currency = 'USD') => {
    try {
      // Special handling for INR and other currencies
      const currencySymbols = {
        'INR': '₹',
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'CNY': '¥',
        'AUD': 'A$',
        'CAD': 'C$',
        'CHF': 'Fr'
      };
      
      const symbol = currencySymbols[currency] || currency;
      const formattedAmount = new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(amount);
      
      return `${symbol} ${formattedAmount}`;
    } catch (error) {
      return `${currency} ${amount.toFixed(2)}`;
    }
  };

  const getAccountTypeColor = (type) => {
    switch (type.toLowerCase()) {
      case 'asset': return 'bg-green-100 text-green-800 border-green-200';
      case 'liability': return 'bg-red-100 text-red-800 border-red-200';
      case 'equity': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'revenue': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'expense': return 'bg-orange-100 text-orange-800 border-orange-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category.toLowerCase()) {
      case 'current assets':
      case 'non-current assets': return <DollarSign className="w-4 h-4" />;
      case 'current liabilities':
      case 'non-current liabilities': return <BarChart3 className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Company Chart of Accounts</h1>
          <p className="text-gray-600">View and manage accounts for individual companies</p>
        </div>
        <Button 
          onClick={() => selectedCompany && fetchCompanyAccounts(selectedCompany.id)} 
          disabled={loading}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Company Selector */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building className="w-5 h-5" />
            Select Company
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <Select value={selectedCompany?.id} onValueChange={handleCompanyChange}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select a company">
                    {selectedCompany && (
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{selectedCompany.name}</span>
                        <Badge variant={selectedCompany.is_main_company ? "default" : "secondary"}>
                          {selectedCompany.is_main_company ? "Main" : "Sister"}
                        </Badge>
                      </div>
                    )}
                  </SelectValue>
                </SelectTrigger>
                <SelectContent>
                  {companies.map(company => (
                    <SelectItem key={company.id} value={company.id}>
                      <div className="flex items-center justify-between w-full">
                        <div className="flex flex-col">
                          <span className="font-medium">{company.name}</span>
                          <span className="text-xs text-gray-500">
                            {company.business_type} • {company.base_currency}
                          </span>
                        </div>
                        <Badge variant={company.is_main_company ? "default" : "secondary"} className="ml-2">
                          {company.is_main_company ? "Main" : "Sister"}
                        </Badge>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            {selectedCompany && (
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <Globe className="w-4 h-4" />
                  {selectedCompany.country_code}
                </div>
                <div className="flex items-center gap-1">
                  <DollarSign className="w-4 h-4" />
                  {selectedCompany.base_currency}
                </div>
                {!selectedCompany.is_main_company && (
                  <Badge variant="outline">
                    {selectedCompany.ownership_percentage}% owned
                  </Badge>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Company Accounts */}
      {selectedCompany && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Chart of Accounts - {selectedCompany.name}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading chart of accounts...</p>
              </div>
            ) : companyAccounts && companyAccounts.accounts_by_category ? (
              <div className="space-y-6">
                {/* Summary */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">{companyAccounts.total_accounts}</div>
                    <div className="text-sm text-gray-600">Total Accounts</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">{Object.keys(companyAccounts.accounts_by_category).length}</div>
                    <div className="text-sm text-gray-600">Categories</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">
                      {selectedCompany.base_currency === 'INR' && '₹'}
                      {selectedCompany.base_currency === 'USD' && '$'}
                      {selectedCompany.base_currency === 'EUR' && '€'}
                      {selectedCompany.base_currency === 'GBP' && '£'}
                      {selectedCompany.base_currency === 'JPY' && '¥'}
                      {!['INR', 'USD', 'EUR', 'GBP', 'JPY'].includes(selectedCompany.base_currency) && selectedCompany.base_currency}
                      {['INR', 'USD', 'EUR', 'GBP', 'JPY'].includes(selectedCompany.base_currency) && ` ${selectedCompany.base_currency}`}
                    </div>
                    <div className="text-sm text-gray-600">Base Currency</div>
                  </div>
                </div>

                {/* Accounts by Category */}
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Chart of Accounts</h3>
                  <Dialog open={showAddAccountDialog} onOpenChange={setShowAddAccountDialog}>
                    <DialogTrigger asChild>
                      <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                        <Plus className="w-4 h-4 mr-2" />
                        Add Account
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Add New Account</DialogTitle>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div>
                          <Label htmlFor="code">Account Code (Auto-generated)</Label>
                          <Input
                            id="code"
                            value={newAccount.code}
                            onChange={(e) => setNewAccount({...newAccount, code: e.target.value})}
                            placeholder="Select account type first"
                            disabled={!newAccount.account_type}
                          />
                          <p className="text-xs text-gray-500 mt-1">Code is auto-generated based on account type. You can modify if needed.</p>
                        </div>
                        <div>
                          <Label htmlFor="name">Account Name</Label>
                          <Input
                            id="name"
                            value={newAccount.name}
                            onChange={(e) => setNewAccount({...newAccount, name: e.target.value})}
                            placeholder="e.g., Cash in Hand"
                          />
                        </div>
                        <div>
                          <Label htmlFor="account_type">Account Type</Label>
                          <Select value={newAccount.account_type} onValueChange={handleAccountTypeChange}>
                            <SelectTrigger>
                              <SelectValue placeholder="Select account type" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="Asset">Asset (1000-1999)</SelectItem>
                              <SelectItem value="Liability">Liability (2000-2999)</SelectItem>
                              <SelectItem value="Equity">Equity (3000-3999)</SelectItem>
                              <SelectItem value="Revenue">Revenue (4000-4999)</SelectItem>
                              <SelectItem value="Expense">Expense (5000-5999)</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="category">Category</Label>
                          <Input
                            id="category"
                            value={newAccount.category}
                            onChange={(e) => setNewAccount({...newAccount, category: e.target.value})}
                            placeholder="e.g., Current Assets"
                          />
                        </div>
                        <div>
                          <Label htmlFor="opening_balance">Opening Balance</Label>
                          <Input
                            id="opening_balance"
                            type="number"
                            value={newAccount.opening_balance}
                            onChange={(e) => setNewAccount({...newAccount, opening_balance: parseFloat(e.target.value) || 0})}
                            placeholder="0.00"
                          />
                        </div>
                        <div className="flex gap-2 pt-4">
                          <Button onClick={addNewAccount} className="bg-blue-600 hover:bg-blue-700">
                            Add Account
                          </Button>
                          <Button variant="outline" onClick={() => setShowAddAccountDialog(false)}>
                            Cancel
                          </Button>
                        </div>
                      </div>
                    </DialogContent>
                  </Dialog>
                </div>

                {Object.entries(companyAccounts.accounts_by_category).map(([category, accounts]) => (
                  <div key={category} className="border rounded-lg overflow-hidden">
                    <div className="bg-gray-50 px-4 py-3 border-b">
                      <div className="flex items-center gap-2">
                        {getCategoryIcon(category)}
                        <h3 className="text-lg font-semibold text-gray-900">{category}</h3>
                        <Badge variant="outline">{accounts.length} accounts</Badge>
                      </div>
                    </div>
                    <div className="divide-y">
                      {accounts.map(account => (
                        <div key={account.id} className="p-4 hover:bg-gray-50 transition-colors">
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-2">
                                <span className="font-mono text-sm font-medium text-gray-700 bg-gray-100 px-2 py-1 rounded">
                                  {account.code}
                                </span>
                                <span className="font-medium text-gray-900">{account.name}</span>
                                <Badge className={getAccountTypeColor(account.account_type)}>
                                  {account.account_type}
                                </Badge>
                              </div>
                            </div>
                            <div className="flex items-center gap-4">
                              <div className="text-right">
                                {editingBalance === account.id ? (
                                  <div className="flex items-center gap-2">
                                    <Input
                                      type="number"
                                      value={newBalance}
                                      onChange={(e) => setNewBalance(e.target.value)}
                                      className="w-32"
                                      placeholder="0.00"
                                    />
                                    <Button 
                                      size="sm" 
                                      onClick={() => updateOpeningBalance(account.id, newBalance)}
                                      className="bg-green-600 hover:bg-green-700"
                                    >
                                      <Save className="w-4 h-4" />
                                    </Button>
                                    <Button 
                                      size="sm" 
                                      variant="outline"
                                      onClick={() => setEditingBalance(null)}
                                    >
                                      <X className="w-4 h-4" />
                                    </Button>
                                  </div>
                                ) : (
                                  <>
                                    <div className="text-lg font-semibold text-gray-900">
                                      {formatCurrency(account.balance, selectedCompany.base_currency)}
                                    </div>
                                    <div className="text-sm text-gray-500">Current Balance</div>
                                  </>
                                )}
                              </div>
                              {editingBalance !== account.id && (
                                <Button 
                                  size="sm" 
                                  variant="outline"
                                  onClick={() => {
                                    setEditingBalance(account.id);
                                    setNewBalance(account.balance.toString());
                                  }}
                                >
                                  <Edit className="w-4 h-4" />
                                </Button>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  No chart of accounts found for this company. The accounts may not have been created yet.
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {companies.length === 0 && (
        <Alert>
          <Building className="h-4 w-4" />
          <AlertDescription>
            No companies found. Please complete your company setup first.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default CompanyAccounts;