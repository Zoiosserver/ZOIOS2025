import React, { useState, useEffect } from 'react';

const SimpleCompanySetup = ({ user, onComplete }) => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [countries, setCountries] = useState([]);
  const [currencies, setCurrencies] = useState([]);
  const [accountingSystems, setAccountingSystems] = useState([]);
  
  const [formData, setFormData] = useState({
    company_name: user?.company || '',
    country: '',
    business_type: 'Private Limited Company',
    industry: '',
    fiscal_year_start: new Date().getFullYear() + '-04-01',
    accounting_system: '',
    base_currency: '',
    additional_currencies: []
  });

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      const backendUrl = window.location.origin;
      
      // Fetch countries
      const countriesRes = await fetch(`${backendUrl}/api/setup/countries`);
      if (countriesRes.ok) {
        const countriesData = await countriesRes.json();
        setCountries(countriesData);
      }

      // Fetch currencies
      const currenciesRes = await fetch(`${backendUrl}/api/currency/available`);
      if (currenciesRes.ok) {
        const currenciesData = await currenciesRes.json();
        setCurrencies(currenciesData);
      }

      // Fetch accounting systems
      const accountingRes = await fetch(`${backendUrl}/api/setup/accounting-systems`);
      if (accountingRes.ok) {
        const accountingData = await accountingRes.json();
        setAccountingSystems(accountingData);
      }
    } catch (err) {
      setError('Failed to load setup data: ' + err.message);
    }
  };

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
        onComplete();
      } else {
        const error = await response.json();
        setError(error.detail || 'Setup failed');
      }
    } catch (err) {
      setError('Connection failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    
    // Auto-set base currency when country changes
    if (name === 'country') {
      const country = countries.find(c => c.code === value);
      if (country) {
        setFormData(prev => ({ 
          ...prev, 
          [name]: value,
          base_currency: country.currency,
          accounting_system: country.accounting_systems?.[0] || ''
        }));
      }
    }
  };

  const handleCurrencyToggle = (currencyCode) => {
    setFormData(prev => ({
      ...prev,
      additional_currencies: prev.additional_currencies.includes(currencyCode)
        ? prev.additional_currencies.filter(c => c !== currencyCode)
        : [...prev.additional_currencies, currencyCode]
    }));
  };

  if (step === 1) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-2xl w-full space-y-8 p-6">
          <div>
            <h2 className="text-center text-3xl font-extrabold text-gray-900">
              Company Setup - Step 1
            </h2>
            <p className="text-center text-gray-600">Basic Company Information</p>
          </div>
          
          <form className="space-y-6" onSubmit={(e) => { e.preventDefault(); setStep(2); }}>
            {error && (
              <div className="bg-red-50 border border-red-300 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}
            
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
                <option value="">Select Country</option>
                {countries.map(country => (
                  <option key={country.code} value={country.code}>
                    {country.name} ({country.currency})
                  </option>
                ))}
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
                <option value="">Select Industry</option>
                <option value="Technology">Technology</option>
                <option value="Manufacturing">Manufacturing</option>
                <option value="Healthcare">Healthcare</option>
                <option value="Financial Services">Financial Services</option>
                <option value="Retail & E-commerce">Retail & E-commerce</option>
                <option value="Real Estate">Real Estate</option>
                <option value="Education">Education</option>
                <option value="Consulting">Consulting</option>
                <option value="Marketing & Advertising">Marketing & Advertising</option>
                <option value="Food & Beverage">Food & Beverage</option>
                <option value="Transportation & Logistics">Transportation & Logistics</option>
                <option value="Construction">Construction</option>
                <option value="Energy & Utilities">Energy & Utilities</option>
                <option value="Media & Entertainment">Media & Entertainment</option>
                <option value="Agriculture">Agriculture</option>
                <option value="Pharmaceuticals">Pharmaceuticals</option>
                <option value="Telecommunications">Telecommunications</option>
                <option value="Travel & Tourism">Travel & Tourism</option>
                <option value="Government">Government</option>
                <option value="Non-Profit">Non-Profit</option>
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
              />
            </div>

            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
            >
              Next: Currency & Accounting →
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-2xl w-full space-y-8 p-6">
        <div>
          <h2 className="text-center text-3xl font-extrabold text-gray-900">
            Company Setup - Step 2
          </h2>
          <p className="text-center text-gray-600">Currency & Accounting Configuration</p>
        </div>
        
        <form className="space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-300 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Accounting System</label>
            <select
              name="accounting_system"
              value={formData.accounting_system}
              onChange={handleChange}
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
              required
            >
              <option value="">Select Accounting System</option>
              {accountingSystems.map(system => (
                <option key={system.id} value={system.id}>
                  {system.name} - {system.description}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Base Currency</label>
            <select
              name="base_currency"
              value={formData.base_currency}
              onChange={handleChange}
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
              required
            >
              <option value="">Select Currency</option>
              {currencies.map(currency => (
                <option key={currency.code} value={currency.code}>
                  {currency.code} - {currency.symbol} - {currency.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Additional Currencies (Optional)
            </label>
            <div className="grid grid-cols-2 gap-3 max-h-60 overflow-y-auto border rounded-lg p-4">
              {currencies
                .filter(c => c.code !== formData.base_currency)
                .slice(0, 20) // Limit to first 20 for simplicity
                .map(currency => (
                <div
                  key={currency.code}
                  onClick={() => handleCurrencyToggle(currency.code)}
                  className={`p-3 border rounded cursor-pointer transition-colors ${
                    formData.additional_currencies.includes(currency.code)
                      ? 'bg-blue-50 border-blue-300'
                      : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="font-medium">{currency.symbol} {currency.code}</span>
                      <div className="text-xs text-gray-600">{currency.name}</div>
                    </div>
                    {formData.additional_currencies.includes(currency.code) && (
                      <span className="text-blue-600">✓</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {formData.additional_currencies.length > 0 && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded">
              <div className="text-sm font-medium text-blue-800">
                Selected Additional Currencies ({formData.additional_currencies.length})
              </div>
              <div className="flex flex-wrap gap-2 mt-2">
                {formData.additional_currencies.map(code => {
                  const currency = currencies.find(c => c.code === code);
                  return (
                    <span key={code} className="bg-white px-2 py-1 rounded border text-sm">
                      {currency?.symbol} {code}
                    </span>
                  );
                })}
              </div>
            </div>
          )}

          <div className="flex space-x-4">
            <button
              type="button"
              onClick={() => setStep(1)}
              className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700"
            >
              ← Back
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Setting up...' : 'Complete Setup'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SimpleCompanySetup;