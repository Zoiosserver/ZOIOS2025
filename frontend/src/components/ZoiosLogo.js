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
      {/* ZOIOS Icon - Accurate recreation of the original logo */}
      <div className={`${width} ${height} flex items-center justify-center`}>
        <svg viewBox="0 0 100 100" className="w-full h-full" fill="none">
          {/* Outer curved arc */}
          <path
            d="M15 25 C25 15, 55 15, 75 25 C85 35, 85 50, 75 75 C65 85, 35 85, 25 75 C15 65, 15 50, 15 35"
            stroke="#2563EB"
            strokeWidth="6"
            strokeLinecap="round"
            fill="none"
          />
          {/* Middle curved arc */}
          <path
            d="M25 35 C35 25, 55 25, 65 35 C70 40, 70 50, 65 65 C55 75, 35 75, 30 65 C25 55, 25 45, 25 40"
            stroke="#2563EB"
            strokeWidth="5"
            strokeLinecap="round"
            fill="none"
          />
          {/* Inner curved arc */}
          <path
            d="M35 45 C40 40, 55 40, 60 45 C62 47, 62 50, 60 55 C55 60, 40 60, 38 55 C35 52, 35 48, 35 47"
            stroke="#2563EB"
            strokeWidth="4"
            strokeLinecap="round"
            fill="none"
          />
          {/* Innermost dot/circle */}
          <circle cx="50" cy="50" r="3" fill="#2563EB"/>
        </svg>
      </div>
      
      {/* ZOIOS Text - Matching the original font weight and style */}
      <span className={`font-bold text-black ${text} tracking-normal`}>
        Zoiios
      </span>
    </div>
  );
};

export default ZoiosLogo;