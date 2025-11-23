import React, { useState, useEffect, useRef } from 'react';
import { streamWorkflow } from '../services/streamingApi';
import { LoadingSpinner, StatusBadge } from '../components/WorkflowCard';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';

const ToolResearchWorkflow = () => {
  const [topic, setTopic] = useState('');
  const [selectedTools, setSelectedTools] = useState(['arxiv', 'wikipedia', 'tavily']);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [currentStep, setCurrentStep] = useState(null);
  const [progressMessage, setProgressMessage] = useState('');
  const cleanupRef = useRef(null);
  
  const availableTools = [
    { id: 'arxiv', name: 'arXiv', description: 'Academic papers and research' },
    { id: 'wikipedia', name: 'Wikipedia', description: 'Encyclopedia knowledge' },
    { id: 'tavily', name: 'Tavily', description: 'Web search' }
  ];
  
  useEffect(() => {
    return () => {
      if (cleanupRef.current) {
        cleanupRef.current();
      }
    };
  }, []);
  
  const handleToolToggle = (toolId) => {
    setSelectedTools(prev =>
      prev.includes(toolId)
        ? prev.filter(t => t !== toolId)
        : [...prev, toolId]
    );
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (selectedTools.length === 0) {
      setError('Please select at least one research tool');
      return;
    }
    
    setLoading(true);
    setError(null);
    setResult({});
    setCurrentStep('research');
    setProgressMessage('');
    
    cleanupRef.current = streamWorkflow(
      'tool-research',
      { topic, tools: selectedTools.join(',') },
      {
        onProgress: (data) => {
          setCurrentStep(data.step);
          setProgressMessage(data.message);
        },
        onStepComplete: (data) => {
          if (data.step === 'research') {
            setResult(data.data);
          }
          setProgressMessage('');
        },
        onComplete: () => {
          setLoading(false);
          setCurrentStep(null);
          setProgressMessage('');
        },
        onError: (errorMsg) => {
          setError(errorMsg);
          setLoading(false);
          setCurrentStep(null);
          setProgressMessage('');
        }
      }
    );
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
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Tool-Enhanced Research</h1>
      <p className="text-gray-600 mb-8">
        Search across arXiv, Wikipedia, and Tavily to synthesize comprehensive research reports.
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
              placeholder="e.g., Quantum computing applications in cryptography"
              className="input-field"
              required
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 font-semibold mb-3">
              Select Research Tools
            </label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {availableTools.map(tool => (
                <div
                  key={tool.id}
                  onClick={() => handleToolToggle(tool.id)}
                  className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    selectedTools.includes(tool.id)
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center space-x-2 mb-1">
                    <input
                      type="checkbox"
                      checked={selectedTools.includes(tool.id)}
                      onChange={() => {}}
                      className="h-4 w-4 text-primary-600"
                    />
                    <span className="font-semibold text-gray-800">{tool.name}</span>
                  </div>
                  <p className="text-sm text-gray-600 ml-6">{tool.description}</p>
                </div>
              ))}
            </div>
          </div>
          
          <button
            type="submit"
            disabled={loading || selectedTools.length === 0}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Researching...' : 'Start Research'}
          </button>
        </form>
      </div>
      
      {loading && (
        <div className="card text-center py-12">
          <LoadingSpinner size="lg" />
          <p className="text-gray-600 mt-4">Searching across selected sources...</p>
          <p className="text-sm text-gray-500 mt-2">This may take 30-60 seconds</p>
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
                {result.sources_count && (
                  <p className="text-sm text-gray-600">
                    Sources found: {result.sources_count}
                  </p>
                )}
              </div>
            </div>
          </div>
          
          {result.research_results && (
            <div className="card">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold text-gray-800">📚 Research Results</h2>
                <button
                  onClick={() => downloadResult(result.research_results, 'research.txt')}
                  className="text-primary-600 hover:text-primary-700 flex items-center space-x-1"
                >
                  <ArrowDownTrayIcon className="h-5 w-5" />
                  <span>Download</span>
                </button>
              </div>
              <div className="prose max-w-none">
                <ReactMarkdown>{result.research_results}</ReactMarkdown>
              </div>
            </div>
          )}
          
          {result.synthesis && (
            <div className="card bg-blue-50">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold text-gray-800">🔍 Synthesis</h2>
                <button
                  onClick={() => downloadResult(result.synthesis, 'synthesis.txt')}
                  className="text-primary-600 hover:text-primary-700 flex items-center space-x-1"
                >
                  <ArrowDownTrayIcon className="h-5 w-5" />
                  <span>Download</span>
                </button>
              </div>
              <div className="prose max-w-none">
                <ReactMarkdown>{result.synthesis}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ToolResearchWorkflow;
