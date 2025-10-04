import React, { useState, useEffect } from 'react';
import ZoiosLogo from './ZoiosLogo';

const CompanyManagement = ({ user, onBack }) => {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingCompany, setEditingCompany] = useState(null);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [activeTab, setActiveTab] = useState('companies'); // companies, accounts, consolidated

  const [companyForm, setCompanyForm] = useState({
    company_name: '',
    country_code: 'IN',
    business_type: 'Private Limited Company',
    industry: 'Technology',
    base_currency: 'INR',
    accounting_system: 'indian_gaap',
    address: '',
    city: '',
    state: '',
    postal_code: '',
    phone: '',
    email: '',
    website: '',
    tax_number: '',
    registration_number: ''
  });

  useEffect(() => {
    fetchCompanies();
  }, []);

  const fetchCompanies = async () => {
    try {
      const backendUrl = window.location.origin;
      const response = await fetch(`${backendUrl}/api/companies/management`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setCompanies(data);
      } else {
        setError('Failed to load companies');
      }
    } catch (err) {
      setError('Connection failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const backendUrl = window.location.origin;
      const url = editingCompany 
        ? `${backendUrl}/api/companies/management/${editingCompany.id}` 
        : `${backendUrl}/api/setup/company`;  // Use existing company setup endpoint for creating
      
      const method = editingCompany ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(companyForm)
      });

      if (response.ok) {
        await fetchCompanies();
        setShowAddModal(false);
        setEditingCompany(null);
        resetForm();
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || 'Failed to save company');
      }
    } catch (err) {
      setError('Connection failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (companyId) => {
    if (!window.confirm('Are you sure you want to delete this company? This will also delete all related chart of accounts and sister companies.')) return;

    try {
      const backendUrl = window.location.origin;
      const response = await fetch(`${backendUrl}/api/companies/management/${companyId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        await fetchCompanies();
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || 'Failed to delete company');
      }
    } catch (err) {
      setError('Connection failed: ' + err.message);
    }
  };

  const resetForm = () => {
    setCompanyForm({
      company_name: '',
      country_code: 'IN',
      business_type: 'Private Limited Company',
      industry: 'Technology',
      base_currency: 'INR',
      accounting_system: 'indian_gaap',
      address: '',
      city: '',
      state: '',
      postal_code: '',
      phone: '',
      email: '',
      website: '',
      tax_number: '',
      registration_number: ''
    });
  };

  const startEdit = (company) => {
    setEditingCompany(company);
    setCompanyForm({ ...company });
    setShowAddModal(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="relative bg-white/80 backdrop-blur-xl shadow-lg border-b border-gray-100/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4 sm:py-6">
            <div className="flex items-center space-x-4">
              <div className="bg-white p-2 sm:p-3 rounded-xl shadow-md border border-gray-100">
                <ZoiosLogo size="medium" />
              </div>
              <div>
                <h1 className="text-xl sm:text-2xl font-bold text-gray-900">Company Management</h1>
                <p className="text-sm sm:text-base text-gray-600">Manage companies and chart of accounts</p>
              </div>
            </div>
            <button
              onClick={onBack}
              className="bg-gradient-to-r from-gray-500 to-gray-600 text-white px-4 py-2 rounded-xl hover:from-gray-600 hover:to-gray-700 transition-all duration-200 transform hover:scale-105 shadow-lg"
            >
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
                </svg>
                <span className="hidden sm:inline">Back to Dashboard</span>
              </div>
            </button>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-2">
          <div className="flex space-x-1">
            <button
              onClick={() => setActiveTab('companies')}
              className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all duration-200 ${
                activeTab === 'companies'
                  ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
                </svg>
                <span>Companies</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('accounts')}
              className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all duration-200 ${
                activeTab === 'accounts'
                  ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
                </svg>
                <span>Chart of Accounts</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('consolidated')}
              className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all duration-200 ${
                activeTab === 'consolidated'
                  ? 'bg-gradient-to-r from-purple-500 to-violet-500 text-white shadow-lg'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                </svg>
                <span>Consolidated</span>
              </div>
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="mt-6">
          {activeTab === 'companies' && (
            <CompaniesTab 
              companies={companies}
              loading={loading}
              error={error}
              onAdd={() => setShowAddModal(true)}
              onEdit={startEdit}
              onDelete={handleDelete}
              onSelectCompany={setSelectedCompany}
            />
          )}
          
          {activeTab === 'accounts' && (
            <ChartOfAccountsTab 
              companies={companies}
              selectedCompany={selectedCompany}
              onSelectCompany={setSelectedCompany}
            />
          )}
          
          {activeTab === 'consolidated' && (
            <ConsolidatedAccountsTab 
              companies={companies}
              user={user}
            />
          )}
        </div>
      </div>

      {/* Add/Edit Company Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-gray-900">
                  {editingCompany ? 'Edit Company' : 'Add New Company'}
                </h3>
                <button
                  onClick={() => {
                    setShowAddModal(false);
                    setEditingCompany(null);
                    resetForm();
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Form fields will be added here */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Company Name</label>
                    <input
                      type="text"
                      value={companyForm.company_name}
                      onChange={(e) => setCompanyForm({ ...companyForm, company_name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Business Type</label>
                    <select
                      value={companyForm.business_type}
                      onChange={(e) => setCompanyForm({ ...companyForm, business_type: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="Private Limited Company">Private Limited Company</option>
                      <option value="Group Company">Group Company</option>
                      <option value="Public Limited Company">Public Limited Company</option>
                      <option value="Partnership">Partnership</option>
                      <option value="Sole Proprietorship">Sole Proprietorship</option>
                    </select>
                  </div>
                </div>

                <div className="flex justify-end space-x-3 pt-6">
                  <button
                    type="button"
                    onClick={() => {
                      setShowAddModal(false);
                      setEditingCompany(null);
                      resetForm();
                    }}
                    className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-6 py-2 bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-lg hover:from-blue-600 hover:to-indigo-600 disabled:opacity-50"
                  >
                    {loading ? 'Saving...' : editingCompany ? 'Update Company' : 'Create Company'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Separate components for each tab
const CompaniesTab = ({ companies, loading, error, onAdd, onEdit, onDelete, onSelectCompany }) => (
  <div className="space-y-6">
    <div className="flex justify-between items-center">
      <h2 className="text-2xl font-bold text-gray-900">Companies</h2>
      <button
        onClick={onAdd}
        className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white px-6 py-3 rounded-xl hover:from-blue-600 hover:to-indigo-600 transition-all duration-200 transform hover:scale-105 font-medium shadow-lg"
      >
        <div className="flex items-center space-x-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4"/>
          </svg>
          <span>Add Company</span>
        </div>
      </button>
    </div>

    {error && (
      <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-lg">
        <span className="text-red-700 text-sm">{error}</span>
      </div>
    )}

    <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
      {companies.map((company) => (
        <div key={company.id} className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h3 className="text-xl font-bold text-gray-900 mb-2">{company.company_name}</h3>
              <div className="space-y-1 text-sm text-gray-600">
                <p><span className="font-medium">Type:</span> {company.business_type}</p>
                <p><span className="font-medium">Industry:</span> {company.industry}</p>
                <p><span className="font-medium">Currency:</span> {company.base_currency}</p>
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => onEdit(company)}
                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                </svg>
              </button>
              <button
                onClick={() => onDelete(company.id)}
                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </div>
          </div>
          
          <button
            onClick={() => onSelectCompany(company)}
            className="w-full bg-gradient-to-r from-green-500 to-emerald-500 text-white py-2 px-4 rounded-xl hover:from-green-600 hover:to-emerald-600 transition-all duration-200 font-medium"
          >
            View Chart of Accounts
          </button>
        </div>
      ))}
    </div>
  </div>
);

const ChartOfAccountsTab = ({ companies, selectedCompany, onSelectCompany }) => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingAccount, setEditingAccount] = useState(null);
  const [accountForm, setAccountForm] = useState({
    account_name: '',
    account_code: '',
    account_type: 'asset',
    category: 'current_asset',
    description: '',
    opening_balance: 0
  });

  const accountTypes = {
    asset: ['current_asset', 'fixed_asset', 'other_asset'],
    liability: ['current_liability', 'long_term_liability', 'other_liability'],
    equity: ['equity'],
    revenue: ['revenue'],
    expense: ['operating_expense', 'other_expense']
  };

  useEffect(() => {
    if (selectedCompany) {
      fetchAccounts();
    }
  }, [selectedCompany]);

  const fetchAccounts = async () => {
    if (!selectedCompany) return;
    
    setLoading(true);
    try {
      const backendUrl = window.location.origin;
      const response = await fetch(`${backendUrl}/api/companies/${selectedCompany.id}/accounts/enhanced`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setAccounts(data.accounts || []);
      } else {
        setError('Failed to load accounts');
      }
    } catch (err) {
      setError('Connection failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAccount = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const backendUrl = window.location.origin;
      const url = editingAccount 
        ? `${backendUrl}/api/companies/${selectedCompany.id}/accounts/${editingAccount.id}/enhanced`
        : `${backendUrl}/api/companies/${selectedCompany.id}/accounts/enhanced`;
      
      const method = editingAccount ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(accountForm)
      });

      if (response.ok) {
        await fetchAccounts();
        setShowAddModal(false);
        setEditingAccount(null);
        resetAccountForm();
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || 'Failed to save account');
      }
    } catch (err) {
      setError('Connection failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async (accountId) => {
    if (!window.confirm('Are you sure you want to delete this account?')) return;

    try {
      const backendUrl = window.location.origin;
      const response = await fetch(`${backendUrl}/api/companies/${selectedCompany.id}/accounts/${accountId}/enhanced`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        await fetchAccounts();
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || 'Failed to delete account');
      }
    } catch (err) {
      setError('Connection failed: ' + err.message);
    }
  };

  const resetAccountForm = () => {
    setAccountForm({
      account_name: '',
      account_code: '',
      account_type: 'asset',
      category: 'current_asset',
      description: '',
      opening_balance: 0
    });
  };

  const startEditAccount = (account) => {
    setEditingAccount(account);
    setAccountForm({ ...account });
    setShowAddModal(true);
  };

  const exportAccounts = async (format) => {
    if (!selectedCompany) return;

    try {
      const backendUrl = window.location.origin;
      const response = await fetch(`${backendUrl}/api/companies/${selectedCompany.id}/accounts/export`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ format })
      });

      if (response.ok) {
        const data = await response.json();
        
        if (format === 'excel') {
          // Create Excel file from data
          const workbook = XLSX.utils.book_new();
          const worksheet = XLSX.utils.json_to_sheet(data.data.accounts);
          XLSX.utils.book_append_sheet(workbook, worksheet, 'Chart of Accounts');
          XLSX.writeFile(workbook, data.filename);
        } else if (format === 'pdf') {
          // Create PDF from data (simplified version)
          window.print(); // This will print the current view
        }
      } else {
        setError('Failed to export accounts');
      }
    } catch (err) {
      setError('Export failed: ' + err.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Chart of Accounts</h2>
          {selectedCompany && (
            <p className="text-gray-600">Managing accounts for {selectedCompany.company_name}</p>
          )}
        </div>
        
        {selectedCompany && (
          <div className="flex space-x-3">
            <button
              onClick={() => exportAccounts('excel')}
              className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-4 py-2 rounded-xl hover:from-green-600 hover:to-emerald-600 transition-all duration-200 font-medium text-sm"
            >
              Export Excel
            </button>
            <button
              onClick={() => exportAccounts('pdf')}
              className="bg-gradient-to-r from-red-500 to-pink-500 text-white px-4 py-2 rounded-xl hover:from-red-600 hover:to-pink-600 transition-all duration-200 font-medium text-sm"
            >
              Export PDF
            </button>
            <button
              onClick={() => setShowAddModal(true)}
              className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white px-4 py-2 rounded-xl hover:from-blue-600 hover:to-indigo-600 transition-all duration-200 font-medium text-sm"
            >
              Add Account
            </button>
          </div>
        )}
      </div>

      {!selectedCompany ? (
        <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-8 text-center">
          <div className="text-gray-400 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">Select a Company</h3>
          <p className="text-gray-500 mb-6">Choose a company from the Companies tab to view its chart of accounts</p>
          
          {companies.length > 0 && (
            <div className="max-w-md mx-auto">
              <select
                onChange={(e) => {
                  const company = companies.find(c => c.id === e.target.value);
                  if (company) onSelectCompany(company);
                }}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a company...</option>
                {companies.map(company => (
                  <option key={company.id} value={company.id}>{company.company_name}</option>
                ))}
              </select>
            </div>
          )}
        </div>
      ) : (
        <>
          {error && (
            <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-lg">
              <span className="text-red-700 text-sm">{error}</span>
            </div>
          )}

          {loading ? (
            <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-8 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
              <p className="text-gray-600 mt-4">Loading accounts...</p>
            </div>
          ) : (
            <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
                    <tr>
                      <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Account Code</th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Account Name</th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Balance</th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {accounts.map((account) => (
                      <tr key={account.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{account.account_code}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{account.account_name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 capitalize">{account.account_type}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 capitalize">{account.category?.replace('_', ' ')}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{account.current_balance || 0}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                          <button
                            onClick={() => startEditAccount(account)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteAccount(account.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {accounts.length === 0 && (
                <div className="p-8 text-center">
                  <p className="text-gray-500">No accounts found for this company</p>
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Add/Edit Account Modal */}
      {showAddModal && selectedCompany && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-gray-900">
                  {editingAccount ? 'Edit Account' : 'Add New Account'}
                </h3>
                <button
                  onClick={() => {
                    setShowAddModal(false);
                    setEditingAccount(null);
                    resetAccountForm();
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>

              <form onSubmit={handleSubmitAccount} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Account Name</label>
                  <input
                    type="text"
                    value={accountForm.account_name}
                    onChange={(e) => setAccountForm({ ...accountForm, account_name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Account Code</label>
                  <input
                    type="text"
                    value={accountForm.account_code}
                    onChange={(e) => setAccountForm({ ...accountForm, account_code: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Account Type</label>
                  <select
                    value={accountForm.account_type}
                    onChange={(e) => {
                      const type = e.target.value;
                      setAccountForm({ 
                        ...accountForm, 
                        account_type: type,
                        category: accountTypes[type][0]
                      });
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="asset">Asset</option>
                    <option value="liability">Liability</option>
                    <option value="equity">Equity</option>
                    <option value="revenue">Revenue</option>
                    <option value="expense">Expense</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                  <select
                    value={accountForm.category}
                    onChange={(e) => setAccountForm({ ...accountForm, category: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {accountTypes[accountForm.account_type]?.map(category => (
                      <option key={category} value={category}>
                        {category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Opening Balance</label>
                  <input
                    type="number"
                    step="0.01"
                    value={accountForm.opening_balance}
                    onChange={(e) => setAccountForm({ ...accountForm, opening_balance: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                  <textarea
                    value={accountForm.description}
                    onChange={(e) => setAccountForm({ ...accountForm, description: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows="2"
                  />
                </div>

                <div className="flex justify-end space-x-3 pt-6">
                  <button
                    type="button"
                    onClick={() => {
                      setShowAddModal(false);
                      setEditingAccount(null);
                      resetAccountForm();
                    }}
                    className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-6 py-2 bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-lg hover:from-blue-600 hover:to-indigo-600 disabled:opacity-50"
                  >
                    {loading ? 'Saving...' : editingAccount ? 'Update Account' : 'Create Account'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const ConsolidatedAccountsTab = ({ companies, user }) => (
  <div>
    <h2 className="text-2xl font-bold text-gray-900 mb-6">Consolidated Accounts</h2>
    {/* Consolidated accounts content will be implemented */}
    <p className="text-gray-600">Consolidated accounts functionality will be implemented here</p>
  </div>
);

export default CompanyManagement;