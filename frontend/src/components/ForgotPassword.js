import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { BarChart3, Mail, AlertCircle, ArrowLeft, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ForgotPassword = ({ onBackToLogin }) => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/auth/forgot-password`, null, {
        params: { email }
      });

      setSuccess(true);
      toast.success('Password reset instructions sent!');
    } catch (error) {
      console.error('Forgot password error:', error);
      setError(error.response?.data?.detail || 'Failed to send reset instructions');
      toast.error('Failed to send reset instructions');
    }
    
    setLoading(false);
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          {/* Logo and Title */}
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              <div className="w-40 h-40 flex items-center justify-center">
                <img 
                  src="https://customer-assets.emergentagent.com/job_outreach-pulse-3/artifacts/5adajuhk_Zoios.png" 
                  alt="ZOIOS Logo" 
                  className="w-40 h-40 object-contain"
                  style={{width: '150px', height: '150px'}}
                />
              </div>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Check Your Email</h1>
            <p className="text-gray-600">Password reset instructions have been sent</p>
          </div>

          {/* Success Message */}
          <Card className="shadow-xl border-0">
            <CardContent className="p-8 text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Instructions Sent!</h3>
              <p className="text-gray-600 mb-6">
                If an account with that email exists, we've sent password reset instructions to:
              </p>
              <p className="font-medium text-gray-900 mb-6">{email}</p>
              <p className="text-sm text-gray-500 mb-6">
                Please check your email and follow the instructions to reset your password.
              </p>
              
              <Button
                onClick={onBackToLogin}
                variant="outline"
                className="w-full"
                data-testid="back-to-login-from-success-btn"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Login
              </Button>
            </CardContent>
          </Card>

          {/* Footer */}
          <div className="text-center mt-8">
            <p className="text-xs text-gray-500">
              © 2025 ZOIOS. Advanced ERP Platform.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="w-40 h-40 flex items-center justify-center">
              <img 
                src="https://customer-assets.emergentagent.com/job_outreach-pulse-3/artifacts/5adajuhk_Zoios.png" 
                alt="ZOIOS Logo" 
                className="w-40 h-40 object-contain"
                style={{width: '150px', height: '150px'}}
              />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Forgot Password?</h1>
          <p className="text-gray-600">Enter your email to receive reset instructions</p>
        </div>

        {/* Forgot Password Form */}
        <Card className="shadow-xl border-0">
          <CardHeader className="space-y-1 pb-6">
            <CardTitle className="text-2xl font-semibold text-center">Reset Password</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <Alert variant="destructive" className="mb-4">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              
              <div className="space-y-2">
                <Label htmlFor="email" className="text-sm font-medium">Email Address</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    placeholder="Enter your email address"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10"
                    required
                    data-testid="forgot-password-email"
                  />
                </div>
              </div>
              
              <Button 
                type="submit" 
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5"
                disabled={loading}
                data-testid="forgot-password-submit-btn"
              >
                {loading ? 'Sending Instructions...' : 'Send Reset Instructions'}
              </Button>

              <div className="text-center pt-4">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={onBackToLogin}
                  className="text-sm text-gray-600 hover:text-gray-900"
                  data-testid="back-to-login-btn"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to Login
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-xs text-gray-500">
            © 2025 ZOIOS. Advanced ERP Platform.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;