import React, { useState, useEffect, useRef } from 'react';
import { streamWorkflow } from '../services/streamingApi';
import { LoadingSpinner, StatusBadge } from '../components/WorkflowCard';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';

const ReflectionWorkflow = () => {
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [currentStep, setCurrentStep] = useState(null);
  const [progressMessage, setProgressMessage] = useState('');
  const cleanupRef = useRef(null);
  
  useEffect(() => {
    return () => {
      if (cleanupRef.current) {
        cleanupRef.current();
      }
    };
  }, []);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult({ draft: '', reflection: '', revised: '' });
    setCurrentStep('draft');
    setProgressMessage('');
    
    cleanupRef.current = streamWorkflow(
      'reflection',
      { topic },
      {
        onProgress: (data) => {
          setCurrentStep(data.step);
          setProgressMessage(data.message);
        },
        onStepComplete: (data) => {
          setResult(prev => ({
            ...prev,
            [data.step]: data.data
          }));
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
      
      {error && (
        <div className="card bg-red-50 border-red-200">
          <p className="text-red-700">Error: {error}</p>
        </div>
      )}
      
      {result && (
        <div className="space-y-6">
          <div className="card">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-800">📝 Initial Draft</h2>
              {result.draft && (
                <button
                  onClick={() => downloadResult(result.draft, 'draft.txt')}
                  className="text-primary-600 hover:text-primary-700 flex items-center space-x-1"
                >
                  <ArrowDownTrayIcon className="h-5 w-5" />
                  <span>Download</span>
                </button>
              )}
            </div>
            {currentStep === 'draft' && progressMessage && (
              <div className="flex items-center space-x-3 p-4 bg-blue-50 rounded-lg mb-4">
                <LoadingSpinner size="sm" />
                <p className="text-blue-700">{progressMessage}</p>
              </div>
            )}
            {result.draft ? (
              <div className="prose max-w-none">
                <ReactMarkdown>{result.draft}</ReactMarkdown>
              </div>
            ) : (
              <p className="text-gray-400">Waiting for draft...</p>
            )}
          </div>
          
          {result.draft && (
            <div className="card bg-blue-50">
              <h2 className="text-xl font-bold text-gray-800 mb-4">🧠 Reflection</h2>
              {currentStep === 'reflection' && progressMessage && (
                <div className="flex items-center space-x-3 p-4 bg-blue-100 rounded-lg mb-4">
                  <LoadingSpinner size="sm" />
                  <p className="text-blue-700">{progressMessage}</p>
                </div>
              )}
              {result.reflection ? (
                <div className="prose max-w-none">
                  <ReactMarkdown>{result.reflection}</ReactMarkdown>
                </div>
              ) : currentStep === 'reflection' || currentStep === 'revision' ? (
                <p className="text-gray-400">Analyzing draft...</p>
              ) : null}
            </div>
          )}
          
          {result.reflection && (
            <div className="card bg-purple-50">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold text-gray-800">✍️ Revised Draft</h2>
                {result.revised && (
                  <button
                    onClick={() => downloadResult(result.revised, 'revised.txt')}
                    className="text-primary-600 hover:text-primary-700 flex items-center space-x-1"
                  >
                    <ArrowDownTrayIcon className="h-5 w-5" />
                    <span>Download</span>
                  </button>
                )}
              </div>
              {currentStep === 'revision' && progressMessage && (
                <div className="flex items-center space-x-3 p-4 bg-purple-100 rounded-lg mb-4">
                  <LoadingSpinner size="sm" />
                  <p className="text-purple-700">{progressMessage}</p>
                </div>
              )}
              {result.revised ? (
                <div className="prose max-w-none">
                  <ReactMarkdown>{result.revised}</ReactMarkdown>
                </div>
              ) : currentStep === 'revision' ? (
                <p className="text-gray-400">Revising based on feedback...</p>
              ) : null}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ReflectionWorkflow;
