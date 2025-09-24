import React, { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { 
  Globe, 
  Search, 
  Play, 
  Download, 
  History, 
  Settings, 
  FileText, 
  Link,
  CheckCircle,
  AlertCircle,
  Clock,
  Eye,
  Filter,
  Database
} from 'lucide-react'

const WebScraping = () => {
  const [targetUrl, setTargetUrl] = useState('')
  const [scrapingRules, setScrapingRules] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [scrapingResults, setScrapingResults] = useState(null)

  // Mock scraping history
  const scrapingHistory = [
    {
      id: 1,
      url: "https://courts.gov.sa/cases",
      description: "Saudi Court Cases Database",
      timestamp: "2024-01-15 14:30",
      status: "success",
      dataPoints: 156,
      type: "Court Records"
    },
    {
      id: 2,
      url: "https://moj.gov.sa/regulations",
      description: "Ministry of Justice Regulations",
      timestamp: "2024-01-15 13:45",
      status: "success",
      dataPoints: 89,
      type: "Legal Regulations"
    },
    {
      id: 3,
      url: "https://spa.gov.sa/news",
      description: "Saudi Press Agency Legal News",
      timestamp: "2024-01-15 12:20",
      status: "success",
      dataPoints: 234,
      type: "News Articles"
    }
  ]

  // Mock scraping templates
  const scrapingTemplates = [
    {
      name: "Court Cases",
      description: "Extract case numbers, dates, and verdicts",
      selectors: {
        caseNumber: ".case-number",
        date: ".case-date",
        verdict: ".verdict-text"
      }
    },
    {
      name: "Legal News",
      description: "Extract headlines, content, and publication dates",
      selectors: {
        headline: "h1, h2.title",
        content: ".article-content",
        date: ".publish-date"
      }
    },
    {
      name: "Regulations",
      description: "Extract regulation titles, numbers, and effective dates",
      selectors: {
        title: ".regulation-title",
        number: ".regulation-number",
        effectiveDate: ".effective-date"
      }
    }
  ]

  const handleStartScraping = async () => {
    if (!targetUrl.trim()) return
    
    setIsLoading(true)
    
    // Simulate scraping process
    setTimeout(() => {
      const mockResults = {
        url: targetUrl,
        totalPages: 5,
        dataExtracted: [
          {
            title: "قضية رقم 2024/123 - نزاع تجاري",
            caseNumber: "2024/123",
            court: "المحكمة التجارية بالرياض",
            date: "2024-01-15",
            status: "قيد النظر"
          },
          {
            title: "قضية رقم 2024/124 - قضية عمالية",
            caseNumber: "2024/124",
            court: "محكمة العمل بجدة",
            date: "2024-01-14",
            status: "صدر الحكم"
          },
          {
            title: "قضية رقم 2024/125 - نزاع عقاري",
            caseNumber: "2024/125",
            court: "المحكمة العامة بالدمام",
            date: "2024-01-13",
            status: "تحت المراجعة"
          }
        ],
        scrapingTime: "2.3s",
        dataPoints: 156
      }
      
      setScrapingResults(mockResults)
      setIsLoading(false)
    }, 3000)
  }

  const loadTemplate = (template) => {
    setScrapingRules(JSON.stringify(template.selectors, null, 2))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center space-x-3">
            <Globe className="w-12 h-12 text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-900">Web Scraping</h1>
          </div>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Extract valuable legal data from websites, court databases, and regulatory portals with intelligent web scraping tools.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Scraping Interface */}
          <div className="lg:col-span-2 space-y-6">
            {/* URL and Configuration */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Link className="w-5 h-5" />
                  <span>Target Configuration</span>
                </CardTitle>
                <CardDescription>
                  Configure the website URL and data extraction rules
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Target URL</label>
                  <Input
                    placeholder="https://example.com/legal-data"
                    value={targetUrl}
                    onChange={(e) => setTargetUrl(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Scraping Rules (CSS Selectors)</label>
                  <Textarea
                    placeholder='{\n  "title": ".case-title",\n  "date": ".case-date",\n  "content": ".case-content"\n}'
                    value={scrapingRules}
                    onChange={(e) => setScrapingRules(e.target.value)}
                    className="min-h-[120px] font-mono text-sm"
                  />
                </div>
                <div className="flex space-x-2">
                  <Button 
                    onClick={handleStartScraping}
                    disabled={isLoading || !targetUrl.trim()}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    {isLoading ? (
                      <>
                        <Clock className="w-4 h-4 mr-2 animate-spin" />
                        Scraping...
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 mr-2" />
                        Start Scraping
                      </>
                    )}
                  </Button>
                  <Button variant="outline">
                    <Eye className="w-4 h-4 mr-2" />
                    Preview
                  </Button>
                  <Button variant="outline">
                    <Settings className="w-4 h-4 mr-2" />
                    Advanced Settings
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Scraping Results */}
            {scrapingResults && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Database className="w-5 h-5" />
                    <span>Extracted Data</span>
                  </CardTitle>
                  <CardDescription>
                    {scrapingResults.dataPoints} data points extracted from {scrapingResults.totalPages} pages in {scrapingResults.scrapingTime}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {scrapingResults.dataExtracted.map((item, index) => (
                      <div key={index} className="border rounded-lg p-4 hover:bg-gray-50">
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-medium text-gray-900">{item.title}</h4>
                          <Badge variant={item.status === 'صدر الحكم' ? 'default' : 'secondary'}>
                            {item.status}
                          </Badge>
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                          <div>
                            <span className="font-medium">Case Number:</span> {item.caseNumber}
                          </div>
                          <div>
                            <span className="font-medium">Date:</span> {item.date}
                          </div>
                          <div className="col-span-2">
                            <span className="font-medium">Court:</span> {item.court}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-6 flex space-x-2">
                    <Button variant="outline" size="sm">
                      <Download className="w-4 h-4 mr-2" />
                      Export JSON
                    </Button>
                    <Button variant="outline" size="sm">
                      <Download className="w-4 h-4 mr-2" />
                      Export CSV
                    </Button>
                    <Button variant="outline" size="sm">
                      <Database className="w-4 h-4 mr-2" />
                      Save to Database
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Scraping Templates */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <FileText className="w-5 h-5" />
                  <span>Templates</span>
                </CardTitle>
                <CardDescription>
                  Pre-configured scraping templates
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {scrapingTemplates.map((template, index) => (
                  <div key={index} className="border rounded-lg p-3 hover:bg-gray-50">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-medium text-gray-900">{template.name}</h4>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => loadTemplate(template)}
                      >
                        Use
                      </Button>
                    </div>
                    <p className="text-sm text-gray-600">{template.description}</p>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Scraping History */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <History className="w-5 h-5" />
                  <span>Recent Scraping Jobs</span>
                </CardTitle>
                <CardDescription>
                  Your recent web scraping activities
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {scrapingHistory.map((job) => (
                  <div key={job.id} className="border rounded-lg p-3 hover:bg-gray-50 cursor-pointer">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        {job.status === 'success' ? (
                          <CheckCircle className="w-4 h-4 text-green-500" />
                        ) : (
                          <AlertCircle className="w-4 h-4 text-red-500" />
                        )}
                        <Badge variant="secondary" className="text-xs">
                          {job.type}
                        </Badge>
                      </div>
                      <span className="text-xs text-gray-500">{job.timestamp}</span>
                    </div>
                    <p className="text-sm font-medium text-gray-900 mb-1">{job.description}</p>
                    <p className="text-xs text-gray-500 mb-2">{job.url}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">{job.dataPoints} data points</span>
                      <Button size="sm" variant="ghost">
                        <Eye className="w-3 h-3 mr-1" />
                        View
                      </Button>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button variant="outline" className="w-full justify-start">
                  <Globe className="w-4 h-4 mr-2" />
                  Court Records
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <FileText className="w-4 h-4 mr-2" />
                  Legal News
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Filter className="w-4 h-4 mr-2" />
                  Regulations
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

export default WebScraping

