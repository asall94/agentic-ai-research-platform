import React, { useState } from 'react';
import { workflowService } from '../services/api';
import { LoadingSpinner, StatusBadge } from '../components/WorkflowCard';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';

const ReflectionWorkflow = () => {
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const data = await workflowService.executeReflectionWorkflow({ topic });
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
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Simple Reflection Workflow</h1>
      <p className="text-gray-600 mb-8">
        This workflow generates a draft, reflects on it, and produces an improved revision.
      </p>
      
      <div className="card mb-8">
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">
              Research Topic
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Should social media platforms be regulated by the government?"
              className="input-field"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Processing...' : 'Start Reflection Workflow'}
          </button>
        </form>
      </div>
      
      {loading && (
        <div className="card text-center py-12">
          <LoadingSpinner size="lg" />
          <p className="text-gray-600 mt-4">Running reflection workflow...</p>
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
              </div>
            </div>
          </div>
          
          <div className="card">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-800">📝 Initial Draft</h2>
              <button
                onClick={() => downloadResult(result.draft, 'draft.txt')}
                className="text-primary-600 hover:text-primary-700 flex items-center space-x-1"
              >
                <ArrowDownTrayIcon className="h-5 w-5" />
                <span>Download</span>
              </button>
            </div>
            <div className="prose max-w-none">
              <ReactMarkdown>{result.draft}</ReactMarkdown>
            </div>
          </div>
          
          <div className="card bg-blue-50">
            <h2 className="text-xl font-bold text-gray-800 mb-4">🧠 Reflection</h2>
            <div className="prose max-w-none">
              <ReactMarkdown>{result.reflection}</ReactMarkdown>
            </div>
          </div>
          
          <div className="card bg-purple-50">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-800">✍️ Revised Draft</h2>
              <button
                onClick={() => downloadResult(result.revised, 'revised.txt')}
                className="text-primary-600 hover:text-primary-700 flex items-center space-x-1"
              >
                <ArrowDownTrayIcon className="h-5 w-5" />
                <span>Download</span>
              </button>
            </div>
            <div className="prose max-w-none">
              <ReactMarkdown>{result.revised}</ReactMarkdown>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReflectionWorkflow;
