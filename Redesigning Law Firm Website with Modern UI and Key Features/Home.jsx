import React from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  Brain, 
  FileText, 
  Search, 
  MessageSquare, 
  BarChart3, 
  Scale, 
  Database, 
  Globe, 
  Shield, 
  Zap,
  ChevronRight,
  Star,
  Users,
  Clock,
  CheckCircle
} from 'lucide-react'

const Home = () => {
  const features = [
    {
      id: 'research',
      icon: Search,
      title: 'Legal Research',
      description: 'AI-powered legal research with natural language queries',
      color: 'bg-blue-500',
      path: '/research'
    },
    {
      id: 'documents',
      icon: FileText,
      title: 'Document Analysis',
      description: 'Comprehensive document analysis and insights',
      color: 'bg-green-500',
      path: '/documents'
    },
    {
      id: 'court',
      icon: Scale,
      title: 'Court Simulation',
      description: 'Practice with realistic courtroom scenarios',
      color: 'bg-purple-500',
      path: '/court'
    },
    {
      id: 'database',
      icon: Database,
      title: 'Database Intelligence',
      description: 'Natural language to SQL conversion',
      color: 'bg-orange-500',
      path: '/database'
    },
    {
      id: 'scraping',
      icon: Globe,
      title: 'Web Scraping',
      description: 'Extract data from legal websites',
      color: 'bg-red-500',
      path: '/scraping'
    },
    {
      id: 'analytics',
      icon: BarChart3,
      title: 'Analytics',
      description: 'Comprehensive system analytics and insights',
      color: 'bg-indigo-500',
      path: '/analytics'
    }
  ]

  const stats = [
    { label: 'Active Users', value: '2,500+', icon: Users },
    { label: 'Documents Processed', value: '50K+', icon: FileText },
    { label: 'Research Queries', value: '100K+', icon: Search },
    { label: 'Uptime', value: '99.9%', icon: Clock }
  ]

  const testimonials = [
    {
      name: 'Sarah Johnson',
      role: 'Senior Partner, Johnson & Associates',
      content: 'DALI Legal AI has transformed our research process. What used to take hours now takes minutes.',
      rating: 5
    },
    {
      name: 'Michael Chen',
      role: 'Legal Researcher',
      content: 'The document analysis feature is incredibly accurate and saves us tremendous time.',
      rating: 5
    },
    {
      name: 'Emily Rodriguez',
      role: 'Corporate Counsel',
      content: 'The court simulation feature helped our team prepare for complex cases effectively.',
      rating: 5
    }
  ]

  return (
    <div>
      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <Badge className="mb-4 bg-blue-100 text-blue-800 hover:bg-blue-200">
              <Zap className="w-4 h-4 mr-1" />
              AI-Powered Legal Intelligence
            </Badge>
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              Transform Your Legal Practice with{' '}
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Advanced AI
              </span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              DALI Legal AI combines cutting-edge artificial intelligence with comprehensive legal tools 
              to revolutionize how legal professionals research, analyze, and practice law.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                Start Free Trial
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
              <Button size="lg" variant="outline">
                Watch Demo
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mb-4">
                  <stat.icon className="w-6 h-6 text-blue-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">{stat.value}</div>
                <div className="text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Comprehensive Legal AI Platform
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Everything you need to enhance your legal practice with artificial intelligence
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature) => {
              const IconComponent = feature.icon
              return (
                <Card key={feature.id} className="group hover:shadow-lg transition-all duration-300 cursor-pointer border-0 shadow-md">
                  <CardHeader>
                    <div className={`w-12 h-12 ${feature.color} rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                      <IconComponent className="w-6 h-6 text-white" />
                    </div>
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                    <CardDescription className="text-gray-600">
                      {feature.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Link to={feature.path}>
                      <Button variant="ghost" className="p-0 h-auto text-blue-600 hover:text-blue-700">
                        Explore feature
                        <ChevronRight className="w-4 h-4 ml-1" />
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      </section>

      {/* Chat Feature Highlight */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              AI Legal Assistant
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Get instant help with legal questions, research, and case preparation
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <Card className="border-0 shadow-2xl overflow-hidden">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                    <MessageSquare className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold">AI Legal Assistant</h3>
                    <p className="text-blue-100">Available 24/7 for legal research and guidance</p>
                  </div>
                </div>
              </div>
              <CardContent className="p-8">
                <div className="space-y-4 mb-6">
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                      <Brain className="w-4 h-4 text-white" />
                    </div>
                    <div className="bg-gray-100 rounded-lg p-3 flex-1">
                      <p className="text-gray-800">Hello! I'm your AI legal assistant. I can help you with legal research, document analysis, case preparation, and answer questions about law. How can I assist you today?</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3 justify-end">
                    <div className="bg-blue-600 text-white rounded-lg p-3 max-w-xs">
                      <p>Can you help me research contract law in California?</p>
                    </div>
                    <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                      <Users className="w-4 h-4 text-gray-600" />
                    </div>
                  </div>
                </div>
                <div className="text-center">
                  <Link to="/chat">
                    <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                      Start Chatting
                      <MessageSquare className="w-4 h-4 ml-2" />
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Trusted by Legal Professionals
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              See what legal professionals are saying about DALI Legal AI
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="border-0 shadow-lg">
                <CardContent className="p-6">
                  <div className="flex items-center mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <p className="text-gray-700 mb-4">"{testimonial.content}"</p>
                  <div>
                    <div className="font-semibold text-gray-900">{testimonial.name}</div>
                    <div className="text-sm text-gray-600">{testimonial.role}</div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Transform Your Legal Practice?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of legal professionals who are already using DALI Legal AI to enhance their practice
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100">
              Start Free Trial
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
            <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-600">
              Schedule Demo
            </Button>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Home

