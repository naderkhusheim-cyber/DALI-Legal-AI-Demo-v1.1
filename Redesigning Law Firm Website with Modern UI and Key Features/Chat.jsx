import React, { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  MessageSquare, 
  Send, 
  Brain, 
  Plus,
  Search,
  MoreVertical,
  Paperclip,
  Mic,
  Users,
  Clock,
  CheckCircle,
  FileText,
  Zap,
  Shield,
  Globe
} from 'lucide-react'

const Chat = () => {
  const [currentMessage, setCurrentMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [activeConversation, setActiveConversation] = useState(1)
  const messagesEndRef = useRef(null)

  const conversations = [
    {
      id: 1,
      title: 'Contract Law Research',
      lastMessage: 'Can you help me understand force majeure clauses?',
      timestamp: '2 minutes ago',
      unread: 0,
      type: 'ai'
    },
    {
      id: 2,
      title: 'Document Review Session',
      lastMessage: 'The merger agreement analysis is complete',
      timestamp: '1 hour ago',
      unread: 2,
      type: 'ai'
    },
    {
      id: 3,
      title: 'Case Preparation',
      lastMessage: 'Here are the relevant precedents for your case',
      timestamp: '3 hours ago',
      unread: 0,
      type: 'ai'
    }
  ]

  const messages = [
    {
      id: 1,
      sender: 'ai',
      content: 'Hello! I\'m your AI legal assistant. I can help you with legal research, document analysis, case preparation, and answer questions about law. How can I assist you today?',
      timestamp: '10:30 AM',
      type: 'text'
    },
    {
      id: 2,
      sender: 'user',
      content: 'Can you help me understand the key elements of a valid contract under Saudi Arabian law?',
      timestamp: '10:32 AM',
      type: 'text'
    },
    {
      id: 3,
      sender: 'ai',
      content: 'Certainly! Under Saudi Arabian law, a valid contract requires several key elements:\n\n1. **Offer and Acceptance (Ijab wa Qabul)**: There must be a clear offer from one party and unambiguous acceptance from the other.\n\n2. **Contractual Capacity**: Both parties must have the legal capacity to enter into contracts (age of majority, sound mind).\n\n3. **Lawful Object**: The subject matter must be lawful under Islamic law (Sharia) and Saudi regulations.\n\n4. **Consideration**: There must be mutual consideration, though the concept differs slightly from common law systems.\n\n5. **Compliance with Sharia**: The contract must not violate Islamic principles (no riba/interest, gharar/excessive uncertainty, etc.).\n\nWould you like me to elaborate on any of these elements?',
      timestamp: '10:33 AM',
      type: 'text'
    },
    {
      id: 4,
      sender: 'user',
      content: 'Yes, can you explain more about the Sharia compliance requirements?',
      timestamp: '10:35 AM',
      type: 'text'
    },
    {
      id: 5,
      sender: 'ai',
      content: 'Absolutely! Sharia compliance is fundamental in Saudi Arabian contract law. Here are the key prohibitions and requirements:\n\n**Prohibited Elements (Haram):**\n• **Riba (Interest)**: No interest-based transactions\n• **Gharar (Excessive Uncertainty)**: Contracts must have clear terms\n• **Maysir (Gambling)**: No speculative or gambling elements\n• **Haram Goods/Services**: Cannot involve prohibited items (alcohol, pork, etc.)\n\n**Required Elements:**\n• **Mutual Consent**: Both parties must freely agree\n• **Transparency**: All terms must be clearly disclosed\n• **Fair Exchange**: The exchange must be equitable\n• **Delivery Capability**: Parties must be able to fulfill obligations\n\nThe Saudi Arabian Monetary Authority (SAMA) and the Committee for the Resolution of Securities Disputes provide guidance on Sharia-compliant contracting.',
      timestamp: '10:36 AM',
      type: 'text'
    }
  ]

  const quickActions = [
    { icon: FileText, label: 'Analyze Document', action: 'document' },
    { icon: Search, label: 'Legal Research', action: 'research' },
    { icon: Brain, label: 'Case Analysis', action: 'case' },
    { icon: Globe, label: 'Jurisdiction Info', action: 'jurisdiction' }
  ]

  const features = [
    {
      icon: Brain,
      title: 'AI Legal Expert',
      description: 'Advanced AI trained on legal knowledge and Saudi Arabian law'
    },
    {
      icon: Zap,
      title: 'Instant Responses',
      description: 'Get immediate answers to your legal questions 24/7'
    },
    {
      icon: Shield,
      title: 'Confidential',
      description: 'All conversations are encrypted and confidential'
    },
    {
      icon: Globe,
      title: 'Multi-Language',
      description: 'Support for Arabic and English legal terminology'
    }
  ]

  const handleSendMessage = () => {
    if (!currentMessage.trim()) return

    setIsTyping(true)
    // Simulate AI response delay
    setTimeout(() => {
      setIsTyping(false)
    }, 2000)

    setCurrentMessage('')
  }

  const handleQuickAction = (action) => {
    const actionMessages = {
      document: 'I need help analyzing a legal document. Can you guide me through the process?',
      research: 'I need to research Saudi Arabian employment law. Where should I start?',
      case: 'Can you help me analyze the strengths and weaknesses of my case?',
      jurisdiction: 'What are the key differences between Saudi Arabian and international contract law?'
    }
    setCurrentMessage(actionMessages[action])
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-2xl mb-6">
            <MessageSquare className="w-8 h-8 text-blue-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">AI Legal Assistant</h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Get instant help with legal research, document analysis, and case preparation. 
            Available 24/7 to support your legal work.
          </p>
        </div>

        {/* Chat Interface */}
        <div className="max-w-6xl mx-auto mb-12">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[600px]">
            {/* Conversations Sidebar */}
            <div className="lg:col-span-1">
              <Card className="h-full border-0 shadow-lg">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">Conversations</CardTitle>
                    <Button size="sm" variant="outline">
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="space-y-1">
                    {conversations.map((conversation) => (
                      <div
                        key={conversation.id}
                        className={`p-3 cursor-pointer hover:bg-gray-50 transition-colors ${
                          activeConversation === conversation.id ? 'bg-blue-50 border-r-2 border-blue-600' : ''
                        }`}
                        onClick={() => setActiveConversation(conversation.id)}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <h4 className="font-medium text-sm text-gray-900 truncate">{conversation.title}</h4>
                          {conversation.unread > 0 && (
                            <Badge className="bg-blue-600 text-white text-xs">{conversation.unread}</Badge>
                          )}
                        </div>
                        <p className="text-xs text-gray-600 truncate">{conversation.lastMessage}</p>
                        <p className="text-xs text-gray-400 mt-1">{conversation.timestamp}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Chat Area */}
            <div className="lg:col-span-3">
              <Card className="h-full border-0 shadow-lg flex flex-col">
                {/* Chat Header */}
                <CardHeader className="border-b">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                        <Brain className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <CardTitle className="text-lg">AI Legal Assistant</CardTitle>
                        <CardDescription className="flex items-center">
                          <CheckCircle className="w-3 h-3 text-green-500 mr-1" />
                          Online • Responds instantly
                        </CardDescription>
                      </div>
                    </div>
                    <Button variant="outline" size="sm">
                      <MoreVertical className="w-4 h-4" />
                    </Button>
                  </div>
                </CardHeader>

                {/* Messages */}
                <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[70%] ${message.sender === 'user' ? 'order-2' : 'order-1'}`}>
                        {message.sender === 'ai' && (
                          <div className="flex items-center space-x-2 mb-1">
                            <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                              <Brain className="w-3 h-3 text-white" />
                            </div>
                            <span className="text-xs text-gray-500">AI Assistant</span>
                          </div>
                        )}
                        <div
                          className={`p-3 rounded-lg ${
                            message.sender === 'user'
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-100 text-gray-900'
                          }`}
                        >
                          <p className="whitespace-pre-wrap">{message.content}</p>
                        </div>
                        <p className="text-xs text-gray-500 mt-1 text-right">{message.timestamp}</p>
                      </div>
                    </div>
                  ))}

                  {isTyping && (
                    <div className="flex justify-start">
                      <div className="max-w-[70%]">
                        <div className="flex items-center space-x-2 mb-1">
                          <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                            <Brain className="w-3 h-3 text-white" />
                          </div>
                          <span className="text-xs text-gray-500">AI Assistant is typing...</span>
                        </div>
                        <div className="bg-gray-100 p-3 rounded-lg">
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </CardContent>

                {/* Quick Actions */}
                <div className="border-t p-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4">
                    {quickActions.map((action, index) => {
                      const IconComponent = action.icon
                      return (
                        <Button
                          key={index}
                          variant="outline"
                          size="sm"
                          className="h-auto py-2 px-3 flex flex-col items-center space-y-1"
                          onClick={() => handleQuickAction(action.action)}
                        >
                          <IconComponent className="w-4 h-4" />
                          <span className="text-xs">{action.label}</span>
                        </Button>
                      )
                    })}
                  </div>

                  {/* Message Input */}
                  <div className="flex items-center space-x-2">
                    <Button variant="outline" size="sm">
                      <Paperclip className="w-4 h-4" />
                    </Button>
                    <Input
                      placeholder="Ask me anything about legal research, document analysis, or case preparation..."
                      value={currentMessage}
                      onChange={(e) => setCurrentMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                      className="flex-1"
                    />
                    <Button variant="outline" size="sm">
                      <Mic className="w-4 h-4" />
                    </Button>
                    <Button 
                      onClick={handleSendMessage}
                      disabled={!currentMessage.trim()}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
            AI Assistant Features
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

        {/* Disclaimer */}
        <div className="max-w-4xl mx-auto mt-12">
          <Card className="border-yellow-200 bg-yellow-50">
            <CardContent className="p-6 text-center">
              <p className="text-sm text-yellow-800">
                <strong>Important:</strong> AI responses are for informational purposes only and do not constitute legal advice. 
                Always consult with a qualified attorney for specific legal matters.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default Chat

