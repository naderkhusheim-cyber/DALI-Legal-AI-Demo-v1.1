import React, { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  MessageSquare, 
  Send, 
  Search,
  X,
  Minimize2,
  Maximize2,
  Users,
  Circle,
  Phone,
  Video,
  MoreVertical,
  Paperclip,
  Smile
} from 'lucide-react'

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [activeChat, setActiveChat] = useState(null)
  const [currentMessage, setCurrentMessage] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const messagesEndRef = useRef(null)

  // Mock users data
  const users = [
    {
      id: 1,
      name: 'Sarah Johnson',
      role: 'Senior Partner',
      avatar: 'SJ',
      isOnline: true,
      lastSeen: 'Online',
      unreadCount: 3
    },
    {
      id: 2,
      name: 'Michael Chen',
      role: 'Legal Researcher',
      avatar: 'MC',
      isOnline: true,
      lastSeen: 'Online',
      unreadCount: 0
    },
    {
      id: 3,
      name: 'Emily Rodriguez',
      role: 'Corporate Counsel',
      avatar: 'ER',
      isOnline: false,
      lastSeen: '2 hours ago',
      unreadCount: 1
    },
    {
      id: 4,
      name: 'David Kim',
      role: 'Paralegal',
      avatar: 'DK',
      isOnline: false,
      lastSeen: '1 day ago',
      unreadCount: 0
    },
    {
      id: 5,
      name: 'Lisa Wang',
      role: 'Contract Specialist',
      avatar: 'LW',
      isOnline: true,
      lastSeen: 'Online',
      unreadCount: 0
    }
  ]

  // Mock messages for active chat
  const messages = activeChat ? [
    {
      id: 1,
      senderId: activeChat.id,
      senderName: activeChat.name,
      content: 'Hi! I need your help with the merger agreement review.',
      timestamp: '10:30 AM',
      isOwn: false
    },
    {
      id: 2,
      senderId: 'current',
      senderName: 'You',
      content: 'Sure! I can help you with that. Which specific sections are you concerned about?',
      timestamp: '10:32 AM',
      isOwn: true
    },
    {
      id: 3,
      senderId: activeChat.id,
      senderName: activeChat.name,
      content: 'The indemnification clauses seem overly broad. Can you take a look?',
      timestamp: '10:35 AM',
      isOwn: false
    }
  ] : []

  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.role.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const onlineUsers = filteredUsers.filter(user => user.isOnline)
  const offlineUsers = filteredUsers.filter(user => !user.isOnline)

  const handleSendMessage = () => {
    if (!currentMessage.trim() || !activeChat) return
    setCurrentMessage('')
  }

  const handleUserSelect = (user) => {
    setActiveChat(user)
  }

  const handleBackToUserList = () => {
    setActiveChat(null)
  }

  const totalUnreadCount = users.reduce((total, user) => total + user.unreadCount, 0)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <Button
          onClick={() => setIsOpen(true)}
          className="bg-blue-600 hover:bg-blue-700 rounded-full w-14 h-14 shadow-lg relative"
        >
          <MessageSquare className="w-6 h-6" />
          {totalUnreadCount > 0 && (
            <Badge className="absolute -top-2 -right-2 bg-red-500 text-white text-xs min-w-[20px] h-5 rounded-full flex items-center justify-center">
              {totalUnreadCount > 99 ? '99+' : totalUnreadCount}
            </Badge>
          )}
        </Button>
      </div>
    )
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <Card className={`shadow-2xl border-0 transition-all duration-300 ${
        isMinimized ? 'w-80 h-12' : 'w-96 h-[600px]'
      }`}>        {/* Header */}
        <CardHeader className="p-3 bg-blue-600 text-white rounded-t-lg flex items-center justify-between relative">
          {activeChat ? (
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                className="text-white hover:bg-blue-700 p-1 h-auto"
                onClick={handleBackToUserList}
              >
                ←
              </Button>
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center text-sm font-medium">
                  {activeChat.avatar}
                </div>
                <div>
                  <CardTitle className="text-sm m-0">{activeChat.name}</CardTitle>
                  <CardDescription className="text-blue-100 text-xs m-0">
                    {activeChat.isOnline ? 'Online' : activeChat.lastSeen}
                  </CardDescription>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <MessageSquare className="w-5 h-5" />
              <CardTitle className="text-sm m-0">Team Chat</CardTitle>
            </div>
          )}
          <div className="flex items-center space-x-1">
            {activeChat && (
              <>
                <Button variant="ghost" size="sm" className="text-white hover:bg-blue-700 p-1 h-auto">
                  <Phone className="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="sm" className="text-white hover:bg-blue-700 p-1 h-auto">
                  <Video className="w-4 h-4" />
                </Button>
              </>
            )}
            <Button
              variant="ghost"
              size="sm"
              className="text-white hover:bg-blue-700 p-1 h-auto"
              onClick={() => setIsMinimized(!isMinimized)}
            >
              {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="text-white hover:bg-blue-700 p-1 h-auto"
              onClick={() => setIsOpen(false)}
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </CardHeader>

        {!isMinimized && (
          <CardContent className="p-0 flex-1 flex flex-col">
            {!activeChat ? (
              // User List View
              <div className="flex-1 flex flex-col">
                {/* Search Bar */}
                <div className="p-3 border-b">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <Input
                      placeholder="Search users..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10 h-8 text-sm"
                    />
                  </div>
                </div>

                {/* Users List */}
                <div className="flex-1 overflow-y-auto">
                  {/* Online Users */}
                  {onlineUsers.length > 0 && (
                    <div>
                      <div className="px-3 py-2 bg-gray-50 border-b">
                        <div className="flex items-center space-x-2">
                          <Circle className="w-3 h-3 text-green-500 fill-current" />
                          <span className="text-xs font-medium text-gray-600">
                            Online ({onlineUsers.length})
                          </span>
                        </div>
                      </div>
                      {onlineUsers.map((user) => (
                        <div
                          key={user.id}
                          className="p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 transition-colors"
                          onClick={() => handleUserSelect(user)}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              <div className="relative">
                                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-sm font-medium text-blue-600">
                                  {user.avatar}
                                </div>
                                <Circle className="absolute -bottom-1 -right-1 w-3 h-3 text-green-500 fill-current bg-white rounded-full" />
                              </div>
                              <div>
                                <p className="text-sm font-medium text-gray-900">{user.name}</p>
                                <p className="text-xs text-gray-500">{user.role}</p>
                              </div>
                            </div>
                            {user.unreadCount > 0 && (
                              <Badge className="bg-red-500 text-white text-xs min-w-[18px] h-4 rounded-full flex items-center justify-center">
                                {user.unreadCount}
                              </Badge>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Offline Users */}
                  {offlineUsers.length > 0 && (
                    <div>
                      <div className="px-3 py-2 bg-gray-50 border-b">
                        <div className="flex items-center space-x-2">
                          <Circle className="w-3 h-3 text-gray-400" />
                          <span className="text-xs font-medium text-gray-600">
                            Offline ({offlineUsers.length})
                          </span>
                        </div>
                      </div>
                      {offlineUsers.map((user) => (
                        <div
                          key={user.id}
                          className="p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 transition-colors"
                          onClick={() => handleUserSelect(user)}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              <div className="relative">
                                <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center text-sm font-medium text-gray-600">
                                  {user.avatar}
                                </div>
                                <Circle className="absolute -bottom-1 -right-1 w-3 h-3 text-gray-400 bg-white rounded-full" />
                              </div>
                              <div>
                                <p className="text-sm font-medium text-gray-900">{user.name}</p>
                                <p className="text-xs text-gray-500">{user.lastSeen}</p>
                              </div>
                            </div>
                            {user.unreadCount > 0 && (
                              <Badge className="bg-red-500 text-white text-xs min-w-[18px] h-4 rounded-full flex items-center justify-center">
                                {user.unreadCount}
                              </Badge>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {filteredUsers.length === 0 && (
                    <div className="p-6 text-center text-gray-500">
                      <Users className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                      <p className="text-sm">No users found</p>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              // Chat View
              <div className="flex-1 flex flex-col">
                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-3 space-y-3">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.isOwn ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[80%] ${message.isOwn ? 'order-2' : 'order-1'}`}>
                        <div
                          className={`p-2 rounded-lg text-sm ${
                            message.isOwn
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-100 text-gray-900'
                          }`}
                        >
                          <p className="break-words">{message.content}</p>
                        </div>
                        <p className="text-xs text-gray-500 mt-1 text-right">{message.timestamp}</p>
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>

                {/* Message Input */}
                <div className="border-t p-3">
                  <div className="flex items-center space-x-2">
                    <Button variant="outline" size="sm" className="p-1 h-auto">
                      <Paperclip className="w-4 h-4" />
                    </Button>
                    <Input
                      placeholder="Type a message..."
                      value={currentMessage}
                      onChange={(e) => setCurrentMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                      className="flex-1 h-8 text-sm"
                    />
                    <Button variant="outline" size="sm" className="p-1 h-auto">
                      <Smile className="w-4 h-4" />
                    </Button>
                    <Button 
                      onClick={handleSendMessage}
                      disabled={!currentMessage.trim()}
                      size="sm"
                      className="bg-blue-600 hover:bg-blue-700 p-1 h-auto"
                    >
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        )}
      </Card>
    </div>
  )
}

export default ChatWidget

