import React from 'react';

const ZoiosLogo = ({ size = "large", className = "" }) => {
  const logoSizes = {
    small: { width: "w-8", height: "h-8", text: "text-lg" },
    medium: { width: "w-10", height: "h-10", text: "text-xl" },
    large: { width: "w-12", height: "h-12", text: "text-2xl" },
    xl: { width: "w-16", height: "h-16", text: "text-3xl" }
  };

  const { width, height, text } = logoSizes[size] || logoSizes.large;

  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      {/* ZOIOS Icon - Exact recreation based on the provided logo */}
      <div className={`${width} ${height} flex items-center justify-center`}>
        <svg viewBox="0 0 80 80" className="w-full h-full" fill="none">
          {/* Outermost arc - longest and most prominent */}
          <path
            d="M12 65 C8 60, 8 50, 12 35 C16 25, 28 15, 45 12 C55 10, 65 12, 72 18"
            stroke="#007BFF"
            strokeWidth="4"
            strokeLinecap="round"
            fill="none"
          />
          {/* Middle arc - longer and smoother with fewer gaps */}
          <path
            d="M18 58 C15 54, 15 47, 18 38 C21 30, 30 22, 42 20 C50 19, 58 20, 63 25"
            stroke="#007BFF"
            strokeWidth="3.5"
            strokeLinecap="round"
            fill="none"
          />
          {/* Innermost arc - shortest and most segmented with dashed appearance */}
          <path
            d="M25 50 C23 47, 23 43, 25 40 C27 36, 32 32, 38 31 C42 30, 46 31, 49 33"
            stroke="#007BFF"
            strokeWidth="3"
            strokeLinecap="round"
            strokeDasharray="2 1"
            fill="none"
          />
        </svg>
      </div>
      
      {/* ZOIOS Text - Bold, sans-serif, uppercase with rounded terminals */}
      <span className={`font-black text-black ${text} tracking-tight uppercase`} style={{fontFamily: 'system-ui, -apple-system, sans-serif'}}>
        ZOIOS
      </span>
    </div>
  );
};

export default ZoiosLogo;