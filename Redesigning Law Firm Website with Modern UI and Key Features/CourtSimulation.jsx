import React, { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { 
  Scale, 
  Play, 
  Pause,
  RotateCcw,
  FileText,
  Users,
  Gavel,
  MessageSquare,
  Clock,
  Award,
  BookOpen,
  Brain,
  Shield,
  Target,
  CheckCircle
} from 'lucide-react'

const CourtSimulation = () => {
  const [currentPhase, setCurrentPhase] = useState('preparation')
  const [isSimulationActive, setIsSimulationActive] = useState(false)
  const [userArgument, setUserArgument] = useState('')

  const simulationPhases = [
    { id: 'preparation', name: 'Case Preparation', icon: FileText, completed: true },
    { id: 'opening', name: 'Opening Statements', icon: MessageSquare, completed: false },
    { id: 'evidence', name: 'Evidence Presentation', icon: BookOpen, completed: false },
    { id: 'examination', name: 'Witness Examination', icon: Users, completed: false },
    { id: 'closing', name: 'Closing Arguments', icon: Scale, completed: false },
    { id: 'verdict', name: 'Verdict & Analysis', icon: Gavel, completed: false }
  ]

  const caseScenarios = [
    {
      id: 1,
      title: 'Contract Dispute - Breach of Service Agreement',
      description: 'A software company claims breach of contract against a client who terminated services early.',
      difficulty: 'Intermediate',
      duration: '45 minutes',
      skills: ['Contract Law', 'Commercial Litigation', 'Damages Assessment']
    },
    {
      id: 2,
      title: 'Employment Law - Wrongful Termination',
      description: 'An employee alleges wrongful termination and discrimination in the workplace.',
      difficulty: 'Advanced',
      duration: '60 minutes',
      skills: ['Employment Law', 'Discrimination Claims', 'Evidence Analysis']
    },
    {
      id: 3,
      title: 'Personal Injury - Motor Vehicle Accident',
      description: 'A pedestrian seeks damages after being injured in a motor vehicle accident.',
      difficulty: 'Beginner',
      duration: '30 minutes',
      skills: ['Tort Law', 'Personal Injury', 'Liability Assessment']
    }
  ]

  const simulationHistory = [
    {
      case: 'Contract Dispute - Software Licensing',
      date: '2024-03-10',
      role: 'Defense Attorney',
      outcome: 'Favorable Settlement',
      score: 87,
      duration: '42 minutes'
    },
    {
      case: 'Employment Discrimination Case',
      date: '2024-03-08',
      role: 'Plaintiff Attorney',
      outcome: 'Jury Verdict - Plaintiff',
      score: 92,
      duration: '55 minutes'
    }
  ]

  const features = [
    {
      icon: Brain,
      title: 'AI Judge & Jury',
      description: 'Realistic AI-powered judge and jury responses based on legal precedents'
    },
    {
      icon: Target,
      title: 'Skill Assessment',
      description: 'Detailed feedback on your legal arguments and courtroom performance'
    },
    {
      icon: BookOpen,
      title: 'Case Library',
      description: 'Extensive library of real-world case scenarios across practice areas'
    },
    {
      icon: Shield,
      title: 'Safe Practice',
      description: 'Risk-free environment to practice and improve your litigation skills'
    }
  ]

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Beginner': return 'bg-green-100 text-green-800'
      case 'Intermediate': return 'bg-yellow-100 text-yellow-800'
      case 'Advanced': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-100 rounded-2xl mb-6">
            <Scale className="w-8 h-8 text-purple-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Court Simulation</h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Practice your litigation skills in realistic courtroom scenarios with AI-powered 
            judges, opposing counsel, and witnesses. Perfect your arguments in a safe environment.
          </p>
        </div>

        {/* Active Simulation */}
        {isSimulationActive && (
          <div className="max-w-6xl mx-auto mb-12">
            <Card className="border-0 shadow-lg">
              <CardHeader className="bg-gradient-to-r from-purple-600 to-blue-600 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-xl">Contract Dispute Simulation</CardTitle>
                    <CardDescription className="text-purple-100">
                      Phase: Opening Statements • Role: Plaintiff Attorney
                    </CardDescription>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button variant="outline" size="sm" className="text-white border-white hover:bg-white hover:text-purple-600">
                      <Pause className="w-4 h-4 mr-2" />
                      Pause
                    </Button>
                    <Button variant="outline" size="sm" className="text-white border-white hover:bg-white hover:text-purple-600">
                      <RotateCcw className="w-4 h-4 mr-2" />
                      Reset
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-6">
                {/* Progress */}
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Simulation Progress</span>
                    <span className="text-sm text-gray-500">Phase 2 of 6</span>
                  </div>
                  <Progress value={33} className="w-full" />
                </div>

                {/* Phase Navigation */}
                <div className="grid grid-cols-3 md:grid-cols-6 gap-2 mb-6">
                  {simulationPhases.map((phase, index) => {
                    const IconComponent = phase.icon
                    return (
                      <div
                        key={phase.id}
                        className={`p-3 rounded-lg text-center transition-colors ${
                          phase.completed
                            ? 'bg-green-100 text-green-700'
                            : currentPhase === phase.id
                            ? 'bg-purple-100 text-purple-700'
                            : 'bg-gray-100 text-gray-500'
                        }`}
                      >
                        <IconComponent className="w-5 h-5 mx-auto mb-1" />
                        <p className="text-xs font-medium">{phase.name}</p>
                      </div>
                    )
                  })}
                </div>

                {/* Courtroom Interface */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Judge Response */}
                  <div className="lg:col-span-2">
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center text-lg">
                          <Gavel className="w-5 h-5 mr-2" />
                          Judge's Response
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="bg-gray-50 p-4 rounded-lg mb-4">
                          <p className="text-gray-800">
                            "Counsel, please proceed with your opening statement. The court is ready to hear 
                            your client's position regarding the alleged breach of the software licensing agreement. 
                            Please be concise and focus on the key facts and legal theories."
                          </p>
                        </div>
                        <Textarea
                          placeholder="Enter your opening statement here..."
                          value={userArgument}
                          onChange={(e) => setUserArgument(e.target.value)}
                          className="min-h-[120px] mb-4"
                        />
                        <div className="flex items-center space-x-2">
                          <Button className="bg-purple-600 hover:bg-purple-700">
                            <MessageSquare className="w-4 h-4 mr-2" />
                            Present Argument
                          </Button>
                          <Button variant="outline">
                            <FileText className="w-4 h-4 mr-2" />
                            Reference Case Law
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Case Information */}
                  <div>
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Case Information</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">Key Facts</h4>
                          <ul className="text-sm text-gray-600 space-y-1">
                            <li>• Contract signed January 2024</li>
                            <li>• Early termination in February</li>
                            <li>• $50,000 in claimed damages</li>
                            <li>• Force majeure clause disputed</li>
                          </ul>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">Legal Issues</h4>
                          <div className="space-y-1">
                            <Badge variant="outline" className="text-xs">Breach of Contract</Badge>
                            <Badge variant="outline" className="text-xs">Damages</Badge>
                            <Badge variant="outline" className="text-xs">Force Majeure</Badge>
                          </div>
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">Time Remaining</h4>
                          <div className="flex items-center text-sm text-gray-600">
                            <Clock className="w-4 h-4 mr-1" />
                            32 minutes
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Case Scenarios */}
        {!isSimulationActive && (
          <div className="max-w-6xl mx-auto mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Choose a Case Scenario</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {caseScenarios.map((scenario) => (
                <Card key={scenario.id} className="border-0 shadow-md hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-center justify-between mb-2">
                      <Badge className={getDifficultyColor(scenario.difficulty)}>
                        {scenario.difficulty}
                      </Badge>
                      <div className="flex items-center text-sm text-gray-500">
                        <Clock className="w-4 h-4 mr-1" />
                        {scenario.duration}
                      </div>
                    </div>
                    <CardTitle className="text-lg">{scenario.title}</CardTitle>
                    <CardDescription>{scenario.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="mb-4">
                      <h4 className="font-medium text-gray-900 mb-2">Skills Practiced</h4>
                      <div className="flex flex-wrap gap-1">
                        {scenario.skills.map((skill, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <Button 
                      className="w-full bg-purple-600 hover:bg-purple-700"
                      onClick={() => setIsSimulationActive(true)}
                    >
                      <Play className="w-4 h-4 mr-2" />
                      Start Simulation
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Simulation History */}
        {!isSimulationActive && (
          <div className="max-w-6xl mx-auto mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Recent Simulations</h2>
            <div className="space-y-4">
              {simulationHistory.map((simulation, index) => (
                <Card key={index} className="border-0 shadow-md">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900">{simulation.case}</h3>
                          <Badge variant="outline">{simulation.role}</Badge>
                          <Badge className="bg-green-100 text-green-800">{simulation.outcome}</Badge>
                        </div>
                        <div className="flex items-center space-x-4 text-sm text-gray-600">
                          <span className="flex items-center">
                            <Clock className="w-4 h-4 mr-1" />
                            {simulation.date}
                          </span>
                          <span className="flex items-center">
                            <Award className="w-4 h-4 mr-1" />
                            Score: {simulation.score}/100
                          </span>
                          <span>Duration: {simulation.duration}</span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" size="sm">
                          <FileText className="w-4 h-4 mr-2" />
                          View Report
                        </Button>
                        <Button variant="outline" size="sm">
                          <RotateCcw className="w-4 h-4 mr-2" />
                          Retry
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
            Advanced Court Simulation Features
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => {
              const IconComponent = feature.icon
              return (
                <Card key={index} className="text-center border-0 shadow-md">
                  <CardContent className="p-6">
                    <div className="inline-flex items-center justify-center w-12 h-12 bg-purple-100 rounded-lg mb-4">
                      <IconComponent className="w-6 h-6 text-purple-600" />
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

export default CourtSimulation

