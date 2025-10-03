import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { 
  DollarSign, 
  RefreshCw, 
  Edit,
  Calendar,
  TrendingUp,
  ArrowUpDown,
  Plus,
  CheckCircle,
  AlertCircle,
  Info
} from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CurrencyManagement = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [exchangeRates, setExchangeRates] = useState([]);
  const [companySetup, setCompanySetup] = useState(null);
  const [editingRate, setEditingRate] = useState(null);
  const [newRate, setNewRate] = useState('');
  const [convertAmount, setConvertAmount] = useState('');
  const [convertFrom, setConvertFrom] = useState('');
  const [convertTo, setConvertTo] = useState('');
  const [convertResult, setConvertResult] = useState(null);
  const [showCurrencySettings, setShowCurrencySettings] = useState(false);
  const [allCurrencies] = useState(['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'SGD']);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    fetchCompanySetup();
    fetchExchangeRates();
  }, []);

  const fetchCompanySetup = async () => {
    try {
      const response = await axios.get(`${API}/setup/company`);
      setCompanySetup(response.data);
    } catch (error) {
      console.error('Error fetching company setup:', error);
    }
  };

  const fetchExchangeRates = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/currency/rates`);
      setExchangeRates(response.data);
      
      // Find the most recent update time
      const latestUpdate = response.data.reduce((latest, rate) => {
        const rateTime = new Date(rate.last_updated);
        return rateTime > latest ? rateTime : latest;
      }, new Date(0));
      
      setLastUpdated(latestUpdate);
    } catch (error) {
      console.error('Error fetching exchange rates:', error);
      toast.error('Failed to load exchange rates');
    } finally {
      setLoading(false);
    }
  };

  const updateOnlineRates = async () => {
    try {
      setLoading(true);
      toast.info('Updating exchange rates from online sources...');
      
      const response = await axios.post(`${API}/currency/update-rates`);
      
      if (response.data.success) {
        toast.success(`Updated ${response.data.updated_count} exchange rates`);
        fetchExchangeRates(); // Refresh the rates
      } else {
        toast.error(response.data.error || 'Failed to update rates');
      }
    } catch (error) {
      console.error('Error updating rates:', error);
      toast.error('Failed to update exchange rates');
    } finally {
      setLoading(false);
    }
  };

  const updateAdditionalCurrencies = async (selectedCurrencies) => {
    try {
      await axios.put(`${API}/company/additional-currencies`, {
        additional_currencies: selectedCurrencies
      });
      toast.success('Additional currencies updated successfully');
      fetchCompanySetup();
      fetchExchangeRates();
    } catch (error) {
      console.error('Error updating additional currencies:', error);
      toast.error('Failed to update additional currencies');
    }
  };

  const saveManualRate = async (baseCurrency, targetCurrency, rate) => {
    try {
      await axios.post(`${API}/currency/set-manual-rate`, {
        base_currency: baseCurrency,
        target_currency: targetCurrency,
        rate: parseFloat(rate),
        source: 'manual'
      });
      
      toast.success('Exchange rate updated successfully');
      setEditingRate(null);
      setNewRate('');
      fetchExchangeRates();
    } catch (error) {
      console.error('Error setting manual rate:', error);
      toast.error('Failed to update exchange rate');
    }
  };

  const convertCurrency = async () => {
    if (!convertAmount || !convertFrom || !convertTo) {
      toast.error('Please fill in all conversion fields');
      return;
    }

    try {
      const response = await axios.post(`${API}/currency/convert`, null, {
        params: {
          amount: parseFloat(convertAmount),
          from_currency: convertFrom,
          to_currency: convertTo
        }
      });
      
      setConvertResult(response.data);
    } catch (error) {
      console.error('Error converting currency:', error);
      toast.error(error.response?.data?.detail || 'Failed to convert currency');
      setConvertResult(null);
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

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getSourceBadgeVariant = (source) => {
    switch (source) {
      case 'online': return 'default';
      case 'manual': return 'secondary';
      case 'system': return 'outline';
      default: return 'outline';
    }
  };

  const availableCurrencies = (companySetup && companySetup.base_currency && companySetup.additional_currencies) ? [
    companySetup.base_currency,
    ...companySetup.additional_currencies
  ] : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Currency Management</h1>
          <p className="text-gray-600">Manage exchange rates and currency conversions</p>
        </div>
        <Button 
          onClick={updateExchangeRates} 
          disabled={updating}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white"
        >
          <RefreshCw className={`w-4 h-4 ${updating ? 'animate-spin' : ''}`} />
          Update Rates
        </Button>
      </div>

      {/* Company Currency Info */}
      {companySetup && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {companySetup?.base_currency === 'INR' ? 
                <span className="text-lg">₹</span> : 
                <DollarSign className="w-5 h-5" />
              }
              Currency Configuration
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium text-gray-700">Base Currency</Label>
                <div className="mt-1">
                  <Badge variant="default" className="text-lg px-3 py-1">
                    {companySetup?.base_currency === 'INR' && '₹ INR'}
                    {companySetup?.base_currency === 'USD' && '$ USD'}
                    {companySetup?.base_currency === 'EUR' && '€ EUR'}
                    {companySetup?.base_currency === 'GBP' && '£ GBP'}
                    {companySetup?.base_currency === 'JPY' && '¥ JPY'}
                    {companySetup?.base_currency && !['INR', 'USD', 'EUR', 'GBP', 'JPY'].includes(companySetup.base_currency) && companySetup.base_currency}
                  </Badge>
                </div>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700">Additional Currencies</Label>
                <div className="mt-1 flex flex-wrap gap-2">
                  {companySetup.additional_currencies?.map(currency => (
                    <Badge key={currency} variant="outline">
                      {currency}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
            {lastUpdated && (
              <div className="mt-4 text-sm text-gray-500">
                Last updated: {formatDate(lastUpdated)}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Exchange Rates */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Current Exchange Rates
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading || !companySetup ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading exchange rates...</p>
            </div>
          ) : exchangeRates.length === 0 ? (
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                No exchange rates configured yet. Update rates to get started.
              </AlertDescription>
            </Alert>
          ) : (
            <div className="space-y-4">
              {exchangeRates.map(rate => (
                <div key={`${rate.base_currency}-${rate.target_currency}`} 
                     className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="text-lg font-medium">
                      {rate.base_currency} → {rate.target_currency}
                    </div>
                    <Badge variant={getSourceBadgeVariant(rate.source)}>
                      {rate.source}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    {editingRate === `${rate.base_currency}-${rate.target_currency}` ? (
                      <div className="flex items-center space-x-2">
                        <Input
                          type="number"
                          step="0.0001"
                          value={newRate}
                          onChange={(e) => setNewRate(e.target.value)}
                          placeholder="Enter new rate"
                          className="w-32"
                        />
                        <Button 
                          size="sm"
                          onClick={() => saveManualRate(rate.base_currency, rate.target_currency, newRate)}
                        >
                          <CheckCircle className="w-4 h-4" />
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => {
                            setEditingRate(null);
                            setNewRate('');
                          }}
                        >
                          Cancel
                        </Button>
                      </div>
                    ) : (
                      <>
                        <div className="text-right">
                          <div className="text-lg font-semibold">{rate.rate.toFixed(4)}</div>
                          <div className="text-sm text-gray-500">
                            {formatDate(rate.last_updated)}
                          </div>
                        </div>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => {
                            setEditingRate(`${rate.base_currency}-${rate.target_currency}`);
                            setNewRate(rate.rate.toString());
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Currency Converter */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ArrowUpDown className="w-5 h-5" />
            Currency Converter
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div>
              <Label htmlFor="amount">Amount</Label>
              <Input
                id="amount"
                type="number"
                step="0.01"
                value={convertAmount}
                onChange={(e) => setConvertAmount(e.target.value)}
                placeholder="Enter amount"
              />
            </div>
            <div>
              <Label htmlFor="from">From Currency</Label>
              <select 
                id="from"
                value={convertFrom}
                onChange={(e) => setConvertFrom(e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
              >
                <option value="">Select currency</option>
                {availableCurrencies.map(currency => (
                  <option key={currency} value={currency}>{currency}</option>
                ))}
              </select>
            </div>
            <div>
              <Label htmlFor="to">To Currency</Label>
              <select 
                id="to"
                value={convertTo}
                onChange={(e) => setConvertTo(e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
              >
                <option value="">Select currency</option>
                {availableCurrencies.map(currency => (
                  <option key={currency} value={currency}>{currency}</option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <Button onClick={convertCurrency} className="w-full bg-blue-600 hover:bg-blue-700 text-white">
                Convert
              </Button>
            </div>
          </div>

          {convertResult && (
            <Alert>
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>
                <div className="text-lg font-semibold">
                  {formatCurrency(convertResult.original_amount, convertResult.from_currency)} = {' '}
                  {formatCurrency(convertResult.converted_amount, convertResult.to_currency)}
                </div>
                <div className="text-sm text-gray-600 mt-2">
                  Exchange Rate: {convertResult.exchange_rate.toFixed(4)} • 
                  Source: {convertResult.rate_source}
                  {convertResult.last_updated && (
                    <> • Updated: {formatDate(convertResult.last_updated)}</>
                  )}
                </div>
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default CurrencyManagement;