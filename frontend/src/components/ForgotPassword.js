import React, { useState } from 'react';
import ZoiosLogo from './ZoiosLogo';

const ForgotPassword = ({ onBackToLogin }) => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const backendUrl = window.location.origin;
      
      const response = await fetch(`${backendUrl}/api/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });

      if (response.ok) {
        setSent(true);
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || 'Failed to send reset email');
      }
    } catch (error) {
      setError('Connection failed: ' + error.message);
    }
    
    setLoading(false);
  };

  if (sent) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex items-center justify-center py-6 sm:py-12 px-4 sm:px-6 lg:px-8">
        {/* Animated Background Elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-green-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse delay-1000"></div>
        </div>

        <div className="relative max-w-md w-full mx-auto">
          {/* Logo/Brand Section */}
          <div className="text-center mb-6 sm:mb-8">
            <div className="inline-flex items-center justify-center bg-white p-4 sm:p-6 rounded-2xl shadow-lg mb-4 sm:mb-6 border border-gray-100">
              <ZoiosLogo size="xl" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
              Check Your Email
            </h1>
            <p className="text-base sm:text-lg text-gray-600">
              We've sent a password reset link to {email}
            </p>
          </div>

          {/* Success Card */}
          <div className="bg-white/80 backdrop-blur-xl rounded-2xl sm:rounded-3xl shadow-2xl border border-gray-100/50 p-6 sm:p-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/>
                </svg>
              </div>
              
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Email Sent Successfully!</h2>
              <p className="text-gray-600 mb-6">
                Please check your email and click the reset link to set a new password. The link will expire in 24 hours.
              </p>
              
              <button 
                onClick={onBackToLogin}
                className="w-full bg-gradient-to-r from-blue-600 to-green-600 text-white py-3 px-4 rounded-xl hover:from-blue-700 hover:to-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 transform hover:scale-[1.02] font-medium text-lg shadow-lg"
              >
                <div className="flex items-center justify-center">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
                  </svg>
                  Back to Login
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <img 
              src="https://cdn.prod.website-files.com/66ba43c0b9849f6f8cb92768/66ba5d35ec7fdb4a95626a94_Zoios.png" 
              alt="ZOIOS Logo" 
              className="w-[150px] h-[150px] object-contain"
            />
          </div>
          <h2 className="text-3xl font-extrabold text-gray-900">Forgot Password?</h2>
          <p className="mt-2 text-sm text-gray-600">
            Enter your email address and we'll send you a reset link
          </p>
        </div>

        <Card>
          <CardContent className="p-6">
            {error && (
              <Alert className="mb-4">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="email">Email address</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  required
                  className="mt-1"
                />
              </div>

              <Button 
                type="submit" 
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700"
              >
                {loading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Sending...
                  </div>
                ) : (
                  <div className="flex items-center justify-center">
                    <Mail className="w-4 h-4 mr-2" />
                    Send Reset Link
                  </div>
                )}
              </Button>

              <Button 
                type="button"
                onClick={onBackToLogin}
                variant="outline" 
                className="w-full"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Login
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ForgotPassword;