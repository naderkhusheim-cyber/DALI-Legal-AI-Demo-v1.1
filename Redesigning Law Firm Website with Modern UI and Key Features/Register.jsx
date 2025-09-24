import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Checkbox } from '@/components/ui/checkbox.jsx'
import { 
  Brain, 
  Eye, 
  EyeOff, 
  Mail, 
  Lock, 
  User, 
  Building,
  Phone,
  ArrowLeft,
  CheckCircle,
  Shield,
  Zap,
  Users
} from 'lucide-react'

const Register = () => {
  const navigate = useNavigate()
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    company: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false,
    subscribeNewsletter: false
  })

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    // Handle registration logic here
    console.log('Registration data:', formData)
    // For demo, redirect to login
    navigate('/login')
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
          {/* Logo */}
          <div className="flex items-center space-x-3 mb-8">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl flex items-center justify-center shadow-lg">
              <Brain className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">DALI Legal AI</h1>
              <p className="text-blue-200 text-sm">AI-Powered Legal Intelligence</p>
            </div>
          </div>

          {/* Main Content */}
          <div className="mb-8">
            <h2 className="text-4xl font-bold mb-6 leading-tight">
              Join the Future of
              <span className="block bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Legal Practice
              </span>
            </h2>
            <p className="text-xl text-gray-300 mb-8 leading-relaxed">
              Create your account and unlock the power of AI-driven legal research, 
              document analysis, and contract management.
            </p>
          </div>

          {/* Features */}
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-green-500/20 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-green-400" />
              </div>
              <span className="text-gray-300">AI-powered legal research and analysis</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <Shield className="w-5 h-5 text-blue-400" />
              </div>
              <span className="text-gray-300">Enterprise-grade security and compliance</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <Zap className="w-5 h-5 text-purple-400" />
              </div>
              <span className="text-gray-300">Automated contract drafting and review</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-orange-500/20 rounded-lg flex items-center justify-center">
                <Users className="w-5 h-5 text-orange-400" />
              </div>
              <span className="text-gray-300">Collaborative team workspace</span>
            </div>
          </div>

          {/* Stats */}
          <div className="mt-12 grid grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-white">2,500+</div>
              <div className="text-sm text-gray-400">Legal Professionals</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">50K+</div>
              <div className="text-sm text-gray-400">Documents Processed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">99.9%</div>
              <div className="text-sm text-gray-400">Uptime</div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Registration Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-gray-50">
        <div className="w-full max-w-md">
          {/* Back to Login */}
          <div className="mb-6">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/login')}
              className="text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Sign In
            </Button>
          </div>

          <Card className="shadow-xl border-0">
            <CardHeader className="text-center pb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                <Brain className="w-8 h-8 text-white" />
              </div>
              <CardTitle className="text-2xl font-bold text-gray-900">Create Account</CardTitle>
              <CardDescription className="text-gray-600">
                Join DALI Legal AI and transform your legal practice
              </CardDescription>
            </CardHeader>

            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Name Fields */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">First Name</label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                      <Input
                        type="text"
                        placeholder="John"
                        value={formData.firstName}
                        onChange={(e) => handleInputChange('firstName', e.target.value)}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">Last Name</label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                      <Input
                        type="text"
                        placeholder="Doe"
                        value={formData.lastName}
                        onChange={(e) => handleInputChange('lastName', e.target.value)}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                </div>

                {/* Email */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Email Address</label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      type="email"
                      placeholder="john.doe@lawfirm.com"
                      value={formData.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      className="pl-10"
                      required
                    />
                  </div>
                </div>

                {/* Phone */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Phone Number</label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      type="tel"
                      placeholder="+966 50 123 4567"
                      value={formData.phone}
                      onChange={(e) => handleInputChange('phone', e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>

                {/* Company */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Company/Law Firm</label>
                  <div className="relative">
                    <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      type="text"
                      placeholder="Al-Rajhi Law Firm"
                      value={formData.company}
                      onChange={(e) => handleInputChange('company', e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>

                {/* Password */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Password</label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      type={showPassword ? "text" : "password"}
                      placeholder="Create a strong password"
                      value={formData.password}
                      onChange={(e) => handleInputChange('password', e.target.value)}
                      className="pl-10 pr-10"
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

                {/* Confirm Password */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Confirm Password</label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      type={showConfirmPassword ? "text" : "password"}
                      placeholder="Confirm your password"
                      value={formData.confirmPassword}
                      onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                      className="pl-10 pr-10"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Checkboxes */}
                <div className="space-y-3">
                  <div className="flex items-start space-x-2">
                    <Checkbox
                      id="terms"
                      checked={formData.agreeToTerms}
                      onCheckedChange={(checked) => handleInputChange('agreeToTerms', checked)}
                      required
                    />
                    <label htmlFor="terms" className="text-sm text-gray-600 leading-relaxed">
                      I agree to the{' '}
                      <Link to="/terms" className="text-blue-600 hover:text-blue-700 underline">
                        Terms of Service
                      </Link>{' '}
                      and{' '}
                      <Link to="/privacy" className="text-blue-600 hover:text-blue-700 underline">
                        Privacy Policy
                      </Link>
                    </label>
                  </div>
                  <div className="flex items-start space-x-2">
                    <Checkbox
                      id="newsletter"
                      checked={formData.subscribeNewsletter}
                      onCheckedChange={(checked) => handleInputChange('subscribeNewsletter', checked)}
                    />
                    <label htmlFor="newsletter" className="text-sm text-gray-600">
                      Subscribe to our newsletter for legal AI insights and updates
                    </label>
                  </div>
                </div>

                {/* Submit Button */}
                <Button type="submit" className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium py-2.5">
                  Create Account
                </Button>

                {/* Sign In Link */}
                <div className="text-center pt-4">
                  <span className="text-sm text-gray-600">
                    Already have an account?{' '}
                    <Link to="/login" className="text-blue-600 hover:text-blue-700 font-medium">
                      Sign in here
                    </Link>
                  </span>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default Register

