import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import NewContractModal from '@/components/NewContractModal.jsx'
import { 
  FileText, 
  Plus, 
  Search, 
  Download, 
  Upload, 
  Edit, 
  Eye,
  Calendar,
  DollarSign,
  User,
  Building,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle,
  Filter,
  MoreVertical,
  Copy,
  Archive
} from 'lucide-react'

const ContractManagement = () => {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedStatus, setSelectedStatus] = useState('all')
  const [selectedContract, setSelectedContract] = useState(null)
  const [isNewContractModalOpen, setIsNewContractModalOpen] = useState(false)

  const handleNewContract = () => {
    setIsNewContractModalOpen(true)
  }

  const handleContractTypeSelect = (contractData) => {
    console.log('Selected contract:', contractData)
    // Navigate to the AI-assisted drafting interface
    navigate('/contract-drafting', { 
      state: { contractData } 
    })
  }

  // Mock contracts data
  const contracts = [
    {
      id: 1,
      title: "Software License Agreement - Saudi Aramco",
      client: "Saudi Aramco",
      type: "Software License",
      value: "2,500,000 SAR",
      status: "active",
      startDate: "2024-01-15",
      endDate: "2025-01-15",
      renewalDate: "2024-12-15",
      lastModified: "2024-01-20",
      progress: 100,
      clauses: 45,
      riskLevel: "low"
    },
    {
      id: 2,
      title: "Construction Contract - NEOM Project",
      client: "NEOM",
      type: "Construction",
      value: "15,000,000 SAR",
      status: "pending",
      startDate: "2024-02-01",
      endDate: "2026-02-01",
      renewalDate: "2025-11-01",
      lastModified: "2024-01-18",
      progress: 75,
      clauses: 78,
      riskLevel: "medium"
    },
    {
      id: 3,
      title: "Service Agreement - SABIC",
      client: "SABIC",
      type: "Service Agreement",
      value: "850,000 SAR",
      status: "draft",
      startDate: "2024-03-01",
      endDate: "2025-03-01",
      renewalDate: "2025-02-01",
      lastModified: "2024-01-22",
      progress: 45,
      clauses: 32,
      riskLevel: "low"
    },
    {
      id: 4,
      title: "Employment Contract - Senior Legal Counsel",
      client: "Internal",
      type: "Employment",
      value: "480,000 SAR",
      status: "expired",
      startDate: "2023-01-01",
      endDate: "2024-01-01",
      renewalDate: "2023-12-01",
      lastModified: "2023-12-15",
      progress: 100,
      clauses: 25,
      riskLevel: "high"
    },
    {
      id: 5,
      title: "Partnership Agreement - Al-Rajhi Bank",
      client: "Al-Rajhi Bank",
      type: "Partnership",
      value: "3,200,000 SAR",
      status: "active",
      startDate: "2024-01-10",
      endDate: "2027-01-10",
      renewalDate: "2026-10-10",
      lastModified: "2024-01-25",
      progress: 100,
      clauses: 56,
      riskLevel: "medium"
    }
  ]

  // Mock contract templates
  const contractTemplates = [
    {
      id: 1,
      name: "Software License Agreement",
      description: "Standard software licensing contract template",
      clauses: 35,
      category: "Technology"
    },
    {
      id: 2,
      name: "Service Agreement",
      description: "Professional services contract template",
      clauses: 28,
      category: "Services"
    },
    {
      id: 3,
      name: "Employment Contract",
      description: "Standard employment agreement template",
      clauses: 22,
      category: "HR"
    },
    {
      id: 4,
      name: "Partnership Agreement",
      description: "Business partnership contract template",
      clauses: 42,
      category: "Business"
    }
  ]

  const statusOptions = [
    { value: 'all', label: 'All Contracts', count: contracts.length },
    { value: 'active', label: 'Active', count: contracts.filter(c => c.status === 'active').length },
    { value: 'pending', label: 'Pending', count: contracts.filter(c => c.status === 'pending').length },
    { value: 'draft', label: 'Draft', count: contracts.filter(c => c.status === 'draft').length },
    { value: 'expired', label: 'Expired', count: contracts.filter(c => c.status === 'expired').length }
  ]

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      case 'draft': return 'bg-blue-100 text-blue-800'
      case 'expired': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <CheckCircle className="w-4 h-4" />
      case 'pending': return <Clock className="w-4 h-4" />
      case 'draft': return <Edit className="w-4 h-4" />
      case 'expired': return <XCircle className="w-4 h-4" />
      default: return <FileText className="w-4 h-4" />
    }
  }

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'low': return 'text-green-600'
      case 'medium': return 'text-yellow-600'
      case 'high': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const filteredContracts = contracts.filter(contract => {
    const matchesSearch = contract.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         contract.client.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         contract.type.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = selectedStatus === 'all' || contract.status === selectedStatus
    return matchesSearch && matchesStatus
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <FileText className="w-12 h-12 text-blue-600" />
              <h1 className="text-4xl font-bold text-gray-900">Contract Management</h1>
            </div>
            <p className="text-xl text-gray-600">
              Manage, track, and analyze all your legal contracts in one centralized platform.
            </p>
          </div>
          <div className="flex space-x-2">
            <Button className="bg-blue-600 hover:bg-blue-700" onClick={handleNewContract}>
              <Plus className="w-4 h-4 mr-2" />
              New Contract
            </Button>
            <Button variant="outline">
              <Upload className="w-4 h-4 mr-2" />
              Import
            </Button>
          </div>
        </div>

        {/* Filters and Search */}
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between space-x-4">
              <div className="flex items-center space-x-4 flex-1">
                <div className="relative flex-1 max-w-md">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <Input
                    placeholder="Search contracts, clients, or types..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <div className="flex space-x-1">
                  {statusOptions.map((status) => (
                    <Button
                      key={status.value}
                      size="sm"
                      variant={selectedStatus === status.value ? "default" : "outline"}
                      onClick={() => setSelectedStatus(status.value)}
                    >
                      {status.label} ({status.count})
                    </Button>
                  ))}
                </div>
              </div>
              <div className="flex space-x-2">
                <Button variant="outline" size="sm">
                  <Filter className="w-4 h-4 mr-2" />
                  More Filters
                </Button>
                <Button variant="outline" size="sm">
                  <Download className="w-4 h-4 mr-2" />
                  Export
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Contracts List */}
          <div className="lg:col-span-2 space-y-4">
            {filteredContracts.map((contract) => (
              <Card key={contract.id} className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{contract.title}</h3>
                        <Badge className={getStatusColor(contract.status)}>
                          {getStatusIcon(contract.status)}
                          <span className="ml-1 capitalize">{contract.status}</span>
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                        <div className="flex items-center space-x-2">
                          <Building className="w-4 h-4" />
                          <span>{contract.client}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <FileText className="w-4 h-4" />
                          <span>{contract.type}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <DollarSign className="w-4 h-4" />
                          <span>{contract.value}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Calendar className="w-4 h-4" />
                          <span>{contract.startDate} - {contract.endDate}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900">{contract.progress}%</p>
                        <p className={`text-xs ${getRiskColor(contract.riskLevel)}`}>
                          {contract.riskLevel} risk
                        </p>
                      </div>
                      <Button variant="ghost" size="sm">
                        <MoreVertical className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  
                  {/* Progress Bar */}
                  <div className="mb-4">
                    <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                      <span>Completion Progress</span>
                      <span>{contract.clauses} clauses</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${contract.progress}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex space-x-2">
                    <Button size="sm" variant="outline">
                      <Eye className="w-3 h-3 mr-1" />
                      View
                    </Button>
                    <Button size="sm" variant="outline">
                      <Edit className="w-3 h-3 mr-1" />
                      Edit
                    </Button>
                    <Button size="sm" variant="outline">
                      <Copy className="w-3 h-3 mr-1" />
                      Duplicate
                    </Button>
                    <Button size="sm" variant="outline">
                      <Download className="w-3 h-3 mr-1" />
                      Export
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}

            {filteredContracts.length === 0 && (
              <Card>
                <CardContent className="p-12 text-center">
                  <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No contracts found</h3>
                  <p className="text-gray-600 mb-4">
                    No contracts match your current search and filter criteria.
                  </p>
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    Create New Contract
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Stats */}
            <Card>
              <CardHeader>
                <CardTitle>Contract Overview</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Total Value</span>
                  <span className="font-semibold">22,030,000 SAR</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Active Contracts</span>
                  <span className="font-semibold">2</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Expiring Soon</span>
                  <span className="font-semibold text-orange-600">1</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Avg. Risk Level</span>
                  <span className="font-semibold text-yellow-600">Medium</span>
                </div>
              </CardContent>
            </Card>

            {/* Contract Templates */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <FileText className="w-5 h-5" />
                  <span>Contract Templates</span>
                </CardTitle>
                <CardDescription>
                  Pre-built templates for common contract types
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {contractTemplates.map((template) => (
                  <div key={template.id} className="border rounded-lg p-3 hover:bg-gray-50 cursor-pointer">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-medium text-gray-900">{template.name}</h4>
                      <Button size="sm" variant="outline">
                        Use
                      </Button>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{template.description}</p>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <Badge variant="secondary">{template.category}</Badge>
                      <span>{template.clauses} clauses</span>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Clock className="w-5 h-5" />
                  <span>Recent Activity</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                  <div>
                    <p className="text-sm font-medium">Contract signed</p>
                    <p className="text-xs text-gray-600">Partnership Agreement - Al-Rajhi Bank</p>
                    <p className="text-xs text-gray-500">2 hours ago</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                  <div>
                    <p className="text-sm font-medium">Contract updated</p>
                    <p className="text-xs text-gray-600">Service Agreement - SABIC</p>
                    <p className="text-xs text-gray-500">1 day ago</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
                  <div>
                    <p className="text-sm font-medium">Renewal reminder</p>
                    <p className="text-xs text-gray-600">Software License - Saudi Aramco</p>
                    <p className="text-xs text-gray-500">3 days ago</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button variant="outline" className="w-full justify-start" onClick={handleNewContract}>
                  <Plus className="w-4 h-4 mr-2" />
                  Create Contract
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Upload className="w-4 h-4 mr-2" />
                  Import Contracts
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Archive className="w-4 h-4 mr-2" />
                  Archive Old Contracts
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* New Contract Modal */}
      <NewContractModal
        isOpen={isNewContractModalOpen}
        onClose={() => setIsNewContractModalOpen(false)}
        onContractTypeSelect={handleContractTypeSelect}
      />
    </div>
  )
}

export default ContractManagement

