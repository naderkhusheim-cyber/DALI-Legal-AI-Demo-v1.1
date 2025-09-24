import React, { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { 
  Database, 
  Search, 
  Play, 
  Download, 
  History, 
  Code, 
  Table, 
  BarChart3,
  FileText,
  CheckCircle,
  AlertCircle,
  Clock
} from 'lucide-react'

const DatabaseIntelligence = () => {
  const [naturalQuery, setNaturalQuery] = useState('')
  const [sqlQuery, setSqlQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [queryResults, setQueryResults] = useState(null)

  // Mock query history
  const queryHistory = [
    {
      id: 1,
      naturalQuery: "Show me all contracts signed in the last 30 days",
      sqlQuery: "SELECT * FROM contracts WHERE signed_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)",
      timestamp: "2024-01-15 14:30",
      status: "success",
      resultCount: 23
    },
    {
      id: 2,
      naturalQuery: "Find clients with pending litigation cases",
      sqlQuery: "SELECT c.name, l.case_number FROM clients c JOIN litigation l ON c.id = l.client_id WHERE l.status = 'pending'",
      timestamp: "2024-01-15 13:45",
      status: "success",
      resultCount: 8
    },
    {
      id: 3,
      naturalQuery: "Get revenue by practice area for this quarter",
      sqlQuery: "SELECT practice_area, SUM(amount) as revenue FROM invoices WHERE quarter = 'Q1 2024' GROUP BY practice_area",
      timestamp: "2024-01-15 12:20",
      status: "success",
      resultCount: 5
    }
  ]

  // Mock database schema
  const databaseSchema = [
    {
      table: "clients",
      description: "Client information and contact details",
      columns: ["id", "name", "email", "phone", "company", "created_date"]
    },
    {
      table: "contracts",
      description: "Legal contracts and agreements",
      columns: ["id", "client_id", "title", "value", "signed_date", "status"]
    },
    {
      table: "litigation",
      description: "Litigation cases and proceedings",
      columns: ["id", "client_id", "case_number", "court", "status", "filed_date"]
    },
    {
      table: "invoices",
      description: "Billing and payment records",
      columns: ["id", "client_id", "amount", "practice_area", "date", "status"]
    }
  ]

  const handleNaturalQuery = async () => {
    if (!naturalQuery.trim()) return
    
    setIsLoading(true)
    
    // Simulate AI processing
    setTimeout(() => {
      // Mock SQL generation based on natural language
      let generatedSQL = ""
      if (naturalQuery.toLowerCase().includes("contract")) {
        generatedSQL = "SELECT * FROM contracts WHERE created_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
      } else if (naturalQuery.toLowerCase().includes("client")) {
        generatedSQL = "SELECT name, email, company FROM clients ORDER BY created_date DESC"
      } else if (naturalQuery.toLowerCase().includes("revenue") || naturalQuery.toLowerCase().includes("billing")) {
        generatedSQL = "SELECT practice_area, SUM(amount) as total_revenue FROM invoices GROUP BY practice_area"
      } else {
        generatedSQL = "SELECT * FROM clients LIMIT 10"
      }
      
      setSqlQuery(generatedSQL)
      setIsLoading(false)
    }, 2000)
  }

  const executeQuery = () => {
    if (!sqlQuery.trim()) return
    
    setIsLoading(true)
    
    // Simulate query execution
    setTimeout(() => {
      const mockResults = {
        columns: ["ID", "Name", "Email", "Company", "Created Date"],
        rows: [
          ["1", "Ahmed Al-Rashid", "ahmed@company.sa", "Al-Rashid Holdings", "2024-01-10"],
          ["2", "Fatima Al-Zahra", "fatima@legal.sa", "Legal Consultants", "2024-01-12"],
          ["3", "Mohammed bin Salman", "mohammed@corp.sa", "Saudi Corp", "2024-01-14"],
          ["4", "Aisha Al-Mansouri", "aisha@firm.sa", "Law Firm Partners", "2024-01-15"]
        ],
        executionTime: "0.045s",
        rowCount: 4
      }
      
      setQueryResults(mockResults)
      setIsLoading(false)
    }, 1500)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center space-x-3">
            <Database className="w-12 h-12 text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-900">Database Intelligence</h1>
          </div>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Transform natural language queries into SQL and extract insights from your legal database with AI-powered intelligence.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Query Interface */}
          <div className="lg:col-span-2 space-y-6">
            {/* Natural Language Query */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Search className="w-5 h-5" />
                  <span>Natural Language Query</span>
                </CardTitle>
                <CardDescription>
                  Describe what you want to find in plain English, and we'll convert it to SQL
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  placeholder="e.g., Show me all contracts signed in the last 30 days with values over 100,000 SAR"
                  value={naturalQuery}
                  onChange={(e) => setNaturalQuery(e.target.value)}
                  className="min-h-[100px]"
                />
                <Button 
                  onClick={handleNaturalQuery}
                  disabled={isLoading || !naturalQuery.trim()}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  {isLoading ? (
                    <>
                      <Clock className="w-4 h-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Code className="w-4 h-4 mr-2" />
                      Generate SQL Query
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Generated SQL Query */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Code className="w-5 h-5" />
                  <span>Generated SQL Query</span>
                </CardTitle>
                <CardDescription>
                  Review and modify the generated SQL query before execution
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  placeholder="SQL query will appear here..."
                  value={sqlQuery}
                  onChange={(e) => setSqlQuery(e.target.value)}
                  className="min-h-[120px] font-mono text-sm"
                />
                <div className="flex space-x-2">
                  <Button 
                    onClick={executeQuery}
                    disabled={isLoading || !sqlQuery.trim()}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Execute Query
                  </Button>
                  <Button variant="outline">
                    <Download className="w-4 h-4 mr-2" />
                    Export SQL
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Query Results */}
            {queryResults && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Table className="w-5 h-5" />
                    <span>Query Results</span>
                  </CardTitle>
                  <CardDescription>
                    {queryResults.rowCount} rows returned in {queryResults.executionTime}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse border border-gray-300">
                      <thead>
                        <tr className="bg-gray-50">
                          {queryResults.columns.map((column, index) => (
                            <th key={index} className="border border-gray-300 px-4 py-2 text-left font-medium">
                              {column}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {queryResults.rows.map((row, rowIndex) => (
                          <tr key={rowIndex} className="hover:bg-gray-50">
                            {row.map((cell, cellIndex) => (
                              <td key={cellIndex} className="border border-gray-300 px-4 py-2">
                                {cell}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div className="mt-4 flex space-x-2">
                    <Button variant="outline" size="sm">
                      <Download className="w-4 h-4 mr-2" />
                      Export CSV
                    </Button>
                    <Button variant="outline" size="sm">
                      <BarChart3 className="w-4 h-4 mr-2" />
                      Create Chart
                    </Button>
                    <Button variant="outline" size="sm">
                      <FileText className="w-4 h-4 mr-2" />
                      Generate Report
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Database Schema */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Database className="w-5 h-5" />
                  <span>Database Schema</span>
                </CardTitle>
                <CardDescription>
                  Available tables and columns
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {databaseSchema.map((table, index) => (
                  <div key={index} className="border rounded-lg p-3">
                    <h4 className="font-medium text-gray-900 mb-1">{table.table}</h4>
                    <p className="text-sm text-gray-600 mb-2">{table.description}</p>
                    <div className="flex flex-wrap gap-1">
                      {table.columns.map((column, colIndex) => (
                        <Badge key={colIndex} variant="secondary" className="text-xs">
                          {column}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Query History */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <History className="w-5 h-5" />
                  <span>Recent Queries</span>
                </CardTitle>
                <CardDescription>
                  Your recent database queries
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {queryHistory.map((query) => (
                  <div key={query.id} className="border rounded-lg p-3 hover:bg-gray-50 cursor-pointer">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        {query.status === 'success' ? (
                          <CheckCircle className="w-4 h-4 text-green-500" />
                        ) : (
                          <AlertCircle className="w-4 h-4 text-red-500" />
                        )}
                        <span className="text-sm font-medium">{query.resultCount} results</span>
                      </div>
                      <span className="text-xs text-gray-500">{query.timestamp}</span>
                    </div>
                    <p className="text-sm text-gray-700 mb-1">{query.naturalQuery}</p>
                    <code className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                      {query.sqlQuery.substring(0, 50)}...
                    </code>
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
                  <BarChart3 className="w-4 h-4 mr-2" />
                  Revenue Analytics
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <FileText className="w-4 h-4 mr-2" />
                  Client Reports
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Database className="w-4 h-4 mr-2" />
                  Case Statistics
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DatabaseIntelligence

