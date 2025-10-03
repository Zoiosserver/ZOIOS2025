import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { 
  Building, 
  Globe, 
  CreditCard, 
  Settings, 
  MapPin, 
  Phone, 
  Mail,
  ChevronRight,
  ChevronLeft,
  CheckCircle,
  AlertCircle,
  Info,
  Plus
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CompanySetup = () => {
  const { user, refreshUser } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [countries, setCountries] = useState([]);
  const [currencies, setCurrencies] = useState([]);
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [accountingSystem, setAccountingSystem] = useState(null);
  const [sisterCompanies, setSisterCompanies] = useState([]);
  const [showSisterCompanyForm, setShowSisterCompanyForm] = useState(false);
  const [editingSisterCompanyId, setEditingSisterCompanyId] = useState(null);
  const [sisterCompanyAccountingSystem, setSisterCompanyAccountingSystem] = useState(null);
  const [sisterCompanyForm, setSisterCompanyForm] = useState({
    company_name: '',
    country_code: '',
    base_currency: '',
    accounting_system: '',
    business_type: '',
    industry: '',
    ownership_percentage: 100,
    fiscal_year_start: ''  // Format: MM-DD
  });

  const [formData, setFormData] = useState({
    // Step 1: Company Basic Info
    company_name: user?.company || '',
    country_code: '',
    business_type: '',
    industry: '',
    
    // Step 2: Accounting & Currency
    base_currency: '',
    additional_currencies: [],
    fiscal_year_start: '',  // Format: MM-DD (e.g., "01-01" for January 1st)
    
    // Step 3: Company Details
    address: '',
    city: '',
    state: '',
    postal_code: '',
    phone: '',
    email: user?.email || '',
    website: '',
    tax_number: '',
    registration_number: ''
  });

  const businessTypes = [
    'Sole Proprietorship',
    'Partnership', 
    'Private Limited Company',
    'Limited Liability Company (LLC)',
    'Corporation',
    'S Corporation',
    'Group Company',
    'Nonprofit Organization',
    'Other'
  ];

  const industries = [
    'Technology & Software',
    'Healthcare & Medical',
    'Financial Services',
    'Manufacturing',
    'Retail & E-commerce',
    'Professional Services',
    'Real Estate',
    'Education',
    'Transportation & Logistics',
    'Food & Beverage',
    'Construction',
    'Agriculture',
    'Entertainment & Media',
    'Energy & Utilities',
    'Elevators & Escalators',
    'Other'
  ];

  useEffect(() => {
    fetchCountries();
    fetchCurrencies();
  }, []);

  useEffect(() => {
    if (formData.country_code) {
      fetchAccountingSystem(formData.country_code);
    }
  }, [formData.country_code]);

  useEffect(() => {
    // Set selectedCountry when countries are loaded and there's a country_code
    if (countries.length > 0 && formData.country_code && !selectedCountry) {
      const country = countries.find(c => c.code === formData.country_code);
      if (country) {
        setSelectedCountry(country);
      }
    }
  }, [countries, formData.country_code]);

  const fetchCountries = async () => {
    try {
      const response = await axios.get(`${API}/setup/countries`);
      setCountries(response.data);
    } catch (error) {
      console.error('Error fetching countries:', error);
      toast.error('Failed to load countries');
    }
  };

  const fetchCurrencies = async () => {
    try {
      const response = await axios.get(`${API}/setup/currencies`);
      setCurrencies(response.data);
    } catch (error) {
      console.error('Error fetching currencies:', error);
      toast.error('Failed to load currencies');
    }
  };

  const fetchAccountingSystem = async (countryCode) => {
    try {
      const response = await axios.get(`${API}/setup/accounting-system/${countryCode}`);
      setAccountingSystem(response.data);
      
      // Auto-set base currency based on country
      if (response.data.currency && !formData.base_currency) {
        setFormData(prev => ({
          ...prev,
          base_currency: response.data.currency
        }));
      }
    } catch (error) {
      console.error('Error fetching accounting system:', error);
    }
  };

  const fetchSisterCompanyAccountingSystem = async (countryCode) => {
    try {
      const response = await axios.get(`${API}/setup/accounting-system/${countryCode}`);
      setSisterCompanyAccountingSystem(response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching sister company accounting system:', error);
      return null;
    }
  };

  const handleCountryChange = (countryCode) => {
    const country = countries.find(c => c.code === countryCode);
    setSelectedCountry(country);
    setFormData(prev => ({
      ...prev,
      country_code: countryCode,
      base_currency: country?.currency || ''
    }));
  };

  const handleCurrencyToggle = (currencyCode) => {
    if (currencyCode === formData.base_currency) return; // Can't remove base currency
    
    const newAdditionalCurrencies = formData.additional_currencies.includes(currencyCode)
      ? formData.additional_currencies.filter(c => c !== currencyCode)
      : [...formData.additional_currencies, currencyCode];
    
    setFormData(prev => ({
      ...prev,
      additional_currencies: newAdditionalCurrencies
    }));
  };

  const validateStep = (step) => {
    switch (step) {
      case 1:
        if (!formData.company_name || !formData.country_code || !formData.business_type || !formData.industry) {
          setError('Please fill in all required fields');
          return false;
        }
        break;
      case 2:
        if (!formData.base_currency) {
          setError('Please select a base currency');
          return false;
        }
        break;
      case 3:
        // Step 3 fields are optional, but we could add validation if needed
        break;
      default:
        break;
    }
    setError('');
    return true;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, 3));
    }
  };

  const handlePrevious = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
    setError('');
  };

  const handleSubmit = async () => {
    if (!validateStep(3)) return;

    setLoading(true);
    setError('');

    try {
      await axios.post(`${API}/setup/company`, formData);
      toast.success('Company setup completed successfully!');
      
      // If this is a group company with sister companies, save them now
      if (formData.business_type === 'Group Company' && sisterCompanies.length > 0) {
        try {
          const sisterCompanyPromises = sisterCompanies.map(company => 
            axios.post(`${API}/company/sister-companies`, {
              company_name: company.company_name,
              country_code: company.country_code,
              base_currency: company.base_currency,
              accounting_system: company.accounting_system,
              business_type: company.business_type,
              industry: company.industry,
              ownership_percentage: company.ownership_percentage,
              fiscal_year_start: company.fiscal_year_start
            })
          );
          
          await Promise.all(sisterCompanyPromises);
          toast.success(`Added ${sisterCompanies.length} sister companies successfully!`);
        } catch (sisterError) {
          console.error('Error saving sister companies:', sisterError);
          toast.error('Main setup completed, but some sister companies failed to save. You can add them later from the consolidated accounts page.');
        }
      }
      
      // Refresh user data to get updated onboarding_completed status
      const refreshResult = await refreshUser();
      if (!refreshResult.success) {
        console.error('Failed to refresh user data:', refreshResult.error);
        toast.error('Setup completed but failed to refresh user data. Please refresh the page.');
      }
      
    } catch (error) {
      console.error('Error setting up company:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to setup company';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const addSisterCompany = () => {
    if (!sisterCompanyForm.company_name || !sisterCompanyForm.country_code || !sisterCompanyForm.business_type || !sisterCompanyForm.industry) {
      toast.error('Please fill in all required fields for sister company');
      return;
    }

    if (editingSisterCompanyId) {
      // Update existing sister company
      setSisterCompanies(sisterCompanies.map(company => 
        company.id === editingSisterCompanyId 
          ? { ...company, ...sisterCompanyForm, updated_at: new Date().toISOString() }
          : company
      ));
      toast.success('Sister company updated successfully!');
      setEditingSisterCompanyId(null);
    } else {
      // Add new sister company to local state (will be saved when main setup completes)
      const newSisterCompany = {
        id: `temp-${Date.now()}`, // Temporary ID
        ...sisterCompanyForm,
        created_at: new Date().toISOString()
      };
      
      setSisterCompanies([...sisterCompanies, newSisterCompany]);
      toast.success('Sister company added to setup!');
    }
    
    // Reset form
    setSisterCompanyForm({
      company_name: '',
      country_code: '',
      base_currency: '',
      accounting_system: '',
      business_type: '',
      industry: '',
      ownership_percentage: 100,
      fiscal_year_start: ''
    });
    setSisterCompanyAccountingSystem(null);
    setShowSisterCompanyForm(false);
  };

  const editSisterCompany = (companyId) => {
    const companyToEdit = sisterCompanies.find(company => company.id === companyId);
    if (companyToEdit) {
      setSisterCompanyForm({
        company_name: companyToEdit.company_name,
        country_code: companyToEdit.country_code,
        base_currency: companyToEdit.base_currency,
        accounting_system: companyToEdit.accounting_system || '',
        business_type: companyToEdit.business_type,
        industry: companyToEdit.industry,
        ownership_percentage: companyToEdit.ownership_percentage,
        fiscal_year_start: companyToEdit.fiscal_year_start || ''
      });
      
      // If there's a country code, fetch the accounting system
      if (companyToEdit.country_code) {
        fetchSisterCompanyAccountingSystem(companyToEdit.country_code);
      }
      
      setEditingSisterCompanyId(companyId);
      setShowSisterCompanyForm(true);
    }
  };

  const cancelEdit = () => {
    setEditingSisterCompanyId(null);
    setSisterCompanyForm({
      company_name: '',
      country_code: '',
      base_currency: '',
      accounting_system: '',
      business_type: '',
      industry: '',
      ownership_percentage: 100,
      fiscal_year_start: ''
    });
    setSisterCompanyAccountingSystem(null);
    setShowSisterCompanyForm(false);
  };

  const removeSisterCompany = (companyId) => {
    setSisterCompanies(sisterCompanies.filter(company => company.id !== companyId));
    toast.success('Sister company removed from setup!');
  };

  const renderStepIndicator = () => (
    <div className="flex items-center justify-center mb-8">
      {[1, 2, 3].map((step) => (
        <div key={step} className="flex items-center">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center font-medium ${
            step <= currentStep 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-200 text-gray-500'
          }`}>
            {step < currentStep ? <CheckCircle className="w-5 h-5" /> : step}
          </div>
          {step < 3 && (
            <div className={`w-8 h-1 mx-2 ${
              step < currentStep ? 'bg-blue-600' : 'bg-gray-200'
            }`} />
          )}
        </div>
      ))}
    </div>
  );

  const renderStep1 = () => (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <Building className="w-12 h-12 text-blue-600 mx-auto mb-3" />
        <h2 className="text-2xl font-bold text-gray-900">Company Information</h2>
        <p className="text-gray-600">Let's start with your basic company details</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="md:col-span-2">
          <Label htmlFor="company_name">Company Name *</Label>
          <Input
            id="company_name"
            tabIndex={1}
            value={formData.company_name}
            onChange={(e) => setFormData(prev => ({...prev, company_name: e.target.value}))}
            placeholder="Enter your company name"
            required
          />
        </div>

        <div className="md:col-span-2">
          <Label htmlFor="country">Country *</Label>
          <Select value={formData.country_code} onValueChange={handleCountryChange}>
            <SelectTrigger className="w-full" tabIndex={2}>
              <div className="flex items-center justify-between w-full">
                {selectedCountry ? (
                  <>
                    <span className="flex-1 text-left truncate">{selectedCountry.name}</span>
                    <span className="text-xs text-gray-500 ml-2 flex-shrink-0">({selectedCountry.currency})</span>
                  </>
                ) : (
                  <span className="text-gray-500">Select your country</span>
                )}
              </div>
            </SelectTrigger>
            <SelectContent className="min-w-[400px] w-auto max-h-[200px] overflow-y-auto">
              {countries.map(country => (
                <SelectItem 
                  key={country.code} 
                  value={country.code}
                  className="cursor-pointer"
                >
                  <div className="flex items-center w-full">
                    <span className="flex-1">{country.name}</span>
                    <span className="text-xs text-gray-500 ml-2">({country.currency})</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {selectedCountry && (
            <p className="text-xs text-blue-600 mt-1">
              Accounting System: {selectedCountry.accounting_system}
            </p>
          )}
        </div>

        <div className="md:col-span-2">
          <Label htmlFor="business_type">Business Type *</Label>
          <Select value={formData.business_type} onValueChange={(value) => setFormData(prev => ({...prev, business_type: value}))}>
            <SelectTrigger className="w-full" tabIndex={3}>
              <SelectValue placeholder="Select business type" />
            </SelectTrigger>
            <SelectContent className="min-w-[300px] w-auto">
              {businessTypes.map(type => (
                <SelectItem key={type} value={type}>{type}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="md:col-span-2">
          <Label htmlFor="industry">Industry *</Label>
          <Select value={formData.industry} onValueChange={(value) => setFormData(prev => ({...prev, industry: value}))}>
            <SelectTrigger tabIndex={4}>
              <SelectValue placeholder="Select your industry" />
            </SelectTrigger>
            <SelectContent>
              {industries.map(industry => (
                <SelectItem key={industry} value={industry}>{industry}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {accountingSystem && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            <strong>Accounting System:</strong> {accountingSystem.name} <br />
            <strong>Fiscal Year:</strong> Starts {accountingSystem.fiscal_year_start} <br />
            <strong>Base Currency:</strong> {accountingSystem.currency}
          </AlertDescription>
        </Alert>
      )}

      {/* Sister Companies Section for Group Companies */}
      {formData.business_type === 'Group Company' && (
        <div className="mt-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">Sister Companies</h3>
            <Button
              type="button"
              size="sm"
              tabIndex={0}
              onClick={() => {
                if (editingSisterCompanyId) {
                  cancelEdit();
                } else {
                  setShowSisterCompanyForm(!showSisterCompanyForm);
                }
              }}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white"
            >
              <Plus className="w-4 h-4" />
              {editingSisterCompanyId ? 'Cancel Edit' : 'Add Sister Company'}
            </Button>
          </div>

          {/* Sister Company Form */}
          {showSisterCompanyForm && (
            <Card className="p-4">
              <h4 className="text-md font-semibold text-gray-900 mb-4">
                {editingSisterCompanyId ? 'Edit Sister Company' : 'Add New Sister Company'}
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="sister_company_name">Company Name *</Label>
                  <Input
                    id="sister_company_name"
                    tabIndex={1}
                    value={sisterCompanyForm.company_name}
                    onChange={(e) => setSisterCompanyForm(prev => ({...prev, company_name: e.target.value}))}
                    placeholder="Enter sister company name"
                  />
                </div>
                
                <div>
                  <Label htmlFor="sister_country">Country *</Label>
                  <Select
                    value={sisterCompanyForm.country_code}
                    onValueChange={async (value) => {
                      const country = countries.find(c => c.code === value);
                      
                      // Fetch accounting system for the selected country
                      const accountingSystemData = await fetchSisterCompanyAccountingSystem(value);
                      
                      setSisterCompanyForm(prev => ({
                        ...prev,
                        country_code: value,
                        base_currency: country?.currency || '',
                        accounting_system: accountingSystemData?.name || ''
                      }));
                    }}
                  >
                    <SelectTrigger className="w-full" tabIndex={2}>
                      <div className="flex items-center justify-between w-full">
                        {sisterCompanyForm.country_code ? (
                          <>
                            <span className="flex-1 text-left truncate">
                              {countries.find(c => c.code === sisterCompanyForm.country_code)?.name || 'Unknown'}
                            </span>
                            <span className="text-xs text-gray-500 ml-2 flex-shrink-0">
                              ({countries.find(c => c.code === sisterCompanyForm.country_code)?.currency || ''})
                            </span>
                          </>
                        ) : (
                          <span className="text-gray-500">Select country</span>
                        )}
                      </div>
                    </SelectTrigger>
                    <SelectContent className="min-w-[400px] w-auto max-h-[200px] overflow-y-auto">
                      {countries.map(country => (
                        <SelectItem key={country.code} value={country.code} className="cursor-pointer">
                          <div className="flex items-center w-full">
                            <span className="flex-1">{country.name}</span>
                            <span className="text-xs text-gray-500 ml-2">({country.currency})</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="sister_business_type">Business Type *</Label>
                  <Select
                    value={sisterCompanyForm.business_type}
                    onValueChange={(value) => setSisterCompanyForm(prev => ({...prev, business_type: value}))}
                  >
                    <SelectTrigger tabIndex={3}>
                      <SelectValue placeholder="Select business type" />
                    </SelectTrigger>
                    <SelectContent>
                      {businessTypes.filter(type => type !== 'Group Company').map(type => (
                        <SelectItem key={type} value={type}>{type}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="sister_industry">Industry *</Label>
                  <Select
                    value={sisterCompanyForm.industry}
                    onValueChange={(value) => setSisterCompanyForm(prev => ({...prev, industry: value}))}
                  >
                    <SelectTrigger tabIndex={4}>
                      <SelectValue placeholder="Select industry" />
                    </SelectTrigger>
                    <SelectContent>
                      {industries.map(industry => (
                        <SelectItem key={industry} value={industry}>{industry}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="ownership_percentage">Ownership Percentage</Label>
                  <Input
                    id="ownership_percentage"
                    tabIndex={5}
                    type="number"
                    min="0"
                    max="100"
                    value={sisterCompanyForm.ownership_percentage}
                    onChange={(e) => setSisterCompanyForm(prev => ({...prev, ownership_percentage: parseFloat(e.target.value)}))}
                    placeholder="100"
                  />
                </div>

                <div>
                  <Label htmlFor="sister_fiscal_year_start">Fiscal Year Start Date *</Label>
                  <Select value={sisterCompanyForm.fiscal_year_start} onValueChange={(value) => setSisterCompanyForm(prev => ({...prev, fiscal_year_start: value}))}>
                    <SelectTrigger tabIndex={6}>
                      <SelectValue placeholder="Select fiscal year start" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="01-01">January 1st</SelectItem>
                      <SelectItem value="04-01">April 1st</SelectItem>
                      <SelectItem value="07-01">July 1st</SelectItem>
                      <SelectItem value="10-01">October 1st</SelectItem>
                      <SelectItem value="01-04">January 4th</SelectItem>
                      <SelectItem value="custom">Custom Date</SelectItem>
                    </SelectContent>
                  </Select>
                  {sisterCompanyForm.fiscal_year_start === 'custom' && (
                    <div className="mt-2">
                      <Input
                        tabIndex={7}
                        placeholder="MM-DD (e.g., 03-15)"
                        pattern="[0-1][0-9]-[0-3][0-9]"
                        onChange={(e) => setSisterCompanyForm(prev => ({...prev, fiscal_year_start: e.target.value}))}
                      />
                    </div>
                  )}
                </div>

                {/* Accounting System Display for Sister Company */}
                {sisterCompanyAccountingSystem && sisterCompanyForm.country_code && (
                  <div className="md:col-span-2">
                    <Alert>
                      <Info className="h-4 w-4" />
                      <AlertDescription>
                        <strong>Accounting System:</strong> {sisterCompanyAccountingSystem.name} <br />
                        <strong>Base Currency:</strong> {sisterCompanyForm.base_currency} <br />
                        <strong>Fiscal Year:</strong> Starts {sisterCompanyAccountingSystem.fiscal_year_start}
                      </AlertDescription>
                    </Alert>
                  </div>
                )}

                <div className="md:col-span-2 flex gap-2">
                  <Button 
                    type="button" 
                    tabIndex={8}
                    onClick={addSisterCompany} 
                    disabled={loading}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    {loading ? 
                      (editingSisterCompanyId ? 'Updating...' : 'Adding...') : 
                      (editingSisterCompanyId ? 'Update Company' : 'Add Company')
                    }
                  </Button>
                  <Button
                    type="button"
                    tabIndex={9}
                    variant="outline"
                    onClick={cancelEdit}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </Card>
          )}

          {/* Sister Companies List */}
          {sisterCompanies.length > 0 && (
            <div className="space-y-2">
              {sisterCompanies.map(company => (
                <Card key={company.id} className="p-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">{company.company_name}</h4>
                      <p className="text-sm text-gray-600">
                        {countries.find(c => c.code === company.country_code)?.name} • {company.business_type} • {company.ownership_percentage}% owned
                      </p>
                      {company.accounting_system && (
                        <p className="text-xs text-blue-600">
                          Accounting: {company.accounting_system} • Currency: {company.base_currency}
                          {company.fiscal_year_start && ` • Fiscal Year: ${company.fiscal_year_start}`}
                        </p>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        tabIndex={10}
                        onClick={() => editSisterCompany(company.id)}
                        className="bg-blue-600 hover:bg-blue-700 text-white"
                      >
                        Edit
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        tabIndex={11}
                        onClick={() => removeSisterCompany(company.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        Remove
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}

          <Alert>
            <Building className="h-4 w-4" />
            <AlertDescription>
              As a Group Company, you can manage multiple sister companies with consolidated accounting. 
              Sister companies added here will be saved when you complete the setup process.
              Each sister company will have its own chart of accounts that can be consolidated for reporting.
            </AlertDescription>
          </Alert>
        </div>
      )}
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <CreditCard className="w-12 h-12 text-blue-600 mx-auto mb-3" />
        <h2 className="text-2xl font-bold text-gray-900">Currency & Accounting</h2>
        <p className="text-gray-600">Configure your accounting system and currencies</p>
      </div>

      <div>
        <Label htmlFor="base_currency">Base Currency *</Label>
        <Select value={formData.base_currency} onValueChange={(value) => setFormData(prev => ({...prev, base_currency: value}))}>
          <SelectTrigger tabIndex={1}>
            <SelectValue placeholder="Select base currency" />
          </SelectTrigger>
          <SelectContent>
            {currencies.map(currency => (
              <SelectItem key={currency.code} value={currency.code}>
                <div className="flex items-center">
                  <span className="font-medium">{currency.code}</span>
                  <span className="ml-2 text-gray-600">{currency.symbol} - {currency.name}</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <p className="text-xs text-gray-500 mt-1">This will be your primary accounting currency</p>
      </div>

      <div>
        <Label>Additional Currencies (Optional)</Label>
        <p className="text-sm text-gray-600 mb-3">Select additional currencies for multi-currency transactions</p>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 max-h-60 overflow-y-auto border rounded-lg p-3">
          {currencies.filter(c => c.code !== formData.base_currency).map(currency => (
            <div 
              key={currency.code} 
              className={`p-2 border rounded-lg cursor-pointer transition-colors ${
                formData.additional_currencies.includes(currency.code)
                  ? 'bg-blue-50 border-blue-300' 
                  : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
              }`}
              onClick={() => handleCurrencyToggle(currency.code)}
            >
              <div className="text-sm font-medium">{currency.code}</div>
              <div className="text-xs text-gray-600">{currency.symbol}</div>
            </div>
          ))}
        </div>
        {formData.additional_currencies.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {formData.additional_currencies.map(code => {
              const currency = currencies.find(c => c.code === code);
              return (
                <Badge key={code} variant="secondary" className="text-xs">
                  {code} ({currency?.symbol})
                </Badge>
              );
            })}
          </div>
        )}
      </div>

      <div>
        <Label htmlFor="fiscal_year_start">Fiscal Year Start Date *</Label>
        <Select value={formData.fiscal_year_start} onValueChange={(value) => setFormData(prev => ({...prev, fiscal_year_start: value}))}>
          <SelectTrigger tabIndex={2}>
            <SelectValue placeholder="Select fiscal year start date" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="01-01">January 1st</SelectItem>
            <SelectItem value="04-01">April 1st</SelectItem>
            <SelectItem value="07-01">July 1st</SelectItem>
            <SelectItem value="10-01">October 1st</SelectItem>
            <SelectItem value="01-04">January 4th</SelectItem>
            <SelectItem value="custom">Custom Date</SelectItem>
          </SelectContent>
        </Select>
        {formData.fiscal_year_start === 'custom' && (
          <div className="mt-2">
            <Label htmlFor="custom_fiscal_date">Custom Fiscal Year Start (MM-DD)</Label>
            <Input
              id="custom_fiscal_date"
              tabIndex={3}
              placeholder="MM-DD (e.g., 03-15)"
              pattern="[0-1][0-9]-[0-3][0-9]"
              onChange={(e) => setFormData(prev => ({...prev, fiscal_year_start: e.target.value}))}
            />
          </div>
        )}
        <p className="text-xs text-gray-500 mt-1">This determines when your company's financial year begins</p>
      </div>

      {accountingSystem && (
        <Alert>
          <Settings className="h-4 w-4" />
          <AlertDescription>
            Your chart of accounts will be automatically created based on <strong>{accountingSystem.name}</strong> standards.
            This includes standard asset, liability, equity, revenue, and expense accounts for your country.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <MapPin className="w-12 h-12 text-blue-600 mx-auto mb-3" />
        <h2 className="text-2xl font-bold text-gray-900">Company Details</h2>
        <p className="text-gray-600">Add additional company information (optional)</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="md:col-span-2">
          <Label htmlFor="address">Address</Label>
          <Textarea
            id="address"
            tabIndex={1}
            value={formData.address}
            onChange={(e) => setFormData(prev => ({...prev, address: e.target.value}))}
            placeholder="Enter company address"
            rows={2}
          />
        </div>

        <div>
          <Label htmlFor="city">City</Label>
          <Input
            id="city"
            tabIndex={2}
            value={formData.city}
            onChange={(e) => setFormData(prev => ({...prev, city: e.target.value}))}
            placeholder="Enter city"
          />
        </div>

        <div>
          <Label htmlFor="state">State/Province</Label>
          <Input
            id="state"
            tabIndex={3}
            value={formData.state}
            onChange={(e) => setFormData(prev => ({...prev, state: e.target.value}))}
            placeholder="Enter state or province"
          />
        </div>

        <div>
          <Label htmlFor="postal_code">Postal Code</Label>
          <Input
            id="postal_code"
            tabIndex={4}
            value={formData.postal_code}
            onChange={(e) => setFormData(prev => ({...prev, postal_code: e.target.value}))}
            placeholder="Enter postal code"
          />
        </div>

        <div>
          <Label htmlFor="phone">Phone</Label>
          <Input
            id="phone"
            tabIndex={5}
            value={formData.phone}
            onChange={(e) => setFormData(prev => ({...prev, phone: e.target.value}))}
            placeholder="Enter phone number"
          />
        </div>

        <div>
          <Label htmlFor="email">Company Email</Label>
          <Input
            id="email"
            tabIndex={6}
            type="email"
            value={formData.email}
            onChange={(e) => setFormData(prev => ({...prev, email: e.target.value}))}
            placeholder="Enter company email"
          />
        </div>

        <div>
          <Label htmlFor="website">Website</Label>
          <Input
            id="website"
            tabIndex={7}
            value={formData.website}
            onChange={(e) => setFormData(prev => ({...prev, website: e.target.value}))}
            placeholder="https://www.example.com"
          />
        </div>

        <div>
          <Label htmlFor="tax_number">Tax Number</Label>
          <Input
            id="tax_number"
            tabIndex={8}
            value={formData.tax_number}
            onChange={(e) => setFormData(prev => ({...prev, tax_number: e.target.value}))}
            placeholder="Enter tax identification number"
          />
        </div>

        <div>
          <Label htmlFor="registration_number">Registration Number</Label>
          <Input
            id="registration_number"
            tabIndex={9}
            value={formData.registration_number}
            onChange={(e) => setFormData(prev => ({...prev, registration_number: e.target.value}))}
            placeholder="Enter business registration number"
          />
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <img 
              src="https://customer-assets.emergentagent.com/job_outreach-pulse-3/artifacts/5adajuhk_Zoios.png" 
              alt="ZOIOS Logo" 
              className="object-contain"
              style={{width: '150px', height: '150px'}}
            />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome to ZOIOS ERP</h1>
          <p className="text-gray-600">Let's set up your company to get started</p>
        </div>

        {/* Step Indicator */}
        {renderStepIndicator()}

        {/* Main Form */}
        <Card className="shadow-xl border-0">
          <CardContent className="p-8">
            {error && (
              <Alert variant="destructive" className="mb-6">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {currentStep === 1 && renderStep1()}
            {currentStep === 2 && renderStep2()}
            {currentStep === 3 && renderStep3()}
          </CardContent>
        </Card>

        {/* Navigation Buttons */}
        <div className="flex justify-between mt-8">
          <Button
            variant="outline"
            tabIndex={10}
            onClick={handlePrevious}
            disabled={currentStep === 1}
            className="flex items-center"
          >
            <ChevronLeft className="w-4 h-4 mr-2" />
            Previous
          </Button>

          {currentStep < 3 ? (
            <Button onClick={handleNext} tabIndex={11} className="flex items-center bg-blue-600 hover:bg-blue-700 text-white">
              Next
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          ) : (
            <Button 
              onClick={handleSubmit} 
              tabIndex={11}
              disabled={loading}
              className="flex items-center bg-blue-600 hover:bg-blue-700 text-white"
            >
              {loading ? 'Setting up...' : 'Complete Setup'}
              <CheckCircle className="w-4 h-4 ml-2" />
            </Button>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-xs text-gray-500">
            © 2025 ZOIOS. Advanced ERP Platform.
          </p>
        </div>
      </div>
    </div>
  );
};

export default CompanySetup;