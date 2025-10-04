import React, { useState, useEffect } from 'react';
import * as XLSX from 'xlsx';

const EnhancedChartOfAccounts = ({ selectedCompany, companies, onSelectCompany }) => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingAccount, setEditingAccount] = useState(null);
  const [filterCategory, setFilterCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const [accountForm, setAccountForm] = useState({
    code: '',
    name: '',
    account_type: 'Asset',
    category: 'Current Assets',
    opening_balance: 0,
    description: ''
  });

  const accountCategories = {
    'Asset': ['Current Assets', 'Fixed Assets', 'Investments', 'Other Assets'],
    'Liability': ['Current Liabilities', 'Long-term Liabilities', 'Other Liabilities'],
    'Equity': ['Share Capital', 'Retained Earnings', 'Other Equity'],
    'Revenue': ['Sales Revenue', 'Other Revenue', 'Service Revenue'],
    'Expense': ['Cost of Sales', 'Operating Expenses', 'Administrative Expenses', 'Financial Expenses']
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
      // Use environment variable for backend URL
      const backendUrl = process.env.REACT_APP_BACKEND_URL || window.location.origin;
      const response = await fetch(`${backendUrl}/api/company/${selectedCompany.id}/chart-of-accounts`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      console.log('DEBUG: Fetching chart of accounts for company:', selectedCompany.company_name, 'ID:', selectedCompany.id);
      console.log('DEBUG: API response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        console.log('DEBUG: Chart of accounts data received:', data);
        
        // Extract accounts from the response structure
        const allAccounts = [];
        if (data.accounts_by_category) {
          // Flatten accounts from all categories and map field names
          Object.values(data.accounts_by_category).forEach(categoryAccounts => {
            const mappedAccounts = categoryAccounts.map(account => ({
              id: account.id,
              account_code: account.code,
              account_name: account.name,
              account_type: account.account_type,
              category: account.category,
              current_balance: account.current_balance || account.opening_balance || 0,
              opening_balance: account.opening_balance || 0,
              description: account.description || ''
            }));
            allAccounts.push(...mappedAccounts);
          });
        }
        
        console.log('DEBUG: Total accounts loaded:', allAccounts.length);
        setAccounts(allAccounts);
        setError(''); // Clear any previous errors
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.log('DEBUG: API error response:', errorData);
        setError(errorData.detail || 'Failed to load accounts');
      }
    } catch (err) {
      console.log('DEBUG: Exception caught:', err);
      setError('Connection failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAccount = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Use environment variable for backend URL
      const backendUrl = process.env.REACT_APP_BACKEND_URL || window.location.origin;
      const url = editingAccount 
        ? `${backendUrl}/api/company/${selectedCompany.id}/chart-of-accounts/${editingAccount.id}` 
        : `${backendUrl}/api/company/${selectedCompany.id}/chart-of-accounts`;
      
      const method = editingAccount ? 'PUT' : 'POST';
      
      console.log('DEBUG: Submitting account with URL:', url);
      console.log('DEBUG: Account data:', accountForm);

      // Map form fields to API expected format
      const requestData = {
        account_name: accountForm.name,
        account_code: accountForm.code,
        account_type: accountForm.account_type?.toLowerCase(),
        category: accountForm.category?.toLowerCase().replace(/ /g, '_'),
        description: accountForm.description,
        opening_balance: accountForm.opening_balance
      };

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(requestData)
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
      // Use environment variable for backend URL
      const backendUrl = process.env.REACT_APP_BACKEND_URL || window.location.origin;
      const response = await fetch(`${backendUrl}/api/company/${selectedCompany.id}/chart-of-accounts/${accountId}`, {
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

  const exportToPDF = async () => {
    // Dynamic import of jsPDF
    const { jsPDF } = await import('jspdf');
    const doc = new jsPDF();
    
    // Header
    doc.setFontSize(20);
    doc.text('Chart of Accounts', 20, 30);
    doc.setFontSize(12);
    doc.text(`Company: ${selectedCompany?.company_name || 'All Companies'}`, 20, 45);
    doc.text(`Generated: ${new Date().toLocaleDateString('en-GB')}`, 20, 55);
    
    // Table headers
    doc.setFontSize(10);
    let yPos = 75;
    doc.text('Code', 20, yPos);
    doc.text('Account Name', 50, yPos);
    doc.text('Type', 120, yPos);
    doc.text('Balance', 160, yPos);
    
    // Draw line
    doc.line(20, yPos + 2, 190, yPos + 2);
    yPos += 10;
    
    // Account data
    const filteredAccounts = getFilteredAccounts();
    filteredAccounts.forEach((account) => {
      if (yPos > 280) { // New page if needed
        doc.addPage();
        yPos = 30;
      }
      
      doc.text(account.code || '', 20, yPos);
      doc.text(account.name || '', 50, yPos);
      doc.text(account.account_type || '', 120, yPos);
      doc.text(formatCurrency(account.opening_balance || 0), 160, yPos);
      yPos += 8;
    });
    
    // Footer
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.text(`Page ${i} of ${pageCount}`, 170, 290);
      doc.text('Generated by ZOIOS ERP', 20, 290);
    }
    
    doc.save(`chart-of-accounts-${selectedCompany?.company_name || 'all'}-${new Date().toISOString().split('T')[0]}.pdf`);
  };

  const exportToExcel = () => {
    try {
      console.log('DEBUG: Excel export started');
      const filteredAccounts = getFilteredAccounts();
      console.log('DEBUG: Filtered accounts:', filteredAccounts.length, filteredAccounts);
      
      if (filteredAccounts.length === 0) {
        alert('No accounts to export');
        return;
      }
      
      // Prepare data for Excel
      const excelData = filteredAccounts.map(account => ({
        'Account Code': account.account_code || account.code || '',
        'Account Name': account.account_name || account.name || '',
        'Account Type': account.account_type || '',
        'Category': account.category || '',
        'Current Balance': account.current_balance || account.opening_balance || 0,
        'Description': account.description || ''
      }));
      
      console.log('DEBUG: Excel data prepared:', excelData.length, excelData);

      // Create workbook and worksheet
      const wb = XLSX.utils.book_new();
      const ws = XLSX.utils.json_to_sheet(excelData);
      
      console.log('DEBUG: Workbook created, worksheet generated');
      
      // Set column widths
      ws['!cols'] = [
        { width: 15 }, // Account Code
        { width: 30 }, // Account Name
        { width: 15 }, // Account Type
        { width: 20 }, // Category
        { width: 15 }, // Current Balance
        { width: 40 }  // Description
      ];
      
      // Add title row
      XLSX.utils.sheet_add_aoa(ws, [[`Chart of Accounts - ${selectedCompany?.company_name || 'All Companies'}`]], { origin: 'A1' });
      XLSX.utils.sheet_add_aoa(ws, [[`Generated: ${new Date().toLocaleDateString('en-GB')}`]], { origin: 'A2' });
      XLSX.utils.sheet_add_aoa(ws, [['']], { origin: 'A3' }); // Empty row
      
      // Append worksheet to workbook
      XLSX.utils.book_append_sheet(wb, ws, 'Chart of Accounts');
      
      console.log('DEBUG: About to write Excel file');
      
      // Write file
      const filename = `chart-of-accounts-${selectedCompany?.company_name || 'all'}-${new Date().toISOString().split('T')[0]}.xlsx`;
      XLSX.writeFile(wb, filename);
      
      console.log('DEBUG: Excel file written successfully:', filename);
      
    } catch (error) {
      console.error('DEBUG: Excel export error:', error);
      alert('Excel export failed: ' + error.message);
    }
  };

  const directPrint = () => {
    const printWindow = window.open('', '', 'height=600,width=800');
    const filteredAccounts = getFilteredAccounts();
    
    printWindow.document.write(`
      <html>
        <head>
          <title>Chart of Accounts - ${selectedCompany?.company_name || 'All Companies'}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { text-align: center; margin-bottom: 30px; }
            .company-name { font-size: 20px; font-weight: bold; margin-bottom: 10px; }
            .date { font-size: 12px; color: #666; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f5f5f5; font-weight: bold; }
            .balance { text-align: right; }
            .footer { margin-top: 30px; font-size: 10px; color: #666; text-align: center; }
          </style>
        </head>
        <body>
          <div class="header">
            <div class="company-name">Chart of Accounts</div>
            <div>Company: ${selectedCompany?.company_name || 'All Companies'}</div>
            <div class="date">Generated: ${new Date().toLocaleDateString('en-GB')}</div>
          </div>
          
          <table>
            <thead>
              <tr>
                <th>Code</th>
                <th>Account Name</th>
                <th>Type</th>
                <th>Category</th>
                <th>Balance</th>
              </tr>
            </thead>
            <tbody>
              ${filteredAccounts.map(account => `
                <tr>
                  <td>${account.code || ''}</td>
                  <td>${account.name || ''}</td>
                  <td>${account.account_type || ''}</td>
                  <td>${account.category || ''}</td>
                  <td class="balance">${formatCurrency(account.opening_balance || 0)}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
          
          <div class="footer">
            Generated by ZOIOS ERP System
          </div>
        </body>
      </html>
    `);
    
    printWindow.document.close();
    printWindow.focus();
    
    setTimeout(() => {
      printWindow.print();
      printWindow.close();
    }, 250);
  };

  const getFilteredAccounts = () => {
    return accounts.filter(account => {
      const matchesCategory = filterCategory === 'all' || account.account_type === filterCategory.toLowerCase();
      const matchesSearch = account.account_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           account.account_code?.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesCategory && matchesSearch;
    });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: selectedCompany?.base_currency || 'INR',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const resetAccountForm = () => {
    setAccountForm({
      code: '',
      name: '',
      account_type: 'Asset',
      category: 'Current Assets',
      opening_balance: 0,
      description: ''
    });
  };

  const startEditAccount = (account) => {
    setEditingAccount(account);
    setAccountForm({ 
      code: account.account_code,
      name: account.account_name,
      account_type: account.account_type?.charAt(0).toUpperCase() + account.account_type?.slice(1),
      category: account.category?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      opening_balance: account.opening_balance || account.current_balance || 0,
      description: account.description || ''
    });
    setShowAddModal(true);
  };

  const generateAccountCode = (accountType) => {
    const codes = {
      'Asset': '1',
      'Liability': '2', 
      'Equity': '3',
      'Revenue': '4',
      'Expense': '5'
    };
    
    const baseCode = codes[accountType] || '1';
    const existingCodes = accounts
      .filter(acc => acc.code?.startsWith(baseCode))
      .map(acc => parseInt(acc.code?.substring(1)) || 0);
    
    const nextNumber = existingCodes.length > 0 ? Math.max(...existingCodes) + 1 : 1;
    return baseCode + nextNumber.toString().padStart(3, '0');
  };

  if (!selectedCompany) {
    return (
      <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-8">
        <div className="text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Select a Company</h3>
          <p className="text-gray-600 mb-6">Choose a company from the dropdown to view its chart of accounts</p>
          
          <div className="max-w-xs mx-auto">
            <select
              value={selectedCompany?.id || ''}
              onChange={(e) => {
                const company = companies.find(c => c.id === e.target.value);
                onSelectCompany(company);
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select Company</option>
              {companies.map((company) => (
                <option key={company.id} value={company.id}>
                  {company.company_name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Company Selection and Actions Header */}
      <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Chart of Accounts</h2>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Company:</span>
                <select
                  value={selectedCompany?.id || ''}
                  onChange={(e) => {
                    const company = companies.find(c => c.id === e.target.value);
                    onSelectCompany(company);
                  }}
                  className="text-sm px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  {companies.map((company) => (
                    <option key={company.id} value={company.id}>
                      {company.company_name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
          
          <div className="flex flex-wrap items-center space-x-2">
            {/* Export/Print Buttons */}
            <button
              onClick={exportToPDF}
              className="bg-gradient-to-r from-red-500 to-pink-500 text-white px-4 py-2 rounded-lg hover:from-red-600 hover:to-pink-600 transition-all duration-200 font-medium shadow-lg text-sm"
            >
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
                </svg>
                <span>PDF</span>
              </div>
            </button>
            
            <button
              onClick={exportToExcel}
              className="bg-gradient-to-r from-green-500 to-teal-500 text-white px-4 py-2 rounded-lg hover:from-green-600 hover:to-teal-600 transition-all duration-200 font-medium shadow-lg text-sm"
            >
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                <span>Excel</span>
              </div>
            </button>
            
            <button
              onClick={directPrint}
              className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white px-4 py-2 rounded-lg hover:from-blue-600 hover:to-indigo-600 transition-all duration-200 font-medium shadow-lg text-sm"
            >
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/>
                </svg>
                <span>Print</span>
              </div>
            </button>
            
            <button
              onClick={() => setShowAddModal(true)}
              className="bg-gradient-to-r from-purple-500 to-violet-500 text-white px-4 py-2 rounded-lg hover:from-purple-600 hover:to-violet-600 transition-all duration-200 font-medium shadow-lg text-sm"
            >
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4"/>
                </svg>
                <span>Add Account</span>
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 p-4">
        <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search accounts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="w-full sm:w-auto px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Types</option>
              <option value="Asset">Assets</option>
              <option value="Liability">Liabilities</option>
              <option value="Equity">Equity</option>
              <option value="Revenue">Revenue</option>
              <option value="Expense">Expenses</option>
            </select>
          </div>
        </div>
      </div>

      {/* Accounts Table */}
      <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100/50 overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading accounts...</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Code</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Account Name</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Balance</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {getFilteredAccounts().map((account) => (
                  <tr key={account.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {account.account_code}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {account.account_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        account.account_type === 'Asset' ? 'bg-blue-100 text-blue-800' :
                        account.account_type === 'Liability' ? 'bg-red-100 text-red-800' :
                        account.account_type === 'Equity' ? 'bg-purple-100 text-purple-800' :
                        account.account_type === 'Revenue' ? 'bg-green-100 text-green-800' :
                        'bg-orange-100 text-orange-800'
                      }`}>
                        {account.account_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {account.category}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                      {formatCurrency(account.current_balance || account.opening_balance || 0)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => startEditAccount(account)}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteAccount(account.id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {getFilteredAccounts().length === 0 && (
              <div className="p-8 text-center text-gray-500">
                No accounts found
              </div>
            )}
          </div>
        )}
      </div>

      {/* Add/Edit Account Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-gray-900">
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
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Account Code</label>
                    <div className="flex space-x-2">
                      <input
                        type="text"
                        value={accountForm.code}
                        onChange={(e) => setAccountForm({ ...accountForm, code: e.target.value })}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setAccountForm({ ...accountForm, code: generateAccountCode(accountForm.account_type) })}
                        className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm"
                      >
                        Auto
                      </button>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Account Type</label>
                    <select
                      value={accountForm.account_type}
                      onChange={(e) => setAccountForm({ 
                        ...accountForm, 
                        account_type: e.target.value,
                        category: accountCategories[e.target.value]?.[0] || ''
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    >
                      {Object.keys(accountCategories).map(type => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Account Name</label>
                  <input
                    type="text"
                    value={accountForm.name}
                    onChange={(e) => setAccountForm({ ...accountForm, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                  <select
                    value={accountForm.category}
                    onChange={(e) => setAccountForm({ ...accountForm, category: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    {(accountCategories[accountForm.account_type] || []).map(category => (
                      <option key={category} value={category}>{category}</option>
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
                    rows={3}
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

export default EnhancedChartOfAccounts;