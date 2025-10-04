import React, { useState } from 'react';

const WorkingCompanySetup = ({ user, onComplete }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showSisterCompanyForm, setShowSisterCompanyForm] = useState(false);
  
  const [formData, setFormData] = useState({
    company_name: user?.company || '',
    country: 'IN',
    business_type: 'Private Limited Company',
    industry: 'Technology',
    fiscal_year_start: '2024-04-01',
    accounting_system: 'indian_gaap',
    base_currency: 'INR',
    additional_currencies: [],
    sister_companies: [],
    address: {
      street_address: '',
      city: '',
      state: '',
      postal_code: '',
      country: 'IN'
    }
  });

  const [sisterCompanyData, setSisterCompanyData] = useState({
    company_name: '',
    country: 'IN',
    business_type: 'Private Limited Company',
    industry: 'Technology',
    fiscal_year_start: '2024-04-01'
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const backendUrl = window.location.origin;
      
      const response = await fetch(`${backendUrl}/api/setup/company`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        alert('Company setup completed successfully!');
        onComplete();
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || 'Setup failed');
      }
    } catch (err) {
      setError('Connection failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name.startsWith('address.')) {
      const addressField = name.split('.')[1];
      setFormData(prev => ({
        ...prev,
        address: { ...prev.address, [addressField]: value }
      }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleSisterCompanyChange = (e) => {
    const { name, value } = e.target;
    setSisterCompanyData(prev => ({ ...prev, [name]: value }));
  };

  const addSisterCompany = () => {
    if (sisterCompanyData.company_name.trim()) {
      setFormData(prev => ({
        ...prev,
        sister_companies: [...prev.sister_companies, { ...sisterCompanyData, id: Date.now() }]
      }));
      setSisterCompanyData({
        company_name: '',
        country: 'IN',
        business_type: 'Private Limited Company',
        industry: 'Technology',
        fiscal_year_start: '2024-04-01'
      });
      setShowSisterCompanyForm(false);
    }
  };

  const removeSisterCompany = (id) => {
    setFormData(prev => ({
      ...prev,
      sister_companies: prev.sister_companies.filter(comp => comp.id !== id)
    }));
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-green-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse delay-1000"></div>
      </div>

      <div className="relative max-w-4xl w-full">
        {/* Logo/Brand Section with Logout */}
        <div className="text-center mb-8 relative">
          <div className="inline-block bg-gradient-to-r from-green-600 to-blue-600 p-4 rounded-2xl shadow-lg mb-6">
            <svg className="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M3 6l3 1v13l-3-1V6zm6 0l3 1v13l-3-1V6zm6 0l3 1v13l-3-1V6zm3-3v2H6V3h12zM6 21h12v2H6v-2z"/>
            </svg>
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent mb-2">
            ZOIOS ERP
          </h1>
          <p className="text-gray-600 text-lg mb-4">Complete Your Company Setup</p>
          
          {/* Logout Button */}
          <button
            onClick={handleLogout}
            className="absolute top-0 right-0 bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition-colors text-sm"
          >
            Logout & Continue Later
          </button>
        </div>
        
        {/* Main Setup Card */}
        <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl border border-gray-100/50 p-8">
          <form className="space-y-8" onSubmit={handleSubmit}>
            {error && (
              <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-lg animate-shake">
                <div className="flex">
                  <svg className="w-5 h-5 text-red-400 mr-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd"/>
                  </svg>
                  <span className="text-red-700 text-sm">{error}</span>
                </div>
              </div>
            )}
            
            {/* Step Indicator */}
            <div className="flex items-center justify-center mb-8">
              <div className="flex items-center space-x-4">
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-medium">
                    1
                  </div>
                  <span className="ml-2 text-sm font-medium text-green-600">Company Details</span>
                </div>
                <div className="w-8 h-0.5 bg-green-500"></div>
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-medium">
                    2
                  </div>
                  <span className="ml-2 text-sm font-medium text-green-600">Address & Completion</span>
                </div>
              </div>
            </div>
            
            {/* Basic Info */}
            <div className="bg-gradient-to-r from-blue-50 to-green-50 p-6 rounded-2xl border border-blue-200">
              <div className="flex items-center mb-4">
                <svg className="w-6 h-6 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 110 2h-3a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H4a1 1 0 110-2V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z" clipRule="evenodd"/>
                </svg>
                <h3 className="text-xl font-semibold text-gray-900">Company Information</h3>
              </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Company Name</label>
                <input
                  type="text"
                  name="company_name"
                  value={formData.company_name}
                  onChange={handleChange}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Country</label>
                <select
                  name="country"
                  value={formData.country}
                  onChange={handleChange}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                  required
                >
                  <option value="IN">India (INR)</option>
                  <option value="US">United States (USD)</option>
                  <option value="GB">United Kingdom (GBP)</option>
                  <option value="CA">Canada (CAD)</option>
                  <option value="AU">Australia (AUD)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Business Type</label>
                <select
                  name="business_type"
                  value={formData.business_type}
                  onChange={handleChange}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="Private Limited Company">Private Limited Company</option>
                  <option value="Group Company">Group Company</option>
                  <option value="Public Limited Company">Public Limited Company</option>
                  <option value="Partnership">Partnership</option>
                  <option value="Sole Proprietorship">Sole Proprietorship</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Industry</label>
                <select
                  name="industry"
                  value={formData.industry}
                  onChange={handleChange}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                  required
                >
                  <option value="Technology">Technology</option>
                  <option value="Manufacturing">Manufacturing</option>
                  <option value="Healthcare">Healthcare</option>
                  <option value="Financial Services">Financial Services</option>
                  <option value="Retail & E-commerce">Retail & E-commerce</option>
                  <option value="Elevator & Escalator">Elevator & Escalator</option>
                  <option value="Real Estate">Real Estate</option>
                  <option value="Education">Education</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Fiscal Year Start</label>
                <input
                  type="date"
                  name="fiscal_year_start"
                  value={formData.fiscal_year_start}
                  onChange={handleChange}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                  required
                />
              </div>
            </div>

            {/* Sister Companies Section - Only show when Group Company is selected */}
            {formData.business_type === 'Group Company' && (
              <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h4 className="text-lg font-medium text-blue-900">Sister Companies</h4>
                    <p className="text-sm text-blue-700">Add sister companies that are part of your group</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setShowSisterCompanyForm(!showSisterCompanyForm)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                  >
                    Add Sister Company
                  </button>
                </div>

                {/* Sister Companies List */}
                {formData.sister_companies.length > 0 && (
                  <div className="mb-4">
                    <h5 className="font-medium text-gray-700 mb-2">Added Sister Companies:</h5>
                    <div className="space-y-2">
                      {formData.sister_companies.map((company) => (
                        <div key={company.id} className="flex items-center justify-between bg-white p-3 rounded border">
                          <div>
                            <span className="font-medium">{company.company_name}</span>
                            <span className="text-gray-500 ml-2">({company.country} - {company.industry})</span>
                          </div>
                          <button
                            type="button"
                            onClick={() => removeSisterCompany(company.id)}
                            className="text-red-600 hover:text-red-800"
                          >
                            Remove
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Sister Company Form */}
                {showSisterCompanyForm && (
                  <div className="bg-white p-4 rounded-lg border">
                    <h5 className="font-medium mb-3">Add New Sister Company</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Company Name</label>
                        <input
                          type="text"
                          name="company_name"
                          value={sisterCompanyData.company_name}
                          onChange={handleSisterCompanyChange}
                          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                          placeholder="Sister company name"
                          required
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Country</label>
                        <select
                          name="country"
                          value={sisterCompanyData.country}
                          onChange={handleSisterCompanyChange}
                          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                          <option value="IN">India (INR)</option>
                          <option value="US">United States (USD)</option>
                          <option value="GB">United Kingdom (GBP)</option>
                          <option value="CA">Canada (CAD)</option>
                          <option value="AU">Australia (AUD)</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">Business Type</label>
                        <select
                          name="business_type"
                          value={sisterCompanyData.business_type}
                          onChange={handleSisterCompanyChange}
                          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                          <option value="Private Limited Company">Private Limited Company</option>
                          <option value="Public Limited Company">Public Limited Company</option>
                          <option value="Partnership">Partnership</option>
                          <option value="Sole Proprietorship">Sole Proprietorship</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">Industry</label>
                        <select
                          name="industry"
                          value={sisterCompanyData.industry}
                          onChange={handleSisterCompanyChange}
                          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                          <option value="Technology">Technology</option>
                          <option value="Manufacturing">Manufacturing</option>
                          <option value="Healthcare">Healthcare</option>
                          <option value="Financial Services">Financial Services</option>
                          <option value="Retail & E-commerce">Retail & E-commerce</option>
                          <option value="Elevator & Escalator">Elevator & Escalator</option>
                          <option value="Real Estate">Real Estate</option>
                          <option value="Education">Education</option>
                          <option value="Other">Other</option>
                        </select>
                      </div>

                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700">Fiscal Year Start</label>
                        <input
                          type="date"
                          name="fiscal_year_start"
                          value={sisterCompanyData.fiscal_year_start}
                          onChange={handleSisterCompanyChange}
                          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                        />
                      </div>
                    </div>

                    <div className="mt-4 flex space-x-2">
                      <button
                        type="button"
                        onClick={addSisterCompany}
                        className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
                      >
                        Add Company
                      </button>
                      <button
                        type="button"
                        onClick={() => setShowSisterCompanyForm(false)}
                        className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Currency & Accounting */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium mb-4">Currency & Accounting</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Base Currency</label>
                <select
                  name="base_currency"
                  value={formData.base_currency}
                  onChange={handleChange}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                  required
                >
                  <option value="INR">INR - ₹ - Indian Rupee</option>
                  <option value="USD">USD - $ - US Dollar</option>
                  <option value="EUR">EUR - € - Euro</option>
                  <option value="GBP">GBP - £ - British Pound</option>
                  <option value="JPY">JPY - ¥ - Japanese Yen</option>
                  <option value="CAD">CAD - C$ - Canadian Dollar</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Accounting System</label>
                <select
                  name="accounting_system"
                  value={formData.accounting_system}
                  onChange={handleChange}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                  required
                >
                  <option value="indian_gaap">Indian GAAP / Ind AS</option>
                  <option value="us_gaap">US GAAP</option>
                  <option value="ifrs">IFRS</option>
                  <option value="uk_gaap">UK GAAP</option>
                  <option value="canadian_gaap">Canadian GAAP</option>
                </select>
              </div>
            </div>
          </div>

          {/* Address */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium mb-4">Company Address</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Street Address</label>
                <textarea
                  name="address.street_address"
                  value={formData.address.street_address}
                  onChange={handleChange}
                  placeholder="Enter complete street address"
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                  rows={2}
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">City</label>
                  <input
                    type="text"
                    name="address.city"
                    value={formData.address.city}
                    onChange={handleChange}
                    placeholder="City"
                    className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">State/Province</label>
                  <input
                    type="text"
                    name="address.state"
                    value={formData.address.state}
                    onChange={handleChange}
                    placeholder="State or Province"
                    className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Postal Code</label>
                  <input
                    type="text"
                    name="address.postal_code"
                    value={formData.address.postal_code}
                    onChange={handleChange}
                    placeholder="Postal Code"
                    className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Country</label>
                  <select
                    name="address.country"
                    value={formData.address.country}
                    onChange={handleChange}
                    className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                    required
                  >
                    <option value="IN">India</option>
                    <option value="US">United States</option>
                    <option value="GB">United Kingdom</option>
                    <option value="CA">Canada</option>
                    <option value="AU">Australia</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-green-600 text-white py-3 px-4 rounded-md hover:bg-green-700 disabled:opacity-50 font-medium"
          >
            {loading ? 'Setting up company...' : 'Complete Company Setup'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default WorkingCompanySetup;