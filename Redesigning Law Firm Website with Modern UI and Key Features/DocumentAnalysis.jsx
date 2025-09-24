import React, { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { 
  FileText, 
  Upload, 
  Brain, 
  Download, 
  Eye,
  AlertTriangle,
  CheckCircle,
  Clock,
  BarChart3,
  FileCheck,
  Zap,
  Shield,
  Search,
  Share
} from 'lucide-react'

const DocumentAnalysis = () => {
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const analysisResults = [
    {
      id: 1,
      fileName: 'Merger_Agreement_Draft.pdf',
      uploadDate: '2024-03-15',
      status: 'completed',
      confidence: 94,
      documentType: 'Merger Agreement',
      keyFindings: [
        'Purchase price: $50M with escrow provisions',
        'Closing conditions include regulatory approval',
        'Material adverse change clause present',
        'Indemnification cap at 20% of purchase price'
      ],
      riskFactors: [
        { level: 'high', text: 'Broad material adverse change definition' },
        { level: 'medium', text: 'Limited survival period for representations' },
        { level: 'low', text: 'Standard termination provisions' }
      ],
      summary: 'This merger agreement contains standard provisions with some buyer-favorable terms. Key areas requiring attention include the MAC clause and indemnification structure.'
    },
    {
      id: 2,
      fileName: 'Employment_Contract_Review.docx',
      uploadDate: '2024-03-14',
      status: 'completed',
      confidence: 89,
      documentType: 'Employment Contract',
      keyFindings: [
        'Non-compete period: 2 years post-termination',
        'Severance package: 6 months base salary',
        'Equity compensation: 10,000 stock options',
        'Confidentiality obligations survive termination'
      ],
      riskFactors: [
        { level: 'medium', text: 'Non-compete may be overly broad' },
        { level: 'low', text: 'Standard confidentiality terms' }
      ],
      summary: 'Employment contract with competitive compensation package. Non-compete clause may need geographic limitations for enforceability.'
    }
  ]

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Analysis',
      description: 'Advanced machine learning extracts key information and insights'
    },
    {
      icon: Shield,
      title: 'Secure Processing',
      description: 'Enterprise-grade security ensures your documents remain confidential'
    },
    {
      icon: Zap,
      title: 'Instant Results',
      description: 'Get comprehensive analysis in minutes, not hours'
    },
    {
      icon: FileCheck,
      title: 'Multiple Formats',
      description: 'Support for PDF, Word, and other common document formats'
    }
  ]

  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files)
    setUploadedFiles(prev => [...prev, ...files])
    setIsAnalyzing(true)
    
    // Simulate analysis
    setTimeout(() => {
      setIsAnalyzing(false)
    }, 3000)
  }

  const getRiskColor = (level) => {
    switch (level) {
      case 'high': return 'text-red-600 bg-red-100'
      case 'medium': return 'text-yellow-600 bg-yellow-100'
      case 'low': return 'text-green-600 bg-green-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-2xl mb-6">
            <FileText className="w-8 h-8 text-green-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Document Analysis</h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Upload legal documents and get comprehensive AI-powered analysis including key terms, 
            risk factors, and actionable insights to support your legal work.
          </p>
        </div>

        {/* Upload Section */}
        <div className="max-w-4xl mx-auto mb-12">
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Upload className="w-5 h-5 mr-2 text-green-600" />
                Upload Documents for Analysis
              </CardTitle>
              <CardDescription>
                Supported formats: PDF, DOC, DOCX, TXT. Maximum file size: 50MB per document.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-green-400 transition-colors">
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-lg text-gray-600 mb-2">Drag and drop your documents here</p>
                <p className="text-sm text-gray-500 mb-4">or</p>
                <label htmlFor="file-upload" className="cursor-pointer">
                  <Button className="bg-green-600 hover:bg-green-700">
                    Choose Files
                  </Button>
                  <input
                    id="file-upload"
                    type="file"
                    multiple
                    accept=".pdf,.doc,.docx,.txt"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </label>
              </div>

              {isAnalyzing && (
                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center mb-2">
                    <Brain className="w-5 h-5 text-blue-600 mr-2" />
                    <span className="font-medium text-blue-900">Analyzing documents...</span>
                  </div>
                  <Progress value={75} className="w-full" />
                  <p className="text-sm text-blue-700 mt-2">Processing document structure and extracting key information</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Analysis Results */}
        <div className="max-w-6xl mx-auto mb-12">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Analysis Results</h2>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Export All
              </Button>
              <Button variant="outline" size="sm">
                <Share className="w-4 h-4 mr-2" />
                Share
              </Button>
            </div>
          </div>

          <div className="space-y-8">
            {analysisResults.map((result) => (
              <Card key={result.id} className="border-0 shadow-lg">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                        <FileText className="w-5 h-5 text-green-600" />
                      </div>
                      <div>
                        <CardTitle className="text-lg">{result.fileName}</CardTitle>
                        <CardDescription className="flex items-center space-x-4">
                          <span className="flex items-center">
                            <Clock className="w-4 h-4 mr-1" />
                            {result.uploadDate}
                          </span>
                          <Badge variant="outline">{result.documentType}</Badge>
                          <span className="flex items-center text-green-600">
                            <CheckCircle className="w-4 h-4 mr-1" />
                            {result.confidence}% confidence
                          </span>
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button variant="outline" size="sm">
                        <Eye className="w-4 h-4 mr-2" />
                        View
                      </Button>
                      <Button size="sm">
                        <Download className="w-4 h-4 mr-2" />
                        Download Report
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Summary */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Executive Summary</h4>
                    <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">{result.summary}</p>
                  </div>

                  {/* Key Findings */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">Key Findings</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {result.keyFindings.map((finding, index) => (
                        <div key={index} className="flex items-start space-x-2 p-3 bg-blue-50 rounded-lg">
                          <CheckCircle className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                          <span className="text-sm text-blue-900">{finding}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Risk Factors */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">Risk Assessment</h4>
                    <div className="space-y-2">
                      {result.riskFactors.map((risk, index) => (
                        <div key={index} className="flex items-start space-x-2 p-3 rounded-lg border">
                          <AlertTriangle className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                            risk.level === 'high' ? 'text-red-600' : 
                            risk.level === 'medium' ? 'text-yellow-600' : 'text-green-600'
                          }`} />
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-1">
                              <Badge className={`text-xs ${getRiskColor(risk.level)}`}>
                                {risk.level.toUpperCase()} RISK
                              </Badge>
                            </div>
                            <span className="text-sm text-gray-700">{risk.text}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Features Section */}
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
            Advanced Document Analysis Features
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => {
              const IconComponent = feature.icon
              return (
                <Card key={index} className="text-center border-0 shadow-md">
                  <CardContent className="p-6">
                    <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg mb-4">
                      <IconComponent className="w-6 h-6 text-green-600" />
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

export default DocumentAnalysis

