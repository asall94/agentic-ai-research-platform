import React, { useState, useEffect, useRef } from 'react';
import { streamWorkflow } from '../services/streamingApi';
import { historyService } from '../services/historyService';
import { LoadingSpinner } from '../components/WorkflowCard';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

const ReflectionWorkflow = () => {
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState({});
  const [error, setError] = useState(null);
  const [currentStep, setCurrentStep] = useState(null);
  const [progressMessage, setProgressMessage] = useState('');
  const [progressSteps, setProgressSteps] = useState({});
  const [executionTime, setExecutionTime] = useState(0);
  const cleanupRef = useRef(null);
  
  // Save to history when result is complete
  useEffect(() => {
    if (result && result.revised && !loading && executionTime > 0) {
      historyService.saveExecution('reflection', topic, result, executionTime, 'completed');
    }
  }, [result, loading, executionTime, topic]);
  
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
    const startTime = Date.now();
    
    cleanupRef.current = streamWorkflow(
      'reflection',
      { topic },
      {
        onProgress: (data) => {
          setCurrentStep(data.step);
          setProgressMessage(data.message);
        },
        onStepComplete: (data) => {
          // Update progress steps with checkmark
          setProgressSteps(prev => ({
            ...prev,
            [data.step]: 'completed'
          }));
          
          // Clear current step to remove spinner
          setCurrentStep(null);
          
          setResult(prev => ({
            ...prev,
            [data.step]: data.data
          }));
          setProgressMessage('');
        },
        onComplete: () => {
          const execTime = Date.now() - startTime;
          setExecutionTime(execTime);
          setLoading(false);
          setCurrentStep(null);
          setProgressMessage('');
        },
        onError: (errorMsg) => {
          setError(errorMsg);
          setLoading(false);
          setCurrentStep(null);
          setProgressMessage('');
        },
        onCacheHit: (data) => {
          // Cache hit - populate all fields immediately
          const cacheResult = {
            draft: data.draft,
            reflection: data.reflection,
            revised: data.revised,
            cacheHit: true
          };
          setResult(cacheResult);
          const execTime = Date.now() - startTime;
          setExecutionTime(execTime);
          setLoading(false);
          setCurrentStep(null);
          setProgressMessage('Cache hit - instant results!');
          setTimeout(() => setProgressMessage(''), 3000);
        }
      }
    );
  };
  
  const handleCancel = () => {
    if (cleanupRef.current) {
      cleanupRef.current();
    }
    setLoading(false);
    setCurrentStep(null);
    setProgressMessage('');
    setError('Workflow stopped by user');
  };
  
  const downloadResult = (content, filename) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
  };
  
  // Convert markdown to formatted PDF with bold and headers
  const addFormattedTextToPDF = (pdf, markdown, pageWidth, margin, startY) => {
    let yPosition = startY;
    const lines = markdown.split('\n');
    
    lines.forEach(line => {
      if (yPosition > 280) {
        pdf.addPage();
        yPosition = margin;
      }
      
      // Headers (### Title)
      if (line.match(/^#{1,3}\s/)) {
        yPosition += 5;
        const headerText = line.replace(/^#{1,3}\s/, '').replace(/\*\*/g, '');
        pdf.setFontSize(12);
        pdf.setFont('helvetica', 'bold');
        const headerLines = pdf.splitTextToSize(headerText, pageWidth - 2 * margin);
        headerLines.forEach(headerLine => {
          if (yPosition > 280) {
            pdf.addPage();
            yPosition = margin;
          }
          pdf.text(headerLine, margin, yPosition);
          yPosition += 7;
        });
        yPosition += 3;
        pdf.setFontSize(10);
        pdf.setFont('helvetica', 'normal');
        return;
      }
      
      // Bold text (**text**) - properly wrapped
      const boldRegex = /\*\*(.+?)\*\*/g;
      if (boldRegex.test(line)) {
        const segments = [];
        let lastIndex = 0;
        const matches = [...line.matchAll(/\*\*(.+?)\*\*/g)];
        
        matches.forEach(match => {
          if (match.index > lastIndex) {
            segments.push({ text: line.substring(lastIndex, match.index), bold: false });
          }
          segments.push({ text: match[1], bold: true });
          lastIndex = match.index + match[0].length;
        });
        
        if (lastIndex < line.length) {
          segments.push({ text: line.substring(lastIndex), bold: false });
        }
        
        // Build lines with bold tracking
        const wrappedLines = [];
        let currentLineParts = [];
        let currentWidth = 0;
        const maxWidth = pageWidth - 2 * margin;
        
        segments.forEach(segment => {
          const words = segment.text.split(' ');
          
          words.forEach((word, wordIdx) => {
            const wordWithSpace = word + ' ';
            pdf.setFont('helvetica', segment.bold ? 'bold' : 'normal');
            const wordWidth = pdf.getTextWidth(wordWithSpace);
            
            if (currentWidth + wordWidth > maxWidth && currentLineParts.length > 0) {
              wrappedLines.push([...currentLineParts]);
              currentLineParts = [{ text: wordWithSpace.trimEnd(), bold: segment.bold }];
              currentWidth = pdf.getTextWidth(word);
            } else {
              currentLineParts.push({ text: wordWithSpace.trimEnd(), bold: segment.bold });
              currentWidth += wordWidth;
            }
          });
        });
        
        if (currentLineParts.length > 0) {
          wrappedLines.push(currentLineParts);
        }
        
        // Render all wrapped lines
        wrappedLines.forEach(lineParts => {
          if (yPosition > 280) {
            pdf.addPage();
            yPosition = margin;
          }
          
          let xPos = margin;
          lineParts.forEach(part => {
            pdf.setFont('helvetica', part.bold ? 'bold' : 'normal');
            pdf.text(part.text, xPos, yPosition);
            xPos += pdf.getTextWidth(part.text) + (part.text.endsWith(' ') ? 0 : pdf.getTextWidth(' '));
          });
          yPosition += 5;
        });
      } else {
        const cleanLine = line
          .replace(/^[-*+]\s/, '• ')
          .replace(/\[(.+?)\]\(.+?\)/g, '$1')
          .replace(/`(.+?)`/g, '$1');
        
        if (cleanLine.trim()) {
          const textLines = pdf.splitTextToSize(cleanLine, pageWidth - 2 * margin);
          textLines.forEach(textLine => {
            if (yPosition > 280) {
              pdf.addPage();
              yPosition = margin;
            }
            pdf.text(textLine, margin, yPosition);
            yPosition += 5;
          });
        } else {
          yPosition += 6;
        }
      }
    });
    
    return yPosition;
  };
  
  const downloadPDF = async () => {
    const pdf = new jsPDF('p', 'mm', 'a4');
    const pageWidth = pdf.internal.pageSize.getWidth();
    const margin = 15;
    let yPosition = margin;
    
    // Title
    pdf.setFontSize(16);
    pdf.setFont('helvetica', 'bold');
    pdf.text('Reflection Workflow - Final Draft', margin, yPosition);
    yPosition += 10;
    
    // Topic
    pdf.setFontSize(12);
    pdf.setFont('helvetica', 'normal');
    pdf.text(`Topic: ${topic}`, margin, yPosition);
    yPosition += 10;
    
    // Final draft content with formatting
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    yPosition = addFormattedTextToPDF(pdf, result.revised || '', pageWidth, margin, yPosition);
    
    pdf.save(`reflection-${topic.replace(/\s+/g, '-').toLowerCase()}.pdf`);
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Simple Reflection Workflow</h1>
      <p className="text-gray-600 mb-8">
        This workflow generates a draft, reflects on it, and produces an improved revision. Results stream in real-time as each step completes.
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
          
          <div className="flex space-x-3">
            <button
              type="submit"
              disabled={loading}
              className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Processing...' : 'Start Reflection Workflow'}
            </button>
            
            {loading && (
              <button
                type="button"
                onClick={handleCancel}
                className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium transition-colors"
              >
                Stop
              </button>
            )}
          </div>
        </form>
      </div>
      
      {loading && (
        <div className="card">
          {/* Progress Steps Visualization */}
          <div className="max-w-2xl mx-auto">
            <div className="space-y-3">
              {['draft', 'reflection', 'revised'].map((step, idx) => {
                const isCompleted = progressSteps[step] === 'completed';
                const isCurrent = currentStep === step;
                
                return (
                  <div
                    key={step}
                    className={`flex items-center space-x-3 p-3 rounded-lg transition-all ${
                      isCurrent
                        ? 'bg-primary-50 border-2 border-primary-500'
                        : isCompleted
                        ? 'bg-green-50 border-2 border-green-500'
                        : 'bg-gray-50 border-2 border-gray-200'
                    }`}
                  >
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                      isCurrent
                        ? 'bg-primary-500 text-white'
                        : isCompleted
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-300 text-gray-600'
                    }`}>
                      {isCurrent ? (
                        <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                      ) : isCompleted ? '✓' : idx + 1}
                    </div>
                    <div className="flex-1">
                      <p className={`font-semibold ${
                        isCurrent ? 'text-primary-700' : isCompleted ? 'text-green-700' : 'text-gray-700'
                      }`}>
                        {step === 'revised' ? 'Revised' : step.charAt(0).toUpperCase() + step.slice(1)}
                      </p>
                      {isCurrent && progressMessage && (
                        <p className="text-sm text-primary-600 mt-1">{progressMessage}</p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
      
      {error && (
        <div className="card bg-red-50 border-red-200">
          <p className="text-red-700">Error: {error}</p>
        </div>
      )}
      
      {/* Final Output - Industry Standard (only when complete) */}
      {result && result.revised && (
        <div className="space-y-6">
          <div className="card">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-800">Final Draft</h2>
              <button
                onClick={downloadPDF}
                className="text-primary-600 hover:text-primary-700 flex items-center space-x-2 font-medium"
              >
                <ArrowDownTrayIcon className="h-5 w-5" />
                <span>Download PDF</span>
              </button>
            </div>
            <div className="prose max-w-none">
              <ReactMarkdown>{result.revised}</ReactMarkdown>
            </div>
          </div>
          
          {/* Collapsible Edit Notes - Industry Standard for transparency */}
          {result.reflection && (
            <details className="card bg-gray-50">
              <summary className="cursor-pointer font-semibold text-gray-700 hover:text-gray-900">
                View Edit Notes & Critique
              </summary>
              <div className="mt-4 prose max-w-none text-sm text-gray-600 border-t pt-4">
                <ReactMarkdown>{result.reflection}</ReactMarkdown>
              </div>
            </details>
          )}
          
          {/* Execution Stats */}
          {executionTime > 0 && (
            <div className="card bg-green-50 border-green-200">
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-600">
                  ⏱️ Execution time: <span className="font-semibold">{(executionTime / 1000).toFixed(2)}s</span>
                </p>
                {result.cacheHit && (
                  <p className="text-sm text-green-600">Cache hit - instant result</p>
                )}
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Progress Display During Execution */}
      {result && !result.revised && (
        <div className="space-y-6">
          <div className="card">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-800">Initial Draft</h2>
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
              ) : currentStep === 'reflection' || currentStep === 'revised' ? (
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
              {currentStep === 'revised' && progressMessage && (
                <div className="flex items-center space-x-3 p-4 bg-purple-100 rounded-lg mb-4">
                  <LoadingSpinner size="sm" />
                  <p className="text-purple-700">{progressMessage}</p>
                </div>
              )}
              {result.revised ? (
                <div className="prose max-w-none">
                  <ReactMarkdown>{result.revised}</ReactMarkdown>
                </div>
              ) : currentStep === 'revised' ? (
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
