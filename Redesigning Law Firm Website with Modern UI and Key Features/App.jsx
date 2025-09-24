import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Home from './pages/Home.jsx'
import LegalResearch from './pages/LegalResearch.jsx'
import DocumentAnalysis from './pages/DocumentAnalysis.jsx'
import CourtSimulation from './pages/CourtSimulation.jsx'
import DatabaseIntelligence from './pages/DatabaseIntelligence.jsx'
import WebScraping from './pages/WebScraping.jsx'
import Analytics from './pages/Analytics.jsx'
import ContractManagement from './pages/ContractManagement.jsx'
import ContractDrafting from './pages/ContractDrafting.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/contract-drafting" element={<ContractDrafting />} />
        <Route path="/*" element={
          <Layout>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/research" element={<LegalResearch />} />
              <Route path="/documents" element={<DocumentAnalysis />} />
              <Route path="/court" element={<CourtSimulation />} />
              <Route path="/database" element={<DatabaseIntelligence />} />
              <Route path="/scraping" element={<WebScraping />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/contracts" element={<ContractManagement />} />
            </Routes>
          </Layout>
        } />
      </Routes>
    </Router>
  )
}

export default App

