import React, { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Checkbox } from '@/components/ui/checkbox.jsx'
import { 
  Brain, 
  Mail, 
  Lock, 
  Eye, 
  EyeOff,
  ArrowRight,
  Shield,
  Zap,
  Users
} from 'lucide-react'

const Login = () => {
  const [showPassword, setShowPassword] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [rememberMe, setRememberMe] = useState(false)

  const handleLogin = (e) => {
    e.preventDefault()
    // Handle login logic here
    console.log('Login attempt:', { email, password, rememberMe })
  }

  return (
    <div className="min-h-screen flex">
      {/* Left Side - Dark Background with Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 relative overflow-hidden">
          {/* Background Pattern */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-blue-600/5 to-purple-600/5"></div>
          </div>
        
        {/* Content */}
        <div className="relative z-10 flex flex-col justify-center px-12 py-12 text-white">
          {/* Logo and Branding */}
          <div className="mb-12">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-purple-400 rounded-2xl flex items-center justify-center shadow-lg">
                <Brain className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">DALI Legal AI</h1>
                <p className="text-blue-200 text-sm">AI-Powered Legal Intelligence</p>
              </div>
            </div>
            
            <h2 className="text-4xl font-bold mb-4 leading-tight">
              Transform Your Legal Practice with 
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent"> Advanced AI</span>
            </h2>
            <p className="text-xl text-gray-300 mb-8 leading-relaxed">
              Join thousands of legal professionals who trust DALI Legal AI for contract management, 
              legal research, and intelligent document analysis.
            </p>
          </div>

          {/* Features */}
          <div className="space-y-6">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <Shield className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <h3 className="font-semibold">Enterprise Security</h3>
                <p className="text-gray-400 text-sm">Bank-level encryption and compliance</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <Zap className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <h3 className="font-semibold">AI-Powered Insights</h3>
                <p className="text-gray-400 text-sm">Smart contract analysis and recommendations</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                <Users className="w-5 h-5 text-green-400" />
              </div>
              <div>
                <h3 className="font-semibold">Team Collaboration</h3>
                <p className="text-gray-400 text-sm">Real-time collaboration and communication</p>
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="mt-12 grid grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-400">2,500+</div>
              <div className="text-sm text-gray-400">Active Users</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-400">50K+</div>
              <div className="text-sm text-gray-400">Contracts Processed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">99.9%</div>
              <div className="text-sm text-gray-400">Uptime</div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Light Background with Login Form */}
      <div className="w-full lg:w-1/2 bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="lg:hidden flex items-center justify-center space-x-3 mb-8">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold text-gray-900">DALI Legal AI</span>
          </div>

          <Card className="shadow-2xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="text-center pb-6">
              <CardTitle className="text-2xl font-bold text-gray-900 mb-2">
                Sign in to your Legal Portal
              </CardTitle>
              <CardDescription className="text-gray-600">
                Access your AI-powered legal workspace
              </CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-6">
              <form onSubmit={handleLogin} className="space-y-4">
                {/* Email Field */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Email Address</label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <Input
                      type="email"
                      placeholder="Enter your email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="pl-10 h-12 border-gray-200 focus:border-blue-500 focus:ring-blue-500"
                      required
                    />
                  </div>
                </div>

                {/* Password Field */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Password</label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <Input
                      type={showPassword ? "text" : "password"}
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="pl-10 pr-10 h-12 border-gray-200 focus:border-blue-500 focus:ring-blue-500"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Remember Me & Forgot Password */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="remember"
                      checked={rememberMe}
                      onCheckedChange={setRememberMe}
                    />
                    <label htmlFor="remember" className="text-sm text-gray-600">
                      Remember me
                    </label>
                  </div>
                  <a href="#" className="text-sm text-blue-600 hover:text-blue-700 font-medium">
                    Forgot password?
                  </a>
                </div>

                {/* Sign In Button */}
                <Button 
                  type="submit" 
                  className="w-full h-12 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium shadow-lg hover:shadow-xl transition-all duration-200"
                >
                  Sign In
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </form>

              {/* Divider */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-200"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-white text-gray-500">Or continue with</span>
                </div>
              </div>

              {/* SSO Options */}
              <div className="grid grid-cols-2 gap-3">
                <Button variant="outline" className="h-12 border-gray-200 hover:bg-gray-50">
                  <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  Google
                </Button>
                <Button variant="outline" className="h-12 border-gray-200 hover:bg-gray-50">
                  <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
                  </svg>
                  Apple
                </Button>
              </div>

              {/* Sign Up Link */}
              <div className="text-center">
                <p className="text-sm text-gray-600">
                  Don't have an account?{' '}
                  <a href="#" className="text-blue-600 hover:text-blue-700 font-medium">
                    Start your free trial
                  </a>
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Footer */}
          <div className="mt-8 text-center text-xs text-gray-500">
            <p>
              By signing in, you agree to our{' '}
              <a href="#" className="text-blue-600 hover:underline">Terms of Service</a>
              {' '}and{' '}
              <a href="#" className="text-blue-600 hover:underline">Privacy Policy</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login

