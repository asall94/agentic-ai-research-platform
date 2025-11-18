import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';
import ReflectionWorkflow from './pages/ReflectionWorkflow';

function App() {
  return (
    <Router>
      <div className="min-h-screen flex flex-col bg-gray-50">
        <Header />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/workflows/reflection" element={<ReflectionWorkflow />} />
            <Route path="/workflows/tool-research" element={
              <div className="container mx-auto px-4 py-8">
                <div className="card">
                  <h1 className="text-2xl font-bold mb-4">Tool-Enhanced Research</h1>
                  <p className="text-gray-600">Coming soon... This workflow will integrate arXiv, Tavily, and Wikipedia searches.</p>
                </div>
              </div>
            } />
            <Route path="/workflows/multi-agent" element={
              <div className="container mx-auto px-4 py-8">
                <div className="card">
                  <h1 className="text-2xl font-bold mb-4">Multi-Agent Orchestration</h1>
                  <p className="text-gray-600">Coming soon... This workflow will coordinate multiple specialized agents.</p>
                </div>
              </div>
            } />
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
