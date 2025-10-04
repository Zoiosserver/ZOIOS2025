import React, { useState } from 'react';

const DemoCompanySetup = () => {
  const [formData, setFormData] = useState({
    company_name: 'Demo Group Company',
    country: 'US',
    business_type: 'Group Company',
    industry: 'Technology',
    fiscal_year_start: '2024-01-01',
    accounting_system: 'us_gaap',
    base_currency: 'USD',
    additional_currencies: [],
    sister_companies: [
      {
        id: 1,
        company_name: 'Sister Company A',
        country: 'IN',
        business_type: 'Private Limited Company',
        industry: 'Manufacturing',
        fiscal_year_start: '2024-04-01'
      }
    ],
    address: {
      street_address: '123 Business Street',
      city: 'Tech City',
      state: 'California',
      postal_code: '90210',
      country: 'US'
    }
  });

  const [sisterCompanyData, setSisterCompanyData] = useState({
    company_name: '',
    country: 'IN',
    business_type: 'Private Limited Company',
    industry: 'Technology',
    fiscal_year_start: '2024-04-01'
  });

  const [showSisterCompanyForm, setShowSisterCompanyForm] = useState(true);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="relative max-w-4xl w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
            ZOIOS ERP
          </h1>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Company Setup</h2>
          <p className="text-gray-600">Complete your company information with sister companies</p>
        </div>

        <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl border border-gray-100/50 p-8">
          {/* Basic Company Info */}
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <h3 className="text-lg font-medium mb-4">Company Information</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Company Name</label>
                <input
                  type="text"
                  value={formData.company_name}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100"
                  disabled
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Country</label>
                <select
                  value={formData.country}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100"
                  disabled
                >
                  <option value="US">United States (USD)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Business Type</label>
                <select
                  value={formData.business_type}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md bg-blue-100 font-medium"
                  disabled
                >
                  <option value="Group Company">Group Company</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Industry</label>
                <select
                  value={formData.industry}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100"
                  disabled
                >
                  <option value="Technology">Technology</option>
                </select>
              </div>
            </div>
          </div>

          {/* Sister Companies Section */}
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
                {showSisterCompanyForm ? 'Hide Form' : 'Add Sister Company'}
              </button>
            </div>

            {/* Sister Companies List */}
            {formData.sister_companies.length > 0 && (
              <div className="mb-4">
                <h5 className="font-medium text-gray-700 mb-2">Added Sister Companies:</h5>
                <div className="space-y-2">
                  {formData.sister_companies.map((company) => (
                    <div key={company.id} className="flex items-center justify-between bg-white p-3 rounded border shadow-sm">
                      <div>
                        <span className="font-medium text-blue-900">{company.company_name}</span>
                        <span className="text-gray-500 ml-2">({company.country} - {company.industry})</span>
                      </div>
                      <span className="text-green-600 text-sm">✓ Active</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Sister Company Form */}
            {showSisterCompanyForm && (
              <div className="bg-white p-4 rounded-lg border shadow-sm">
                <h5 className="font-medium mb-3 text-gray-800">Add New Sister Company</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Company Name</label>
                    <input
                      type="text"
                      name="company_name"
                      value={sisterCompanyData.company_name}
                      className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Sister company name"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Country</label>
                    <select
                      name="country"
                      value={sisterCompanyData.country}
                      className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                      className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                      className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                      className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div className="mt-4 flex space-x-2">
                  <button
                    type="button"
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

          <div className="mt-6 text-center">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="text-green-800 font-medium mb-2">✅ Sister Company Feature Available!</h4>
              <p className="text-green-700 text-sm">
                When you select "Group Company" as your business type, the sister company section will appear automatically. 
                You can add multiple sister companies with their own details and manage them as part of your group.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DemoCompanySetup;