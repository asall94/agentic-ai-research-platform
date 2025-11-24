import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';
import ReflectionWorkflow from './pages/ReflectionWorkflow';
import ToolResearchWorkflow from './pages/ToolResearchWorkflow';
import MultiAgentWorkflow from './pages/MultiAgentWorkflow';

function App() {
  return (
    <Router>
      <div className="min-h-screen flex flex-col bg-gray-50">
        <Header />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/workflows" element={<Navigate to="/" replace />} />
            <Route path="/workflows/reflection" element={<ReflectionWorkflow />} />
            <Route path="/workflows/tool-research" element={<ToolResearchWorkflow />} />
            <Route path="/workflows/multi-agent" element={<MultiAgentWorkflow />} />
            <Route path="/history" element={
              <div className="container mx-auto px-4 py-8">
                <div className="card">
                  <h1 className="text-2xl font-bold mb-4">Workflow History</h1>
                  <p className="text-gray-600">Coming soon... View your past workflow executions here.</p>
                </div>
              </div>
            } />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
