import React from 'react';

const ZoiosLogo = ({ size = "large", className = "" }) => {
  const logoSizes = {
    small: { height: "h-6" },
    medium: { height: "h-8" },
    large: { height: "h-10" },
    xl: { height: "h-12" }
  };

  const { height } = logoSizes[size] || logoSizes.large;

  return (
    <div className={`flex items-center ${className}`}>
      {/* ZOIOS Logo - Using the exact PNG image provided */}
      <img 
        src="https://customer-assets.emergentagent.com/job_finance-hub-176/artifacts/zvtyoqsa_Zoios.png"
        alt="ZOIOS Logo"
        className={`${height} w-auto object-contain`}
        style={{ aspectRatio: '4/1' }} // Based on the analysis: width is ~4x height
      />
    </div>
  );
};

export default ZoiosLogo;