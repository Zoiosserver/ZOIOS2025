import React, { useState, useRef } from 'react';
import { formatDateForDisplay, formatDateForInput } from '../utils/dateUtils';

const DateInput = ({ 
  name, 
  value, 
  onChange, 
  placeholder = "dd/mm/yyyy", 
  className = "", 
  required = false,
  ...props 
}) => {
  const [displayValue, setDisplayValue] = useState(formatDateForDisplay(value) || '');
  const [showNativePicker, setShowNativePicker] = useState(false);
  const nativeInputRef = useRef(null);

  const handleDisplayChange = (e) => {
    let inputValue = e.target.value;
    
    // Remove any non-numeric characters except /
    inputValue = inputValue.replace(/[^\d\/]/g, '');
    
    // Remove duplicate slashes
    inputValue = inputValue.replace(/\/+/g, '/');
    
    // Auto-format as user types
    let formattedValue = '';
    let numericOnly = inputValue.replace(/\//g, '');
    
    if (numericOnly.length >= 2) {
      formattedValue = numericOnly.substring(0, 2);
      if (numericOnly.length >= 4) {
        formattedValue += '/' + numericOnly.substring(2, 4);
        if (numericOnly.length >= 8) {
          formattedValue += '/' + numericOnly.substring(4, 8);
        } else if (numericOnly.length > 4) {
          formattedValue += '/' + numericOnly.substring(4);
        }
      } else if (numericOnly.length > 2) {
        formattedValue += '/' + numericOnly.substring(2);
      }
    } else {
      formattedValue = numericOnly;
    }
    
    // Add slash after day and month if not present and we have enough digits
    if (inputValue.length === 2 && !inputValue.includes('/')) {
      formattedValue += '/';
    } else if (inputValue.length === 5 && inputValue.split('/').length === 2) {
      formattedValue += '/';
    }
    
    // Limit to 10 characters (dd/mm/yyyy)
    if (formattedValue.length <= 10) {
      setDisplayValue(formattedValue);
      
      // If we have a complete date, convert and call onChange
      if (formattedValue.length === 10 && formattedValue.split('/').length === 3) {
        const parts = formattedValue.split('/');
        const day = parts[0];
        const month = parts[1];
        const year = parts[2];
        
        // Basic validation
        if (day <= 31 && month <= 12 && year.length === 4) {
          const isoDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
          onChange({ target: { name, value: isoDate } });
        }
      }
    }
  };

  const handleNativeChange = (e) => {
    const isoDate = e.target.value;
    setDisplayValue(formatDateForDisplay(isoDate));
    setShowNativePicker(false);
    onChange({ target: { name, value: isoDate } });
  };

  const handleFocus = () => {
    // On mobile devices, show the native date picker
    if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
      setShowNativePicker(true);
      setTimeout(() => {
        if (nativeInputRef.current) {
          nativeInputRef.current.focus();
          nativeInputRef.current.showPicker?.();
        }
      }, 100);
    }
  };

  return (
    <div className="relative">
      {/* Display input for desktop */}
      <input
        type="text"
        name={name}
        value={displayValue}
        onChange={handleDisplayChange}
        onFocus={handleFocus}
        placeholder={placeholder}
        className={className}
        required={required}
        {...props}
      />
      
      {/* Hidden native date input for mobile */}
      {showNativePicker && (
        <input
          ref={nativeInputRef}
          type="date"
          value={formatDateForInput(value)}
          onChange={handleNativeChange}
          onBlur={() => setShowNativePicker(false)}
          className="absolute inset-0 opacity-0 w-full h-full"
          style={{ zIndex: 10 }}
        />
      )}
      
      {/* Calendar icon */}
      <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
        <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd"/>
        </svg>
      </div>
    </div>
  );
};

export default DateInput;