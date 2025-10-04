import React, { useState, useEffect } from 'react';
import ZoiosLogo from './ZoiosLogo';

const CompanyManagement = ({ user, onBack }) => {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddCompanyModal, setShowAddCompanyModal] = useState(false);
  const [showAddSisterModal, setShowAddSisterModal] = useState(false);
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
      // Use environment variable for backend URL to ensure correct API calls
      const backendUrl = process.env.REACT_APP_BACKEND_URL || window.location.origin;
      const apiUrl = `${backendUrl}/api/companies/management`;
      
      console.log('DEBUG: Fetching companies from URL:', apiUrl);
      console.log('DEBUG: Using token:', localStorage.getItem('token') ? 'Token present' : 'No token found');
      
      const response = await fetch(apiUrl, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const companiesData = await response.json();
        
        console.log('DEBUG: ===== COMPANY DATA ANALYSIS =====');
        console.log('DEBUG: Received companies data:', companiesData);
        console.log('DEBUG: Total companies count:', companiesData.length);
        console.log('DEBUG: Data type check:', Array.isArray(companiesData) ? 'Array' : typeof companiesData);
        
        if (companiesData.length > 0) {
          console.log('DEBUG: First company structure:', companiesData[0]);
          console.log('DEBUG: First company fields:', Object.keys(companiesData[0]));
        }
        
        // Ensure we have an array to work with
        const companiesArray = Array.isArray(companiesData) ? companiesData : [];
        
        if (companiesArray.length === 0) {
          console.log('DEBUG: No companies found in response');
          setCompanies([]);
          return;
        }
        
        // The backend returns both main companies and sister companies in one list
        // Group them for better display
        const mainCompanies = companiesArray.filter(company => {
          const isMain = company.is_main_company === true;
          console.log(`DEBUG: Company ${company.company_name} - is_main_company: ${company.is_main_company} (${typeof company.is_main_company}) - filtered as main: ${isMain}`);
          return isMain;
        });
        
        const sisterCompanies = companiesArray.filter(company => {
          const isSister = company.is_main_company === false;
          console.log(`DEBUG: Company ${company.company_name} - is_main_company: ${company.is_main_company} (${typeof company.is_main_company}) - filtered as sister: ${isSister}`);
          return isSister;
        });
        
        console.log('DEBUG: ===== FILTERING RESULTS =====');
        console.log('DEBUG: Main companies count:', mainCompanies.length);
        console.log('DEBUG: Main companies:', mainCompanies.map(c => ({ name: c.company_name, id: c.id, is_main: c.is_main_company })));
        console.log('DEBUG: Sister companies count:', sisterCompanies.length);
        console.log('DEBUG: Sister companies:', sisterCompanies.map(c => ({ name: c.company_name, id: c.id, is_main: c.is_main_company, parent_id: c.parent_company_id })));
        
        // Add sister companies info to main companies
        const companiesWithSisters = mainCompanies.map(company => {
          const attachedSisters = sisterCompanies.filter(sister => {
            const matches = sister.parent_company_id === company.id;
            console.log(`DEBUG: Sister ${sister.company_name} (parent_id: ${sister.parent_company_id}) matches main company ${company.company_name} (id: ${company.id}): ${matches}`);
            return matches;
          });
          
          console.log(`DEBUG: ===== FINAL ATTACHMENT =====`);
          console.log(`DEBUG: Main company ${company.company_name} (ID: ${company.id}) has ${attachedSisters.length} sister companies attached`);
          if (attachedSisters.length > 0) {
            console.log('DEBUG: Attached sisters:', attachedSisters.map(s => s.company_name));
          }
          
          return {
            ...company,
            sister_companies: attachedSisters
          };
        });
        
        console.log('DEBUG: ===== FINAL STATE =====');
        console.log('DEBUG: Companies with sisters attached:', companiesWithSisters.map(c => ({ 
          name: c.company_name, 
          id: c.id, 
          sister_count: c.sister_companies?.length || 0,
          sisters: c.sister_companies?.map(s => s.company_name) || []
        })));
        
        // Set companies - include both main companies (with sister data) and individual sister companies
        const finalCompanies = [...companiesWithSisters, ...sisterCompanies];
        console.log('DEBUG: Final companies array length:', finalCompanies.length);
        console.log('DEBUG: Final companies:', finalCompanies.map(c => ({ name: c.company_name, is_main: c.is_main_company, has_sisters: c.sister_companies?.length > 0 })));
        
        setCompanies(finalCompanies);
      } else {
        const errorText = await response.text();
        console.error('DEBUG: API Error Response:', response.status, errorText);
        setError(`Failed to load companies: ${response.status} ${response.statusText}`);
      }
    } catch (err) {
      console.error('DEBUG: Network Error:', err);
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
        setShowAddCompanyModal(false);
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

  const handleConvertToGroupCompany = async () => {
    if (!window.confirm('Convert your company to Group Company? This will enable you to add sister companies.')) return;

    try {
      // Use environment variable for backend URL to ensure correct API calls
      const backendUrl = process.env.REACT_APP_BACKEND_URL || window.location.origin;
      const response = await fetch(`${backendUrl}/api/setup/company/convert-to-group`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const result = await response.json();
        await fetchCompanies(); // Refresh the companies list
        alert('Company successfully converted to Group Company! You can now add sister companies.');
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || 'Failed to convert company to Group Company');
      }
    } catch (err) {
      setError('Connection failed: ' + err.message);
    }
  };

  const handleAddSisterCompany = async (e) => {
    e.preventDefault();
    
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || window.location.origin;
      const response = await fetch(`${backendUrl}/api/company/sister-companies`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(sisterCompanyForm)
      });

      if (response.ok) {
        await fetchCompanies(); // Refresh the companies list
        setShowAddSisterModal(false);
        resetSisterForm();
        alert('Sister company added successfully!');
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || 'Failed to add sister company');
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
    setShowAddCompanyModal(true);
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

      {/* Navigation Tabs - Mobile Friendly */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
        <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-1 sm:p-2">
          <div className="grid grid-cols-3 gap-1 sm:flex sm:space-x-1">
            <button
              onClick={() => setActiveTab('companies')}
              className={`py-2 px-2 sm:py-3 sm:px-4 rounded-xl font-medium transition-all duration-200 text-xs sm:text-sm ${
                activeTab === 'companies'
                  ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <div className="flex flex-col sm:flex-row items-center justify-center space-y-1 sm:space-y-0 sm:space-x-2">
                <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
                </svg>
                <span className="hidden sm:inline">Companies</span>
                <span className="sm:hidden">Companies</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('accounts')}
              className={`py-2 px-2 sm:py-3 sm:px-4 rounded-xl font-medium transition-all duration-200 text-xs sm:text-sm ${
                activeTab === 'accounts'
                  ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <div className="flex flex-col sm:flex-row items-center justify-center space-y-1 sm:space-y-0 sm:space-x-2">
                <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
                </svg>
                <span className="hidden sm:inline">Chart of Accounts</span>
                <span className="sm:hidden">Accounts</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('consolidated')}
              className={`py-2 px-2 sm:py-3 sm:px-4 rounded-xl font-medium transition-all duration-200 text-xs sm:text-sm ${
                activeTab === 'consolidated'
                  ? 'bg-gradient-to-r from-purple-500 to-violet-500 text-white shadow-lg'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <div className="flex flex-col sm:flex-row items-center justify-center space-y-1 sm:space-y-0 sm:space-x-2">
                <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                </svg>
                <span className="hidden sm:inline">Consolidated</span>
                <span className="sm:hidden">Consolidated</span>
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
              onAdd={() => setShowAddCompanyModal(true)}
              onAddSister={() => setShowAddSisterModal(true)}
              onEdit={startEdit}
              onDelete={handleDelete}
              onSelectCompany={setSelectedCompany}
              onConvertToGroup={handleConvertToGroupCompany}
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
      {showAddCompanyModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-gray-900">
                  {editingCompany ? 'Edit Company' : 'Add New Company'}
                </h3>
                <button
                  onClick={() => {
                    setShowAddCompanyModal(false);
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
                      setShowAddCompanyModal(false);
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
const CompaniesTab = ({ companies, loading, error, onAdd, onAddSister, onEdit, onDelete, onSelectCompany, onConvertToGroup }) => (
  <div className="space-y-6">
    <div className="flex justify-between items-center">
      <h2 className="text-2xl font-bold text-gray-900">Companies</h2>
      <div className="flex gap-2">
        <button
          onClick={onConvertToGroup}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
          title="Convert your company to Group Company to add sister companies"
        >
          Enable Sister Companies
        </button>
        <button
          onClick={onAddSister}
          className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white px-6 py-3 rounded-xl hover:from-blue-600 hover:to-indigo-600 transition-all duration-200 transform hover:scale-105 font-medium shadow-lg"
        >
          <div className="flex items-center space-x-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4"/>
            </svg>
            <span>Add Sister Company</span>
          </div>
        </button>
      </div>
    </div>

    {error && (
      <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-lg">
        <span className="text-red-700 text-sm">{error}</span>
      </div>
    )}

    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6">
      {companies.map((company) => (
        <div key={company.id} className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-4 sm:p-6">
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between mb-4 space-y-3 sm:space-y-0">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
                <h3 className="text-lg sm:text-xl font-bold text-gray-900 truncate">{company.company_name}</h3>
                {company.is_main_company ? (
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">Main</span>
                ) : (
                  <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs font-medium rounded-full">Sister</span>
                )}
              </div>
              <div className="space-y-1 text-sm text-gray-600">
                <p><span className="font-medium">Type:</span> <span className="break-words">{company.business_type}</span></p>
                <p><span className="font-medium">Industry:</span> <span className="break-words">{company.industry}</span></p>
                <p><span className="font-medium">Currency:</span> {company.base_currency}</p>
                {company.is_main_company === true && (
                  <div>
                    {company.sister_companies && company.sister_companies.length > 0 ? (
                      <div>
                        <p><span className="font-medium">Sister Companies ({company.sister_companies.length}):</span></p>
                        <div className="mt-1 ml-2 space-y-1">
                          {company.sister_companies.map((sister, index) => (
                            <p key={index} className="text-xs text-blue-600 font-medium">
                              • {sister.company_name || 'Unknown Sister Company'} ({sister.business_type || 'Unknown Type'})
                            </p>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <p><span className="font-medium">Sister Companies:</span> <span className="text-gray-500 text-sm">None</span></p>
                    )}
                  </div>
                )}
                {!company.is_main_company && company.parent_company_id && (
                  <p><span className="font-medium">Parent Company ID:</span> <span className="text-xs font-mono">{company.parent_company_id.substring(0, 8)}...</span></p>
                )}
              </div>
            </div>
            <div className="flex space-x-2 sm:flex-col sm:space-x-0 sm:space-y-2 justify-end">
              <button
                onClick={() => onEdit(company)}
                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="Edit Company"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                </svg>
              </button>
              <button
                onClick={() => onDelete(company.id)}
                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Delete Company"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </div>
          </div>
          
          <button
            onClick={() => onSelectCompany(company)}
            className="w-full bg-gradient-to-r from-green-500 to-emerald-500 text-white py-2 px-4 rounded-xl hover:from-green-600 hover:to-emerald-600 transition-all duration-200 font-medium text-sm sm:text-base"
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
  const [nextCodeLoading, setNextCodeLoading] = useState(false);
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

  const fetchNextAccountCode = async (accountType) => {
    if (!selectedCompany || !accountType) return;
    
    setNextCodeLoading(true);
    try {
      const backendUrl = window.location.origin;
      const response = await fetch(`${backendUrl}/api/companies/${selectedCompany.id}/accounts/next-code/${accountType}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setAccountForm(prev => ({
          ...prev,
          account_code: data.next_code
        }));
      }
    } catch (err) {
      console.error('Failed to fetch next account code:', err);
    } finally {
      setNextCodeLoading(false);
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
          const { utils, writeFile } = await import('xlsx');
          const workbook = utils.book_new();
          
          // Prepare data for Excel
          const excelData = accounts.map(account => ({
            'Account Code': account.account_code || 'N/A',
            'Account Name': account.account_name || 'N/A',
            'Account Type': account.account_type || 'N/A',
            'Category': (account.category || 'N/A').replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
            'Current Balance': account.current_balance || 0
          }));
          
          const worksheet = utils.json_to_sheet(excelData);
          utils.book_append_sheet(workbook, worksheet, 'Chart of Accounts');
          writeFile(workbook, data.filename || 'chart_of_accounts.xlsx');
        } else if (format === 'pdf') {
          // Create clean PDF with company header and table
          await generateCleanPDF(data.data);
        }
      } else {
        setError('Failed to export accounts');
      }
    } catch (err) {
      setError('Export failed: ' + err.message);
    }
  };

  const generateCleanPDF = async (pdfData) => {
    try {
      const { jsPDF } = await import('jspdf');
      await import('jspdf-autotable');
      
      const doc = new jsPDF();
      const pageWidth = doc.internal.pageSize.width;
      
      // Company Header
      doc.setFontSize(20);
      doc.setFont('helvetica', 'bold');
      doc.text(pdfData.company_info.name, pageWidth / 2, 20, { align: 'center' });
      
      // Company Address
      if (pdfData.company_info.address) {
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        doc.text(pdfData.company_info.address, pageWidth / 2, 28, { align: 'center' });
      }
      
      // Title
      doc.setFontSize(16);
      doc.setFont('helvetica', 'bold');
      doc.text('Chart of Accounts', pageWidth / 2, 40, { align: 'center' });
      
      // Export Date
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      doc.text(`Generated on: ${pdfData.company_info.export_date}`, pageWidth / 2, 47, { align: 'center' });
      
      // Table
      doc.autoTable({
        head: [pdfData.table_data.headers],
        body: pdfData.table_data.rows,
        startY: 55,
        theme: 'grid',
        headStyles: {
          fillColor: [59, 130, 246], // Blue color
          textColor: 255,
          fontStyle: 'bold'
        },
        styles: {
          fontSize: 8,
          cellPadding: 3
        },
        alternateRowStyles: {
          fillColor: [248, 250, 252] // Light gray
        }
      });
      
      // Summary at bottom
      const finalY = doc.lastAutoTable.finalY + 10;
      doc.setFontSize(12);
      doc.setFont('helvetica', 'bold');
      doc.text('Summary', 14, finalY);
      
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      let summaryY = finalY + 8;
      doc.text(`Total Accounts: ${pdfData.summary.total_accounts}`, 14, summaryY);
      doc.text(`Assets: ${pdfData.summary.assets_count}`, 14, summaryY + 6);
      doc.text(`Liabilities: ${pdfData.summary.liabilities_count}`, 14, summaryY + 12);
      doc.text(`Equity: ${pdfData.summary.equity_count}`, 14, summaryY + 18);
      doc.text(`Revenue: ${pdfData.summary.revenue_count}`, 90, summaryY + 6);
      doc.text(`Expenses: ${pdfData.summary.expense_count}`, 90, summaryY + 12);
      
      // Save PDF
      doc.save(`${pdfData.company_info.name.replace(/\s+/g, '_')}_chart_of_accounts.pdf`);
    } catch (error) {
      console.error('PDF generation failed:', error);
      setError('PDF generation failed: ' + error.message);
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
          <div className="flex flex-wrap gap-2 sm:space-x-3">
            <button
              onClick={() => exportAccounts('excel')}
              className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-3 sm:px-4 py-2 rounded-xl hover:from-green-600 hover:to-emerald-600 transition-all duration-200 font-medium text-sm"
            >
              <span className="hidden sm:inline">Export </span>Excel
            </button>
            <button
              onClick={() => exportAccounts('pdf')}
              className="bg-gradient-to-r from-red-500 to-pink-500 text-white px-3 sm:px-4 py-2 rounded-xl hover:from-red-600 hover:to-pink-600 transition-all duration-200 font-medium text-sm"
            >
              <span className="hidden sm:inline">Export </span>PDF
            </button>
            <button
              onClick={() => {
                setShowAddModal(true);
                fetchNextAccountCode('asset'); // Auto-fetch code for default asset type
              }}
              className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white px-3 sm:px-4 py-2 rounded-xl hover:from-blue-600 hover:to-indigo-600 transition-all duration-200 font-medium text-sm"
            >
              <span className="hidden sm:inline">Add </span>Account
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
              {/* Desktop Table View */}
              <div className="hidden md:block overflow-x-auto">
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
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{account.account_code || 'N/A'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{account.account_name || 'N/A'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 capitalize">{account.account_type || 'N/A'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 capitalize">{account.category?.replace('_', ' ') || 'N/A'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{account.current_balance || account.opening_balance || 0}</td>
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

              {/* Mobile Card View */}
              <div className="md:hidden divide-y divide-gray-200">
                {accounts.map((account) => (
                  <div key={account.id} className="p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-col space-y-1">
                          <div className="text-sm font-medium text-gray-900">
                            <span className="text-gray-500">Code:</span> {account.account_code || 'N/A'}
                          </div>
                          <div className="text-sm text-gray-900 break-words">
                            <span className="text-gray-500">Name:</span> {account.account_name || 'N/A'}
                          </div>
                        </div>
                      </div>
                      <div className="flex space-x-2 ml-4">
                        <button
                          onClick={() => startEditAccount(account)}
                          className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                          </svg>
                        </button>
                        <button
                          onClick={() => handleDeleteAccount(account.id)}
                          className="p-1 text-red-600 hover:bg-red-50 rounded"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                          </svg>
                        </button>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <span className="text-gray-500">Type:</span> 
                        <span className="ml-1 capitalize">{account.account_type || 'N/A'}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Category:</span> 
                        <span className="ml-1 capitalize">{account.category?.replace('_', ' ') || 'N/A'}</span>
                      </div>
                      <div className="col-span-2">
                        <span className="text-gray-500">Balance:</span> 
                        <span className="ml-1 font-medium">{account.current_balance || account.opening_balance || 0}</span>
                      </div>
                    </div>
                  </div>
                ))}
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
                      fetchNextAccountCode(type);
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
                  <label className="block text-sm font-medium text-gray-700 mb-2">Account Code</label>
                  <div className="relative">
                    <input
                      type="text"
                      value={accountForm.account_code}
                      onChange={(e) => setAccountForm({ ...accountForm, account_code: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Auto-generated based on account type"
                      required
                    />
                    {nextCodeLoading && (
                      <div className="absolute right-3 top-3">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                      </div>
                    )}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Code ranges: Assets (1000-1999), Liabilities (2000-2999), Equity (3000-3999), Revenue (4000-4999), Expenses (5000-5999)
                  </p>
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

const ConsolidatedAccountsTab = ({ companies, user }) => {
  const [consolidatedAccounts, setConsolidatedAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [groupBy, setGroupBy] = useState('account_type'); // account_type, company, category

  useEffect(() => {
    fetchConsolidatedAccounts();
  }, []);

  const fetchConsolidatedAccounts = async () => {
    setLoading(true);
    try {
      const backendUrl = window.location.origin;
      const response = await fetch(`${backendUrl}/api/companies/consolidated-accounts/enhanced`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setConsolidatedAccounts(data.consolidated_accounts || []);
      } else {
        setError('Failed to load consolidated accounts');
      }
    } catch (err) {
      setError('Connection failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const exportConsolidatedAccounts = async (format) => {
    try {
      const backendUrl = window.location.origin;
      const response = await fetch(`${backendUrl}/api/companies/consolidated-accounts/export`, {
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
          const { utils, writeFile } = await import('xlsx');
          const workbook = utils.book_new();
          
          // Prepare consolidated data for Excel
          const excelData = consolidatedAccounts.map(account => ({
            'Account Code': account.account_code || 'N/A',
            'Account Name': account.account_name || 'N/A',
            'Company': account.company_name || 'N/A',
            'Account Type': account.account_type || 'N/A',
            'Category': (account.category || 'N/A').replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
            'Current Balance': account.current_balance || 0
          }));
          
          const worksheet = utils.json_to_sheet(excelData);
          utils.book_append_sheet(workbook, worksheet, 'Consolidated Accounts');
          writeFile(workbook, data.filename || 'consolidated_accounts.xlsx');
        } else if (format === 'pdf') {
          // Create clean consolidated PDF
          await generateConsolidatedPDF(data.data);
        }
      } else {
        setError('Failed to export consolidated accounts');
      }
    } catch (err) {
      setError('Export failed: ' + err.message);
    }
  };

  const generateConsolidatedPDF = async (pdfData) => {
    try {
      const { jsPDF } = await import('jspdf');
      await import('jspdf-autotable');
      
      const doc = new jsPDF();
      const pageWidth = doc.internal.pageSize.width;
      
      // Header
      doc.setFontSize(20);
      doc.setFont('helvetica', 'bold');
      doc.text('Consolidated Chart of Accounts', pageWidth / 2, 20, { align: 'center' });
      
      // Export Date
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      doc.text(`Generated on: ${pdfData.export_date}`, pageWidth / 2, 30, { align: 'center' });
      
      // Prepare table data with company names
      const tableRows = consolidatedAccounts.map(account => [
        account.account_code || 'N/A',
        account.account_name || 'N/A',
        account.company_name || 'N/A',
        (account.account_type || 'N/A').charAt(0).toUpperCase() + (account.account_type || '').slice(1),
        (account.category || 'N/A').replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        `${account.current_balance || 0}`
      ]);
      
      // Table
      doc.autoTable({
        head: [['Account Code', 'Account Name', 'Company', 'Type', 'Category', 'Balance']],
        body: tableRows,
        startY: 40,
        theme: 'grid',
        headStyles: {
          fillColor: [59, 130, 246], // Blue color
          textColor: 255,
          fontStyle: 'bold'
        },
        styles: {
          fontSize: 7,
          cellPadding: 2
        },
        alternateRowStyles: {
          fillColor: [248, 250, 252] // Light gray
        },
        columnStyles: {
          0: { cellWidth: 25 }, // Account Code
          1: { cellWidth: 40 }, // Account Name
          2: { cellWidth: 35 }, // Company
          3: { cellWidth: 25 }, // Type
          4: { cellWidth: 30 }, // Category
          5: { cellWidth: 25 }  // Balance
        }
      });
      
      // Summary at bottom
      const finalY = doc.lastAutoTable.finalY + 10;
      doc.setFontSize(12);
      doc.setFont('helvetica', 'bold');
      doc.text('Summary', 14, finalY);
      
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      let summaryY = finalY + 8;
      doc.text(`Total Companies: ${pdfData.total_companies}`, 14, summaryY);
      doc.text(`Total Accounts: ${pdfData.total_accounts}`, 14, summaryY + 6);
      doc.text(`Assets: ${pdfData.summary.assets}`, 14, summaryY + 12);
      doc.text(`Liabilities: ${pdfData.summary.liabilities}`, 14, summaryY + 18);
      doc.text(`Equity: ${pdfData.summary.equity}`, 90, summaryY + 6);
      doc.text(`Revenue: ${pdfData.summary.revenue}`, 90, summaryY + 12);
      doc.text(`Expenses: ${pdfData.summary.expense}`, 90, summaryY + 18);
      
      // Save PDF
      doc.save('consolidated_chart_of_accounts.pdf');
    } catch (error) {
      console.error('Consolidated PDF generation failed:', error);
      setError('PDF generation failed: ' + error.message);
    }
  };

  const groupedAccounts = consolidatedAccounts.reduce((groups, account) => {
    let key;
    switch (groupBy) {
      case 'company':
        key = account.company_name || 'Unknown Company';
        break;
      case 'category':
        key = account.category || 'Other';
        break;
      default:
        key = account.account_type || 'Other';
    }
    
    if (!groups[key]) {
      groups[key] = [];
    }
    groups[key].push(account);
    return groups;
  }, {});

  const getTotalBalance = (accounts) => {
    return accounts.reduce((sum, account) => sum + (account.current_balance || 0), 0).toFixed(2);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Consolidated Accounts</h2>
          <p className="text-gray-600">View accounts from all companies in one consolidated view</p>
        </div>
        
        <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
          <select
            value={groupBy}
            onChange={(e) => setGroupBy(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            <option value="account_type">Group by Type</option>
            <option value="company">Group by Company</option>
            <option value="category">Group by Category</option>
          </select>
          
          <div className="flex space-x-2 sm:space-x-3">
            <button
              onClick={() => exportConsolidatedAccounts('excel')}
              className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-3 sm:px-4 py-2 rounded-xl hover:from-green-600 hover:to-emerald-600 transition-all duration-200 font-medium text-sm"
            >
              Excel
            </button>
            <button
              onClick={() => exportConsolidatedAccounts('pdf')}
              className="bg-gradient-to-r from-red-500 to-pink-500 text-white px-3 sm:px-4 py-2 rounded-xl hover:from-red-600 hover:to-pink-600 transition-all duration-200 font-medium text-sm"
            >
              PDF
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-lg">
          <span className="text-red-700 text-sm">{error}</span>
        </div>
      )}

      {loading ? (
        <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading consolidated accounts...</p>
        </div>
      ) : (
        <div className="space-y-6">
          {consolidatedAccounts.length === 0 ? (
            <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-8 text-center">
              <div className="text-gray-400 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">No Consolidated Accounts</h3>
              <p className="text-gray-500">No accounts found across companies. Create companies and accounts first.</p>
            </div>
          ) : (
            Object.entries(groupedAccounts).map(([groupName, accounts]) => (
              <div key={groupName} className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 overflow-hidden">
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 border-b border-gray-100">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-gray-900 capitalize">
                      {groupName.replace('_', ' ')}
                    </h3>
                    <div className="text-sm text-gray-600">
                      <span className="font-medium">{accounts.length} accounts</span>
                      <span className="mx-2">•</span>
                      <span className="font-medium">Total: {getTotalBalance(accounts)}</span>
                    </div>
                  </div>
                </div>
                
                {/* Desktop Table View */}
                <div className="hidden md:block overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Code</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Account Name</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Balance</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {accounts.map((account) => (
                        <tr key={`${account.company_id}-${account.id}`} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{account.account_code || 'N/A'}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{account.account_name || 'N/A'}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{account.company_name || 'N/A'}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 capitalize">{account.account_type || 'N/A'}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 capitalize">{account.category?.replace('_', ' ') || 'N/A'}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">{account.current_balance || 0}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Mobile Card View */}
                <div className="md:hidden divide-y divide-gray-200">
                  {accounts.map((account) => (
                    <div key={`${account.company_id}-${account.id}`} className="p-4 hover:bg-gray-50">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex flex-col space-y-1">
                            <div className="text-sm font-medium text-gray-900 break-words">
                              {account.account_name || 'N/A'}
                            </div>
                            <div className="text-xs text-gray-500">
                              Code: {account.account_code || 'N/A'}
                            </div>
                          </div>
                        </div>
                        <div className="text-sm font-medium text-gray-900 ml-4">
                          {account.current_balance || 0}
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div>
                          <span className="text-gray-500">Company:</span> 
                          <span className="ml-1 break-words">{account.company_name || 'N/A'}</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Type:</span> 
                          <span className="ml-1 capitalize">{account.account_type || 'N/A'}</span>
                        </div>
                        <div className="col-span-2">
                          <span className="text-gray-500">Category:</span> 
                          <span className="ml-1 capitalize">{account.category?.replace('_', ' ') || 'N/A'}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default CompanyManagement;