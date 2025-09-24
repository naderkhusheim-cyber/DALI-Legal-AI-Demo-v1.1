import React, { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  Search, 
  Brain, 
  FileText, 
  Clock, 
  Star, 
  Filter,
  Download,
  Bookmark,
  ChevronRight,
  Zap,
  Scale,
  BookOpen,
  Globe
} from 'lucide-react'

const LegalResearch = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [isSearching, setIsSearching] = useState(false)

  const recentSearches = [
    'Contract Law in California',
    'Employment Rights Saudi Arabia',
    'Intellectual Property Disputes',
    'Corporate Merger Regulations',
    'Criminal Defense Procedures'
  ]

  const searchResults = [
    {
      title: 'California Contract Law: Essential Elements and Enforceability',
      source: 'California Civil Code Section 1550-1701',
      relevance: 98,
      type: 'Statute',
      summary: 'Comprehensive overview of contract formation, consideration, and enforceability requirements under California law.',
      date: '2024-01-15',
      citations: 45
    },
    {
      title: 'Breach of Contract Remedies in California Courts',
      source: 'California Court of Appeals, 2nd District',
      relevance: 95,
      type: 'Case Law',
      summary: 'Recent appellate decisions on damages, specific performance, and other remedies for contract breaches.',
      date: '2024-02-20',
      citations: 32
    },
    {
      title: 'Contract Interpretation Standards: Recent Developments',
      source: 'California Supreme Court',
      relevance: 92,
      type: 'Case Law',
      summary: 'Latest guidance on interpreting ambiguous contract terms and the parol evidence rule.',
      date: '2024-03-10',
      citations: 28
    }
  ]

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Analysis',
      description: 'Advanced natural language processing understands complex legal queries'
    },
    {
      icon: Scale,
      title: 'Jurisdiction-Specific',
      description: 'Focused on Saudi Arabian legal system with international law coverage'
    },
    {
      icon: BookOpen,
      title: 'Comprehensive Sources',
      description: 'Access to statutes, case law, regulations, and legal commentary'
    },
    {
      icon: Zap,
      title: 'Instant Results',
      description: 'Get relevant legal information in seconds, not hours'
    }
  ]

  const handleSearch = () => {
    setIsSearching(true)
    // Simulate search delay
    setTimeout(() => {
      setIsSearching(false)
    }, 2000)
  }

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-2xl mb-6">
            <Search className="w-8 h-8 text-blue-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Legal Research Assistant</h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Ask questions about Saudi Arabian law in natural language and get comprehensive, 
            AI-powered research results with relevant citations and analysis.
          </p>
        </div>

        {/* Search Interface */}
        <div className="max-w-4xl mx-auto mb-12">
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Brain className="w-5 h-5 mr-2 text-blue-600" />
                AI Legal Research Query
              </CardTitle>
              <CardDescription>
                Ask your legal question in plain English. Our AI will analyze and provide relevant legal information.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex space-x-2">
                <Input
                  placeholder="e.g., What are the requirements for a valid contract in Saudi Arabia?"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1"
                />
                <Button 
                  onClick={handleSearch}
                  disabled={isSearching || !searchQuery.trim()}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {isSearching ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Searching...
                    </>
                  ) : (
                    <>
                      <Search className="w-4 h-4 mr-2" />
                      Research
                    </>
                  )}
                </Button>
              </div>
              
              {/* Recent Searches */}
              <div>
                <p className="text-sm text-gray-600 mb-2">Recent searches:</p>
                <div className="flex flex-wrap gap-2">
                  {recentSearches.map((search, index) => (
                    <Badge 
                      key={index} 
                      variant="secondary" 
                      className="cursor-pointer hover:bg-blue-100"
                      onClick={() => setSearchQuery(search)}
                    >
                      {search}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Search Results */}
        {searchQuery && (
          <div className="max-w-6xl mx-auto mb-12">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Research Results</h2>
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="sm">
                  <Filter className="w-4 h-4 mr-2" />
                  Filter
                </Button>
                <Button variant="outline" size="sm">
                  <Download className="w-4 h-4 mr-2" />
                  Export
                </Button>
              </div>
            </div>

            <div className="space-y-6">
              {searchResults.map((result, index) => (
                <Card key={index} className="border-0 shadow-md hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <Badge variant="outline" className="text-xs">
                            {result.type}
                          </Badge>
                          <div className="flex items-center">
                            <Star className="w-4 h-4 text-yellow-400 fill-current" />
                            <span className="text-sm text-gray-600 ml-1">{result.relevance}% relevant</span>
                          </div>
                        </div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">{result.title}</h3>
                        <p className="text-gray-600 mb-3">{result.summary}</p>
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <span className="flex items-center">
                            <Globe className="w-4 h-4 mr-1" />
                            {result.source}
                          </span>
                          <span className="flex items-center">
                            <Clock className="w-4 h-4 mr-1" />
                            {result.date}
                          </span>
                          <span className="flex items-center">
                            <FileText className="w-4 h-4 mr-1" />
                            {result.citations} citations
                          </span>
                        </div>
                      </div>
                      <div className="flex flex-col space-y-2 ml-4">
                        <Button variant="outline" size="sm">
                          <Bookmark className="w-4 h-4 mr-2" />
                          Save
                        </Button>
                        <Button size="sm">
                          View Details
                          <ChevronRight className="w-4 h-4 ml-2" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Features Section */}
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
            Why Choose Our Legal Research Assistant?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => {
              const IconComponent = feature.icon
              return (
                <Card key={index} className="text-center border-0 shadow-md">
                  <CardContent className="p-6">
                    <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mb-4">
                      <IconComponent className="w-6 h-6 text-blue-600" />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                    <p className="text-gray-600">{feature.description}</p>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

export default LegalResearch

