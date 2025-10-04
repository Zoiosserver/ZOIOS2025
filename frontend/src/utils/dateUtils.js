// Date utility functions for dd/mm/yyyy format

/**
 * Convert a date string to dd/mm/yyyy format for display
 * @param {string} dateString - Date in YYYY-MM-DD format
 * @returns {string} Date in dd/mm/yyyy format
 */
export const formatDateForDisplay = (dateString) => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return '';
  
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  
  return `${day}/${month}/${year}`;
};

/**
 * Convert a date string from dd/mm/yyyy format to YYYY-MM-DD for input fields
 * @param {string} displayDate - Date in dd/mm/yyyy format
 * @returns {string} Date in YYYY-MM-DD format
 */
export const formatDateForInput = (displayDate) => {
  if (!displayDate) return '';
  
  // Check if it's already in YYYY-MM-DD format
  if (displayDate.match(/^\d{4}-\d{2}-\d{2}$/)) {
    return displayDate;
  }
  
  // Parse dd/mm/yyyy format
  const parts = displayDate.split('/');
  if (parts.length === 3) {
    const day = parts[0].padStart(2, '0');
    const month = parts[1].padStart(2, '0');
    const year = parts[2];
    return `${year}-${month}-${day}`;
  }
  
  return displayDate;
};

/**
 * Get current date in dd/mm/yyyy format
 * @returns {string} Current date in dd/mm/yyyy format
 */
export const getCurrentDateForDisplay = () => {
  const today = new Date();
  return formatDateForDisplay(today.toISOString().split('T')[0]);
};

/**
 * Get current date in YYYY-MM-DD format for input fields
 * @returns {string} Current date in YYYY-MM-DD format
 */
export const getCurrentDateForInput = () => {
  const today = new Date();
  return today.toISOString().split('T')[0];
};

/**
 * Convert fiscal year start to dd/mm format for display
 * @param {string} dateString - Date in YYYY-MM-DD format
 * @returns {string} Date in dd/mm format (without year)
 */
export const formatFiscalYearForDisplay = (dateString) => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return '';
  
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  
  return `${day}/${month}`;
};