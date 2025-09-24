import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import ChatWidget from './ChatWidget.jsx'
import { 
  Brain, 
  Menu, 
  X,
  Home,
  Search,
  FileText,
  Scale,
  Database,
  Globe,
  BarChart3,
  Settings,
  User
} from 'lucide-react'

const Layout = ({ children }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const location = useLocation()

  const navigationItems = [
    { path: '/', label: 'Home', icon: Home },
    { path: '/research', label: 'Research', icon: Search },
    { path: '/documents', label: 'Documents', icon: FileText },
    { path: '/court', label: 'Court', icon: Scale },
    { path: '/database', label: 'Database', icon: Database },
    { path: '/scraping', label: 'Scraping', icon: Globe },
    { path: '/analytics', label: 'Analytics', icon: BarChart3 },
    { path: '/contracts', label: 'Contracts', icon: FileText },
  ]

  const isActivePath = (path) => {
    if (path === '/') {
      return location.pathname === '/'
    }
    return location.pathname.startsWith(path)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">DALI Legal AI</span>
            </Link>
            
            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center space-x-1">
              {navigationItems.map((item) => {
                const IconComponent = item.icon
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActivePath(item.path)
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-700 hover:text-blue-600 hover:bg-gray-100'
                    }`}
                  >
                    <IconComponent className="w-4 h-4" />
                    <span>{item.label}</span>
                  </Link>
                )
              })}
            </div>

            {/* Desktop Auth Buttons */}
            <div className="hidden lg:flex items-center space-x-4">
              <Button variant="outline" size="sm" asChild>
                <Link to="/login">
                  <User className="w-4 h-4 mr-2" />
                  Sign In
                </Link>
              </Button>
              <Button size="sm" asChild>
                <Link to="/register">Get Started</Link>
              </Button>
            </div>

            {/* Mobile Menu Button */}
            <button 
              className="lg:hidden"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="lg:hidden bg-white border-t border-gray-200">
            <div className="px-4 py-2 space-y-1">
              {navigationItems.map((item) => {
                const IconComponent = item.icon
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActivePath(item.path)
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-700 hover:text-blue-600 hover:bg-gray-100'
                    }`}
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <IconComponent className="w-4 h-4" />
                    <span>{item.label}</span>
                  </Link>
                )
              })}
              <div className="pt-4 space-y-2">
                <Button variant="outline" className="w-full" size="sm" asChild>
                  <Link to="/login">
                    <User className="w-4 h-4 mr-2" />
                    Sign In
                  </Link>
                </Button>
                <Button className="w-full" size="sm" asChild>
                  <Link to="/register">Get Started</Link>
                </Button>
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Chat Widget */}
      <ChatWidget />

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold">DALI Legal AI</span>
              </div>
              <p className="text-gray-400">
                AI-powered legal intelligence platform for modern legal professionals.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Features</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/research" className="hover:text-white transition-colors">Legal Research</Link></li>
                <li><Link to="/documents" className="hover:text-white transition-colors">Document Analysis</Link></li>
                <li><Link to="/court" className="hover:text-white transition-colors">Court Simulation</Link></li>
                <li><Link to="/database" className="hover:text-white transition-colors">Database Intelligence</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">About Us</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Community</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Status</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 DALI Legal AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Layout

