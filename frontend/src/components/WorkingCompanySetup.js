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

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-2xl w-full space-y-8 p-6">
        <div>
          <h2 className="text-center text-3xl font-extrabold text-gray-900">
            Company Setup
          </h2>
          <p className="text-center text-gray-600">Complete your company information</p>
        </div>
        
        <form className="space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-300 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          
          {/* Basic Info */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium mb-4">Company Information</h3>
            
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