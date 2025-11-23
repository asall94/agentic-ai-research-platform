import React, { useState } from 'react';
import { workflowService } from '../services/api';
import { LoadingSpinner, StatusBadge } from '../components/WorkflowCard';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';

const MultiAgentWorkflow = () => {
  const [topic, setTopic] = useState('');
  const [maxSteps, setMaxSteps] = useState(4);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const data = await workflowService.executeMultiAgentWorkflow({
        topic,
        max_steps: maxSteps
      });
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  const downloadResult = (content, filename) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Multi-Agent Orchestration</h1>
      <p className="text-gray-600 mb-8">
        Coordinate specialized agents (Planner, Research, Writer, Editor) to execute complex research workflows dynamically.
      </p>
      
      <div className="card mb-8">
        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label className="block text-gray-700 font-semibold mb-2">
              Research Topic
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Impact of climate change on global food security"
              className="input-field"
              required
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 font-semibold mb-2">
              Maximum Steps: {maxSteps}
            </label>
            <input
              type="range"
              min="2"
              max="6"
              value={maxSteps}
              onChange={(e) => setMaxSteps(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>2 steps</span>
              <span>4 steps (recommended)</span>
              <span>6 steps</span>
            </div>
            <p className="text-sm text-gray-600 mt-2">
              More steps = deeper analysis but longer execution time
            </p>
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Orchestrating Agents...' : 'Start Multi-Agent Workflow'}
          </button>
        </form>
      </div>
      
      {loading && (
        <div className="card text-center py-12">
          <LoadingSpinner size="lg" />
          <p className="text-gray-600 mt-4">Coordinating specialized agents...</p>
          <p className="text-sm text-gray-500 mt-2">This may take 60-90 seconds</p>
        </div>
      )}
      
      {error && (
        <div className="card bg-red-50 border-red-200">
          <p className="text-red-700">Error: {error}</p>
        </div>
      )}
      
      {result && (
        <div className="space-y-6">
          <div className="card bg-green-50 border-green-200">
            <div className="flex justify-between items-center">
              <div>
                <StatusBadge status={result.status} />
                <p className="text-sm text-gray-600 mt-2">
                  Execution time: {result.execution_time?.toFixed(2)}s
                </p>
                {result.steps_executed && (
                  <p className="text-sm text-gray-600">
                    Steps executed: {result.steps_executed}
                  </p>
                )}
              </div>
            </div>
          </div>
          
          {result.plan && result.plan.length > 0 && (
            <div className="card bg-yellow-50">
              <h2 className="text-xl font-bold text-gray-800 mb-4">📋 Execution Plan</h2>
              <ol className="list-decimal list-inside space-y-2">
                {result.plan.map((step, index) => (
                  <li key={index} className="text-gray-700">
                    {step}
                  </li>
                ))}
              </ol>
            </div>
          )}
          
          {result.history && result.history.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-gray-800">🔄 Agent Execution History</h2>
              {result.history.map((step, index) => (
                <div key={index} className="card bg-gray-50">
                  <div className="flex items-center space-x-2 mb-3">
                    <span className="px-2 py-1 bg-primary-100 text-primary-700 text-xs font-semibold rounded">
                      Step {step.step}
                    </span>
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded">
                      {step.agent}
                    </span>
                  </div>
                  <div className="prose max-w-none text-sm">
                    <ReactMarkdown>{step.output}</ReactMarkdown>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {result.final_output && (
            <div className="card bg-purple-50">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold text-gray-800">✨ Final Output</h2>
                <button
                  onClick={() => downloadResult(result.final_output, 'final_output.txt')}
                  className="text-primary-600 hover:text-primary-700 flex items-center space-x-1"
                >
                  <ArrowDownTrayIcon className="h-5 w-5" />
                  <span>Download</span>
                </button>
              </div>
              <div className="prose max-w-none">
                <ReactMarkdown>{result.final_output}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MultiAgentWorkflow;
