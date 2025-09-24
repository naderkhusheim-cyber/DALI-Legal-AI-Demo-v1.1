import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  X, 
  Building, 
  Users, 
  Home, 
  ShoppingCart, 
  Banknote, 
  Lightbulb, 
  Heart, 
  Globe,
  ArrowRight,
  ArrowLeft,
  FileText,
  Briefcase,
  Clock,
  MapPin,
  GraduationCap
} from 'lucide-react'

const NewContractModal = ({ isOpen, onClose, onContractTypeSelect }) => {
  const navigate = useNavigate()
  const [selectedType, setSelectedType] = useState(null)
  const [step, setStep] = useState(1) // 1: Select Type, 2: Select Sub-type

  // Contract types with their sub-types
  const contractTypes = [
    {
      id: 'corporate',
      name: 'Corporate',
      icon: Building,
      color: 'bg-blue-500',
      description: 'Business formation and corporate governance',
      subTypes: [
        { id: 'articles', name: 'Articles of Association (LLC)', description: 'Limited liability company formation documents' },
        { id: 'joint-venture', name: 'Joint Venture Agreements', description: 'Partnership agreements for business ventures' },
        { id: 'shareholders', name: 'Shareholders\' Agreements', description: 'Rights and obligations of shareholders' },
        { id: 'ma', name: 'Mergers and Acquisitions (M&A)', description: 'Corporate restructuring and acquisition agreements' },
        { id: 'liquidation', name: 'Company Conversion or Liquidation', description: 'Corporate dissolution and conversion processes' }
      ]
    },
    {
      id: 'employment',
      name: 'Employment',
      icon: Users,
      color: 'bg-green-500',
      description: 'Employment contracts and labor agreements',
      subTypes: [
        { id: 'standard', name: 'Standard Saudi Employment Contract', description: 'Fixed or indefinite term employment' },
        { id: 'foreign', name: 'Foreign Employment Contract', description: 'Contracts for international employees' },
        { id: 'flexible', name: 'Flexible Work Contract', description: 'Hour-based and flexible arrangements' },
        { id: 'training', name: 'Training & Employment Contract', description: 'Combined training and employment agreements' }
      ]
    },
    {
      id: 'real-estate',
      name: 'Real Estate',
      icon: Home,
      color: 'bg-orange-500',
      description: 'Property transactions and real estate deals',
      subTypes: [
        { id: 'sale', name: 'Real Estate Sale Agreement', description: 'Property purchase and sale contracts' },
        { id: 'lease', name: 'Residential or Commercial Lease', description: 'Property rental and leasing agreements' },
        { id: 'development', name: 'Real Estate Development Agreement', description: 'Property development and construction contracts' },
        { id: 'management', name: 'Property Management Contract', description: 'Property management service agreements' }
      ]
    },
    {
      id: 'commercial',
      name: 'Commercial',
      icon: ShoppingCart,
      color: 'bg-purple-500',
      description: 'Business transactions and commercial agreements',
      subTypes: [
        { id: 'distribution', name: 'Distribution Agreements', description: 'Product distribution and supply chain contracts' },
        { id: 'agency', name: 'Commercial Agency Agreements', description: 'Registered commercial representation contracts' },
        { id: 'franchise', name: 'Franchise Agreements', description: 'Business franchise and licensing contracts' },
        { id: 'procurement', name: 'Supply and Procurement Contracts', description: 'Goods and services procurement agreements' },
        { id: 'b2b', name: 'B2B Sales and Purchase Agreements', description: 'Business-to-business transaction contracts' }
      ]
    },
    {
      id: 'banking',
      name: 'Banking & Finance',
      icon: Banknote,
      color: 'bg-emerald-500',
      description: 'Financial services and banking contracts',
      subTypes: [
        { id: 'loan', name: 'Loan Agreements', description: 'Personal and corporate lending contracts' },
        { id: 'mortgage', name: 'Mortgage Contracts', description: 'Property financing and mortgage agreements' },
        { id: 'islamic', name: 'Islamic Financing', description: 'Murabaha, Ijara, and Sharia-compliant financing' },
        { id: 'guarantee', name: 'Guarantee and Security Contracts', description: 'Financial guarantees and security agreements' }
      ]
    },
    {
      id: 'ip',
      name: 'Intellectual Property',
      icon: Lightbulb,
      color: 'bg-yellow-500',
      description: 'IP protection and licensing agreements',
      subTypes: [
        { id: 'trademark', name: 'Trademark Licensing Agreement', description: 'Trademark usage and licensing contracts' },
        { id: 'copyright', name: 'Copyright and Publishing Agreement', description: 'Copyright licensing and publishing contracts' },
        { id: 'software', name: 'Software Licensing Agreements', description: 'Software usage and distribution licenses' },
        { id: 'patent', name: 'Patent Assignment or Licensing', description: 'Patent rights and licensing agreements' }
      ]
    },
    {
      id: 'family',
      name: 'Family & Personal Status',
      icon: Heart,
      color: 'bg-pink-500',
      description: 'Family law and personal status contracts',
      subTypes: [
        { id: 'marriage', name: 'Official Marriage Contracts', description: 'Court or notary-authorized marriage contracts' },
        { id: 'divorce', name: 'Divorce Settlement Agreement', description: 'Divorce proceedings and settlement agreements' },
        { id: 'custody', name: 'Child Custody Agreement', description: 'Child custody and visitation arrangements' },
        { id: 'alimony', name: 'Alimony and Support Agreement', description: 'Financial support and alimony contracts' }
      ]
    },
    {
      id: 'international',
      name: 'International',
      icon: Globe,
      color: 'bg-indigo-500',
      description: 'Cross-border and international agreements',
      subTypes: [
        { id: 'sales', name: 'Cross-border Sales Contracts', description: 'CISG-based international sales agreements' },
        { id: 'agency-intl', name: 'International Agency Contracts', description: 'International franchise and agency agreements' },
        { id: 'arbitration', name: 'International Arbitration Clauses', description: 'Cross-border dispute resolution agreements' }
      ]
    }
  ]

  const handleTypeSelect = (type) => {
    setSelectedType(type)
    setStep(2)
  }

  const handleSubTypeSelect = (subType) => {
    const contractData = {
      type: selectedType,
      subType: subType
    }
    
    // Close modal first
    onClose()
    
    // Navigate to contract drafting page with contract data
    navigate('/contract-drafting', { 
      state: { contractData } 
    })
    
    // Also call the original callback if provided
    if (onContractTypeSelect) {
      onContractTypeSelect(contractData)
    }
  }

  const handleBack = () => {
    setStep(1)
    setSelectedType(null)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            {step === 2 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleBack}
                className="mr-2"
              >
                <ArrowLeft className="w-4 h-4" />
              </Button>
            )}
            <FileText className="w-6 h-6 text-blue-600" />
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                {step === 1 ? 'Choose Contract Type' : `Select ${selectedType?.name} Contract`}
              </h2>
              <p className="text-sm text-gray-600">
                {step === 1 
                  ? 'Select the type of contract you want to create' 
                  : 'Choose the specific contract sub-type for your needs'
                }
              </p>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {step === 1 ? (
            // Step 1: Contract Types
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {contractTypes.map((type) => {
                const IconComponent = type.icon
                return (
                  <Card 
                    key={type.id}
                    className="cursor-pointer hover:shadow-lg transition-all duration-200 hover:scale-105 border-2 hover:border-blue-200"
                    onClick={() => handleTypeSelect(type)}
                  >
                    <CardContent className="p-6 text-center">
                      <div className={`w-12 h-12 ${type.color} rounded-xl flex items-center justify-center mx-auto mb-4 shadow-lg`}>
                        <IconComponent className="w-6 h-6 text-white" />
                      </div>
                      <h3 className="font-semibold text-gray-900 mb-2">{type.name}</h3>
                      <p className="text-sm text-gray-600 leading-relaxed">{type.description}</p>
                      <div className="mt-4">
                        <Badge variant="secondary" className="text-xs">
                          {type.subTypes.length} templates
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          ) : (
            // Step 2: Sub-types
            <div className="space-y-4">
              {selectedType?.subTypes.map((subType) => (
                <Card 
                  key={subType.id}
                  className="cursor-pointer hover:shadow-md transition-all duration-200 hover:bg-gray-50 border hover:border-blue-200"
                  onClick={() => handleSubTypeSelect(subType)}
                >
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <div className={`w-10 h-10 ${selectedType.color} rounded-lg flex items-center justify-center shadow-sm`}>
                            <FileText className="w-5 h-5 text-white" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900">{subType.name}</h3>
                            <p className="text-sm text-gray-600">{subType.description}</p>
                          </div>
                        </div>
                        
                        {/* Mock additional info */}
                        <div className="flex items-center space-x-4 mt-4 text-xs text-gray-500">
                          <div className="flex items-center space-x-1">
                            <Clock className="w-3 h-3" />
                            <span>~15 min setup</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <MapPin className="w-3 h-3" />
                            <span>Saudi Law</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <GraduationCap className="w-3 h-3" />
                            <span>AI Assisted</span>
                          </div>
                        </div>
                      </div>
                      <ArrowRight className="w-5 h-5 text-gray-400 mt-2" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
          <div className="text-sm text-gray-600">
            {step === 1 
              ? `${contractTypes.length} contract types available`
              : `${selectedType?.subTypes.length} ${selectedType?.name.toLowerCase()} templates available`
            }
          </div>
          <div className="flex space-x-2">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            {step === 2 && (
              <Button onClick={handleBack} variant="outline">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default NewContractModal

