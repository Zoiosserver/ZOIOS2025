import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { BarChart3, Lock, Mail, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import Signup from './Signup';
import ForgotPassword from './ForgotPassword';

const Login = () => {
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentView, setCurrentView] = useState('login'); // 'login', 'signup', 'forgot-password'

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Use the preview URL from supervisor config
      const BACKEND_URL = 'https://b74cc3d4-0a98-4583-9eb2-4600dc1ad1aa.preview.emergentagent.com';
      console.log('Login - Using backend URL:', BACKEND_URL);
      
      const response = await fetch(`${BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password
        })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        toast.success('Login successful! Redirecting...');
        window.location.href = '/'; // Force reload to trigger auth check
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Login failed');
        toast.error(errorData.detail || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Network error - cannot connect to server');
      toast.error('Network error - cannot connect to server');
    }
    
    setLoading(false);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // Show different views based on current state
  if (currentView === 'signup') {
    return <Signup onBackToLogin={() => setCurrentView('login')} />;
  }

  if (currentView === 'forgot-password') {
    return <ForgotPassword onBackToLogin={() => setCurrentView('login')} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <img 
              src="https://customer-assets.emergentagent.com/job_outreach-pulse-3/artifacts/5adajuhk_Zoios.png" 
              alt="ZOIOS Logo" 
              className="object-contain"
              style={{width: '150px', height: '150px'}}
            />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome to ZOIOS</h1>
          <p className="text-gray-600">Sign in to your ERP account</p>
        </div>

        {/* Login Form */}
        <Card className="shadow-xl border-0">
          <CardHeader className="space-y-1 pb-6">
            <CardTitle className="text-2xl font-semibold text-center">Sign In</CardTitle>
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
                <Label htmlFor="email" className="text-sm font-medium">Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    placeholder="Enter your email"
                    value={formData.email}
                    onChange={handleChange}
                    className="pl-10"
                    required
                    data-testid="login-email"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    placeholder="Enter your password"
                    value={formData.password}
                    onChange={handleChange}
                    className="pl-10"
                    required
                    data-testid="login-password"
                  />
                </div>
              </div>
              
              <Button 
                type="submit" 
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5"
                disabled={loading}
                data-testid="login-submit-btn"
              >
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>

              {/* Forgot Password Link */}
              <div className="text-center pt-4">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setCurrentView('forgot-password')}
                  className="text-sm text-blue-600 hover:text-blue-700"
                  data-testid="forgot-password-link"
                >
                  Forgot your password?
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Sign Up Link */}
        <Card className="mt-6 bg-gray-50 border-gray-200">
          <CardContent className="p-4 text-center">
            <p className="text-sm text-gray-600 mb-2">
              Don't have an account?
            </p>
            <Button
              variant="outline"
              onClick={() => setCurrentView('signup')}
              className="text-blue-600 border-blue-600 hover:bg-blue-50"
              data-testid="signup-link"
            >
              Create Account
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
};

export default Login;