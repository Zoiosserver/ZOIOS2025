import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { 
  DollarSign, 
  TrendingUp, 
  RefreshCw, 
  Plus, 
  Minus,
  ArrowUpDown,
  Info,
  Settings,
  Edit,
  Trash2,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = window.location.origin.replace(':3000', '');
const API = `${BACKEND_URL}/api`;

const CurrencyManagement = () => {
  const { user } = useAuth();
  const [exchangeRates, setExchangeRates] = useState({});
  const [loading, setLoading] = useState(true);
  const [updateLoading, setUpdateLoading] = useState(false);
  const [companySetup, setCompanySetup] = useState(null);
  const [availableCurrencies, setAvailableCurrencies] = useState([]);
  const [conversionAmount, setConversionAmount] = useState(100);
  const [fromCurrency, setFromCurrency] = useState('');
  const [toCurrency, setToCurrency] = useState('');
  const [conversionResult, setConversionResult] = useState(null);
  const [editingCurrencies, setEditingCurrencies] = useState(false);
  const [selectedCurrencies, setSelectedCurrencies] = useState([]);

  // Load company setup and exchange rates
  useEffect(() => {
    fetchCompanySetup();
    fetchExchangeRates();
    fetchAvailableCurrencies();
  }, []);

  const fetchCompanySetup = async () => {
    try {
      const response = await axios.get(`${API}/setup/company`);
      setCompanySetup(response.data);
      setFromCurrency(response.data.base_currency);
      
      // Set selected currencies from company setup
      if (response.data.additional_currencies) {
        setSelectedCurrencies(response.data.additional_currencies);
      }
    } catch (error) {
      console.error('Error fetching company setup:', error);
      if (error.response?.status !== 404) {
        toast.error('Failed to load company setup');
      }
    }
  };

  const fetchExchangeRates = async () => {
    try {
      const response = await axios.get(`${API}/currency/rates`);
      setExchangeRates(response.data);
    } catch (error) {
      console.error('Error fetching exchange rates:', error);
      toast.error('Failed to load exchange rates');
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailableCurrencies = async () => {
    try {
      const response = await axios.get(`${API}/currency/available`);
      setAvailableCurrencies(response.data);
    } catch (error) {
      console.error('Error fetching available currencies:', error);
    }
  };

  const updateExchangeRates = async () => {
    setUpdateLoading(true);
    try {
      const response = await axios.post(`${API}/currency/update-rates`, {
        base_currency: companySetup?.base_currency || 'USD'
      });
      
      toast.success(`Updated ${response.data.updated_rates || 0} exchange rates`);
      fetchExchangeRates();
    } catch (error) {
      console.error('Error updating exchange rates:', error);
      toast.error('Failed to update exchange rates');
    } finally {
      setUpdateLoading(false);
    }
  };

  const handleConversion = () => {
    if (!fromCurrency || !toCurrency || !conversionAmount) {
      toast.error('Please fill all conversion fields');
      return;
    }

    let result = conversionAmount;
    
    if (fromCurrency !== toCurrency) {
      const fromRate = exchangeRates[fromCurrency] || 1;
      const toRate = exchangeRates[toCurrency] || 1;
      result = (conversionAmount / fromRate) * toRate;
    }
    
    setConversionResult({
      from: { amount: conversionAmount, currency: fromCurrency },
      to: { amount: result.toFixed(4), currency: toCurrency },
      rate: fromCurrency === toCurrency ? 1 : (exchangeRates[toCurrency] / exchangeRates[fromCurrency] || 0).toFixed(6)
    });
  };

  const formatCurrency = (amount, currencyCode) => {
    const currency = availableCurrencies.find(c => c.code === currencyCode);
    const symbol = currency?.symbol || '$';
    const decimals = ['JPY', 'KRW'].includes(currencyCode) ? 0 : 2;
    
    return `${symbol}${parseFloat(amount).toLocaleString('en-US', { 
      minimumFractionDigits: decimals, 
      maximumFractionDigits: decimals 
    })}`;
  };

  const handleCurrencyToggle = (currencyCode) => {
    setSelectedCurrencies(prev => {
      if (prev.includes(currencyCode)) {
        return prev.filter(c => c !== currencyCode);
      } else {
        return [...prev, currencyCode];
      }
    });
  };

  const saveCurrencySelection = async () => {
    try {
      await axios.put(`${API}/setup/company`, {
        ...companySetup,
        additional_currencies: selectedCurrencies
      });
      
      setCompanySetup(prev => ({ ...prev, additional_currencies: selectedCurrencies }));
      setEditingCurrencies(false);
      toast.success('Currency selection updated successfully!');
      
      // Refresh exchange rates for new currencies
      fetchExchangeRates();
    } catch (error) {
      console.error('Error updating currency selection:', error);
      toast.error('Failed to update currency selection');
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2">Loading currency data...</span>
        </div>
      </div>
    );
  }

  if (!companySetup) {
    return (
      <div className="p-6">
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            Please complete your company setup first to access currency management.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const baseCurrency = companySetup.base_currency;
  const additionalCurrencies = companySetup.additional_currencies || [];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Currency Management</h1>
          <p className="text-gray-600">Manage exchange rates and currency conversions</p>
        </div>
        <Button 
          onClick={updateExchangeRates} 
          disabled={updateLoading}
          className="bg-blue-600 hover:bg-blue-700"
        >
          {updateLoading ? (
            <div className="flex items-center">
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              Updating...
            </div>
          ) : (
            <div className="flex items-center">
              <RefreshCw className="w-4 h-4 mr-2" />
              Update Rates
            </div>
          )}
        </Button>
      </div>

      {/* Company Currency Configuration */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle className="flex items-center gap-2">
              {(() => {
                const currencyIcons = {
                  'INR': <span className="text-lg">₹</span>,
                  'USD': <DollarSign className="w-5 h-5" />,
                  'EUR': <span className="text-lg">€</span>,
                  'GBP': <span className="text-lg">£</span>,
                  'JPY': <span className="text-lg">¥</span>,
                  'CNY': <span className="text-lg">¥</span>
                };
                return currencyIcons[companySetup?.base_currency] || <DollarSign className="w-5 h-5" />;
              })()}
              Currency Configuration
            </CardTitle>
            <Dialog open={editingCurrencies} onOpenChange={setEditingCurrencies}>
              <DialogTrigger asChild>
                <Button variant="outline" size="sm">
                  <Settings className="w-4 h-4 mr-2" />
                  Edit Currencies
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Manage Additional Currencies</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {availableCurrencies
                      .filter(currency => currency.code !== baseCurrency)
                      .map(currency => (
                        <div
                          key={currency.code}
                          onClick={() => handleCurrencyToggle(currency.code)}
                          className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                            selectedCurrencies.includes(currency.code)
                              ? 'bg-blue-50 border-blue-300'
                              : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                              <span className="text-sm font-medium">{currency.symbol}</span>
                              <span className="text-xs text-gray-600">{currency.code}</span>
                            </div>
                            {selectedCurrencies.includes(currency.code) && (
                              <CheckCircle className="w-4 h-4 text-blue-600" />
                            )}
                          </div>
                          <div className="text-xs text-gray-500 mt-1 truncate">{currency.name}</div>
                        </div>
                      ))
                    }
                  </div>
                  <div className="flex justify-end space-x-2 pt-4 border-t">
                    <Button variant="outline" onClick={() => setEditingCurrencies(false)}>
                      Cancel
                    </Button>
                    <Button onClick={saveCurrencySelection}>
                      Save Changes
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label className="text-sm font-medium text-gray-700">Base Currency</Label>
              <div className="mt-1 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center space-x-2">
                  <span className="text-lg font-semibold text-blue-800">{baseCurrency}</span>
                  <span className="text-sm text-blue-600">
                    {availableCurrencies.find(c => c.code === baseCurrency)?.name}
                  </span>
                </div>
              </div>
            </div>
            <div>
              <Label className="text-sm font-medium text-gray-700">
                Additional Currencies ({additionalCurrencies.length})
              </Label>
              <div className="mt-1 min-h-[60px] p-3 bg-gray-50 border rounded-lg">
                {additionalCurrencies.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {additionalCurrencies.map(code => {
                      const currency = availableCurrencies.find(c => c.code === code);
                      return (
                        <Badge key={code} variant="secondary" className="text-xs">
                          {currency?.symbol} {code}
                        </Badge>
                      );
                    })}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No additional currencies configured</p>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Exchange Rates */}
      {Object.keys(exchangeRates).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Current Exchange Rates
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(exchangeRates).map(([currency, rate]) => {
                const currencyInfo = availableCurrencies.find(c => c.code === currency);
                return (
                  <div key={currency} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="font-medium">{currency}</div>
                        <div className="text-sm text-gray-600">{currencyInfo?.name}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">{rate.toFixed(4)}</div>
                        <div className="text-sm text-gray-500">per {baseCurrency}</div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Currency Converter */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ArrowUpDown className="w-5 h-5" />
            Currency Converter
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-4 gap-4 items-end">
            <div>
              <Label>Amount</Label>
              <Input
                type="number"
                value={conversionAmount}
                onChange={(e) => setConversionAmount(parseFloat(e.target.value) || 0)}
                placeholder="Enter amount"
              />
            </div>
            <div>
              <Label>From Currency</Label>
              <Select value={fromCurrency} onValueChange={setFromCurrency}>
                <SelectTrigger>
                  <SelectValue placeholder="Select currency" />
                </SelectTrigger>
                <SelectContent>
                  {[baseCurrency, ...additionalCurrencies].map(code => {
                    const currency = availableCurrencies.find(c => c.code === code);
                    return (
                      <SelectItem key={code} value={code}>
                        {currency?.symbol} {code} - {currency?.name}
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>To Currency</Label>
              <Select value={toCurrency} onValueChange={setToCurrency}>
                <SelectTrigger>
                  <SelectValue placeholder="Select currency" />
                </SelectTrigger>
                <SelectContent>
                  {[baseCurrency, ...additionalCurrencies].map(code => {
                    const currency = availableCurrencies.find(c => c.code === code);
                    return (
                      <SelectItem key={code} value={code}>
                        {currency?.symbol} {code} - {currency?.name}
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>
            </div>
            <Button onClick={handleConversion} className="bg-blue-600 hover:bg-blue-700">
              Convert
            </Button>
          </div>
          
          {conversionResult && (
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-800">
                  {formatCurrency(conversionResult.from.amount, conversionResult.from.currency)} = {formatCurrency(conversionResult.to.amount, conversionResult.to.currency)}
                </div>
                <div className="text-sm text-blue-600 mt-2">
                  Exchange Rate: 1 {conversionResult.from.currency} = {conversionResult.rate} {conversionResult.to.currency}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default CurrencyManagement;