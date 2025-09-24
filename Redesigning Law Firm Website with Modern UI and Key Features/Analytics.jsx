import React, { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  FileText, 
  DollarSign, 
  Calendar,
  Download,
  Filter,
  RefreshCw,
  Eye,
  PieChart,
  LineChart,
  Activity
} from 'lucide-react'

const Analytics = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('month')
  const [selectedMetric, setSelectedMetric] = useState('revenue')

  // Mock analytics data
  const analyticsData = {
    overview: {
      totalRevenue: "2,450,000 SAR",
      totalCases: 156,
      activeClients: 89,
      completionRate: "94%"
    },
    revenueByPracticeArea: [
      { area: "Corporate Law", revenue: 850000, percentage: 35, cases: 45 },
      { area: "Litigation", revenue: 650000, percentage: 27, cases: 38 },
      { area: "Real Estate", revenue: 480000, percentage: 20, cases: 28 },
      { area: "Employment Law", revenue: 290000, percentage: 12, cases: 22 },
      { area: "Intellectual Property", revenue: 180000, percentage: 7, cases: 15 }
    ],
    monthlyTrends: [
      { month: "Jan", revenue: 380000, cases: 25, clients: 18 },
      { month: "Feb", revenue: 420000, cases: 28, clients: 22 },
      { month: "Mar", revenue: 450000, cases: 32, clients: 25 },
      { month: "Apr", revenue: 380000, cases: 29, clients: 21 },
      { month: "May", revenue: 520000, cases: 35, clients: 28 },
      { month: "Jun", revenue: 480000, cases: 31, clients: 24 }
    ],
    topClients: [
      { name: "Saudi Aramco", revenue: 450000, cases: 12, status: "Active" },
      { name: "SABIC", revenue: 380000, cases: 8, status: "Active" },
      { name: "Al-Rajhi Bank", revenue: 320000, cases: 15, status: "Active" },
      { name: "STC", revenue: 280000, cases: 10, status: "Active" },
      { name: "SAMBA Bank", revenue: 250000, cases: 9, status: "Active" }
    ],
    caseOutcomes: [
      { outcome: "Won", count: 89, percentage: 57 },
      { outcome: "Settled", count: 45, percentage: 29 },
      { outcome: "Ongoing", count: 22, percentage: 14 }
    ]
  }

  const periods = [
    { value: 'week', label: 'This Week' },
    { value: 'month', label: 'This Month' },
    { value: 'quarter', label: 'This Quarter' },
    { value: 'year', label: 'This Year' }
  ]

  const metrics = [
    { value: 'revenue', label: 'Revenue', icon: DollarSign },
    { value: 'cases', label: 'Cases', icon: FileText },
    { value: 'clients', label: 'Clients', icon: Users },
    { value: 'performance', label: 'Performance', icon: TrendingUp }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <BarChart3 className="w-12 h-12 text-blue-600" />
              <h1 className="text-4xl font-bold text-gray-900">Analytics Dashboard</h1>
            </div>
            <p className="text-xl text-gray-600">
              Comprehensive insights into your legal practice performance and metrics.
            </p>
          </div>
          <div className="flex space-x-2">
            <Button variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Export Report
            </Button>
            <Button variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh Data
            </Button>
          </div>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4 text-gray-500" />
                  <span className="text-sm font-medium">Period:</span>
                  <div className="flex space-x-1">
                    {periods.map((period) => (
                      <Button
                        key={period.value}
                        size="sm"
                        variant={selectedPeriod === period.value ? "default" : "outline"}
                        onClick={() => setSelectedPeriod(period.value)}
                      >
                        {period.label}
                      </Button>
                    ))}
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Filter className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium">Metric:</span>
                <div className="flex space-x-1">
                  {metrics.map((metric) => {
                    const Icon = metric.icon
                    return (
                      <Button
                        key={metric.value}
                        size="sm"
                        variant={selectedMetric === metric.value ? "default" : "outline"}
                        onClick={() => setSelectedMetric(metric.value)}
                      >
                        <Icon className="w-3 h-3 mr-1" />
                        {metric.label}
                      </Button>
                    )
                  })}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Revenue</p>
                  <p className="text-2xl font-bold text-gray-900">{analyticsData.overview.totalRevenue}</p>
                </div>
                <DollarSign className="w-8 h-8 text-green-600" />
              </div>
              <div className="mt-4 flex items-center">
                <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
                <span className="text-sm text-green-600">+12.5% from last month</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Cases</p>
                  <p className="text-2xl font-bold text-gray-900">{analyticsData.overview.totalCases}</p>
                </div>
                <FileText className="w-8 h-8 text-blue-600" />
              </div>
              <div className="mt-4 flex items-center">
                <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
                <span className="text-sm text-green-600">+8.3% from last month</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Active Clients</p>
                  <p className="text-2xl font-bold text-gray-900">{analyticsData.overview.activeClients}</p>
                </div>
                <Users className="w-8 h-8 text-purple-600" />
              </div>
              <div className="mt-4 flex items-center">
                <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
                <span className="text-sm text-green-600">+15.2% from last month</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Success Rate</p>
                  <p className="text-2xl font-bold text-gray-900">{analyticsData.overview.completionRate}</p>
                </div>
                <Activity className="w-8 h-8 text-orange-600" />
              </div>
              <div className="mt-4 flex items-center">
                <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
                <span className="text-sm text-green-600">+2.1% from last month</span>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Revenue by Practice Area */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <PieChart className="w-5 h-5" />
                <span>Revenue by Practice Area</span>
              </CardTitle>
              <CardDescription>
                Distribution of revenue across different legal practice areas
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analyticsData.revenueByPracticeArea.map((area, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div 
                        className="w-4 h-4 rounded-full"
                        style={{ backgroundColor: `hsl(${index * 60}, 70%, 50%)` }}
                      ></div>
                      <div>
                        <p className="font-medium text-gray-900">{area.area}</p>
                        <p className="text-sm text-gray-600">{area.cases} cases</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-gray-900">{area.revenue.toLocaleString()} SAR</p>
                      <p className="text-sm text-gray-600">{area.percentage}%</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Monthly Trends */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <LineChart className="w-5 h-5" />
                <span>Monthly Trends</span>
              </CardTitle>
              <CardDescription>
                Revenue and case trends over the past 6 months
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analyticsData.monthlyTrends.map((month, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 text-center">
                        <p className="font-medium text-gray-900">{month.month}</p>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <div 
                            className="h-2 bg-blue-500 rounded"
                            style={{ width: `${(month.revenue / 600000) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-gray-900">{month.revenue.toLocaleString()} SAR</p>
                      <p className="text-sm text-gray-600">{month.cases} cases</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Top Clients */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="w-5 h-5" />
                <span>Top Clients</span>
              </CardTitle>
              <CardDescription>
                Highest revenue generating clients
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analyticsData.topClients.map((client, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-medium text-blue-600">{index + 1}</span>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{client.name}</p>
                        <p className="text-sm text-gray-600">{client.cases} cases</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-gray-900">{client.revenue.toLocaleString()} SAR</p>
                      <Badge variant="secondary">{client.status}</Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Case Outcomes */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="w-5 h-5" />
                <span>Case Outcomes</span>
              </CardTitle>
              <CardDescription>
                Distribution of case results and outcomes
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analyticsData.caseOutcomes.map((outcome, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div 
                        className="w-4 h-4 rounded-full"
                        style={{ 
                          backgroundColor: outcome.outcome === 'Won' ? '#10b981' : 
                                         outcome.outcome === 'Settled' ? '#f59e0b' : '#6b7280' 
                        }}
                      ></div>
                      <p className="font-medium text-gray-900">{outcome.outcome}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-gray-900">{outcome.count} cases</p>
                      <p className="text-sm text-gray-600">{outcome.percentage}%</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Generate reports and perform analytics tasks
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2">
                <Download className="w-6 h-6" />
                <span>Export Monthly Report</span>
              </Button>
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2">
                <Eye className="w-6 h-6" />
                <span>View Detailed Analytics</span>
              </Button>
              <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2">
                <BarChart3 className="w-6 h-6" />
                <span>Create Custom Dashboard</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Analytics

