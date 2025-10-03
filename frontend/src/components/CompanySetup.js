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
  Info
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

  const [formData, setFormData] = useState({
    // Step 1: Company Basic Info
    company_name: user?.company || '',
    country_code: '',
    business_type: '',
    industry: '',
    
    // Step 2: Accounting & Currency
    base_currency: '',
    additional_currencies: [],
    
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
            value={formData.company_name}
            onChange={(e) => setFormData(prev => ({...prev, company_name: e.target.value}))}
            placeholder="Enter your company name"
            required
          />
        </div>

        <div>
          <Label htmlFor="country">Country *</Label>
          <Select value={formData.country_code} onValueChange={handleCountryChange}>
            <SelectTrigger>
              <SelectValue placeholder="Select your country" />
            </SelectTrigger>
            <SelectContent className="max-w-none w-full">
              {countries.map(country => (
                <SelectItem key={country.code} value={country.code} className="max-w-none">
                  <div className="flex items-center justify-between w-full min-w-0">
                    <span className="flex-1 truncate">{country.name}</span>
                    <span className="text-xs text-gray-500 ml-2 flex-shrink-0">({country.currency})</span>
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

        <div>
          <Label htmlFor="business_type">Business Type *</Label>
          <Select value={formData.business_type} onValueChange={(value) => setFormData(prev => ({...prev, business_type: value}))}>
            <SelectTrigger>
              <SelectValue placeholder="Select business type" />
            </SelectTrigger>
            <SelectContent>
              {businessTypes.map(type => (
                <SelectItem key={type} value={type}>{type}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="md:col-span-2">
          <Label htmlFor="industry">Industry *</Label>
          <Select value={formData.industry} onValueChange={(value) => setFormData(prev => ({...prev, industry: value}))}>
            <SelectTrigger>
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
          <SelectTrigger>
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
            value={formData.city}
            onChange={(e) => setFormData(prev => ({...prev, city: e.target.value}))}
            placeholder="Enter city"
          />
        </div>

        <div>
          <Label htmlFor="state">State/Province</Label>
          <Input
            id="state"
            value={formData.state}
            onChange={(e) => setFormData(prev => ({...prev, state: e.target.value}))}
            placeholder="Enter state or province"
          />
        </div>

        <div>
          <Label htmlFor="postal_code">Postal Code</Label>
          <Input
            id="postal_code"
            value={formData.postal_code}
            onChange={(e) => setFormData(prev => ({...prev, postal_code: e.target.value}))}
            placeholder="Enter postal code"
          />
        </div>

        <div>
          <Label htmlFor="phone">Phone</Label>
          <Input
            id="phone"
            value={formData.phone}
            onChange={(e) => setFormData(prev => ({...prev, phone: e.target.value}))}
            placeholder="Enter phone number"
          />
        </div>

        <div>
          <Label htmlFor="email">Company Email</Label>
          <Input
            id="email"
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
            value={formData.website}
            onChange={(e) => setFormData(prev => ({...prev, website: e.target.value}))}
            placeholder="https://www.example.com"
          />
        </div>

        <div>
          <Label htmlFor="tax_number">Tax Number</Label>
          <Input
            id="tax_number"
            value={formData.tax_number}
            onChange={(e) => setFormData(prev => ({...prev, tax_number: e.target.value}))}
            placeholder="Enter tax identification number"
          />
        </div>

        <div>
          <Label htmlFor="registration_number">Registration Number</Label>
          <Input
            id="registration_number"
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
            onClick={handlePrevious}
            disabled={currentStep === 1}
            className="flex items-center"
          >
            <ChevronLeft className="w-4 h-4 mr-2" />
            Previous
          </Button>

          {currentStep < 3 ? (
            <Button onClick={handleNext} className="flex items-center">
              Next
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          ) : (
            <Button 
              onClick={handleSubmit} 
              disabled={loading}
              className="flex items-center bg-green-600 hover:bg-green-700"
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