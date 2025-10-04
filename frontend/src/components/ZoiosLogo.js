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
      {/* ZOIOS Icon - Blue curved segments */}
      <div className={`${width} ${height} flex items-center justify-center`}>
        <svg viewBox="0 0 100 100" className="w-full h-full" fill="none">
          {/* Curved segments creating the dynamic ZOIOS icon */}
          <path
            d="M20 20 C30 15, 50 15, 60 20 C70 25, 80 35, 80 50 C80 65, 70 75, 60 80 C50 85, 30 85, 20 80"
            stroke="#3B82F6"
            strokeWidth="8"
            strokeLinecap="round"
            fill="none"
          />
          <path
            d="M30 30 C35 27, 45 27, 50 30 C55 33, 65 40, 65 50 C65 60, 55 67, 50 70 C45 73, 35 73, 30 70"
            stroke="#3B82F6"
            strokeWidth="6"
            strokeLinecap="round"
            fill="none"
          />
          <path
            d="M40 40 C42 39, 47 39, 49 40 C51 41, 55 44, 55 50 C55 56, 51 59, 49 60 C47 61, 42 61, 40 60"
            stroke="#3B82F6"
            strokeWidth="4"
            strokeLinecap="round"
            fill="none"
          />
        </svg>
      </div>
      
      {/* ZOIOS Text */}
      <span className={`font-bold text-black ${text} tracking-wide`}>
        Zoiios
      </span>
    </div>
  );
};

export default ZoiosLogo;