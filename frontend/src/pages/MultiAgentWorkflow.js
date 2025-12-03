import React, { useState, useEffect, useRef } from 'react';
import { streamWorkflow } from '../services/streamingApi';
import { historyService } from '../services/historyService';
import { LoadingSpinner } from '../components/WorkflowCard';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

const MultiAgentWorkflow = () => {
  const [topic, setTopic] = useState('');
  const [maxSteps, setMaxSteps] = useState(4);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [currentStep, setCurrentStep] = useState(null);
  const [progressMessage, setProgressMessage] = useState('');
  const [executionSteps, setExecutionSteps] = useState([]); // Track dynamic steps
  const [completedSteps, setCompletedSteps] = useState(new Set()); // Track completed step numbers
  const cleanupRef = useRef(null);
  
  // Fixed execution plan based on agent architecture - always visible
  const getExecutionPlan = () => [
    'Research agent: Search for recent papers and articles on ' + (topic || 'the topic') + '.',
    'Research agent: Compile a list of key findings and themes from the search results.',
    'Writer agent: Draft a summary of the key findings and themes on ' + (topic || 'the topic') + '.',
    'Editor agent: Revise the draft summary for clarity and coherence.'
  ].slice(0, maxSteps);
  
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
    setResult({ plan: [], history: [], final_report: '' });
    setCurrentStep(1);
    setProgressMessage('');
    setExecutionSteps([]);
    setCompletedSteps(new Set());
    const startTime = Date.now();
    
    cleanupRef.current = streamWorkflow(
      'multi-agent',
      { topic, max_steps: maxSteps },
      {
        onProgress: (data) => {
          // Track which step is currently executing
          if (data.step && data.step.startsWith('step_')) {
            const stepNum = parseInt(data.step.split('_')[1]);
            console.log('[Multi-Agent] Setting currentStep to:', stepNum);
            setCurrentStep(stepNum);
          } else if (typeof data.step === 'string') {
            console.log('[Multi-Agent] Progress step (non-numeric):', data.step);
          }
          console.log('[Multi-Agent] Progress:', data.message);
          setProgressMessage(data.message);
        },
        onStepComplete: (data) => {
          console.log('[Multi-Agent] Step complete:', data.step, data);
          
          // Track execution steps dynamically
          if (data.step === 'plan') {
            // When plan received, initialize execution steps
            const plan = data.data;
            console.log('[Multi-Agent] Plan received:', plan);
            if (Array.isArray(plan)) {
              const steps = plan.map((step, idx) => ({
                number: idx + 1,
                description: step,
                agent: step.split(':')[0]?.trim() || 'Agent'
              }));
              console.log('[Multi-Agent] Initialized execution steps:', steps);
              setExecutionSteps(steps);
            }
            setResult(prev => ({ ...prev, plan: data.data }));
          } else if (data.step.startsWith('step_')) {
            const stepNum = parseInt(data.step.split('_')[1]);
            console.log('[Multi-Agent] Marking step complete:', stepNum);
            setCompletedSteps(prev => new Set([...prev, stepNum]));
            // Don't clear currentStep here - let onProgress handle it for next step
            
            setResult(prev => ({
              ...prev,
              history: [...(prev.history || []), data.data]
            }));
          } else if (data.step === 'final') {
            setResult(prev => ({
              ...prev,
              plan: data.data.plan,
              history: data.data.history,
              final_report: data.data.final_report
            }));
          }
          setProgressMessage('');
        },
        onComplete: () => {
          const executionTime = Date.now() - startTime;
          historyService.saveExecution('multi-agent', topic, result, executionTime, 'completed');
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
          const cacheResult = {
            plan: data.plan || [],
            history: data.history || [],
            final_report: data.final_report || '',
            cacheHit: true
          };
          setResult(cacheResult);
          const executionTime = Date.now() - startTime;
          historyService.saveExecution('multi-agent', topic, cacheResult, executionTime, 'completed');
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
    setExecutionSteps([]);
    setCompletedSteps(new Set());
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
      
      // Headers
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
      
      // Bold text - properly wrapped
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
    pdf.text('Multi-Agent Workflow - Research Summary', margin, yPosition);
    yPosition += 10;
    
    // Topic
    pdf.setFontSize(12);
    pdf.setFont('helvetica', 'normal');
    pdf.text(`Topic: ${topic}`, margin, yPosition);
    yPosition += 10;
    
    // Final report content with formatting
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    yPosition = addFormattedTextToPDF(pdf, result.final_report || '', pageWidth, margin, yPosition);
    
    // Sources
    if (result.sources && result.sources.length > 0) {
      if (yPosition > 250) {
        pdf.addPage();
        yPosition = margin;
      }
      yPosition += 10;
      pdf.setFontSize(12);
      pdf.setFont('helvetica', 'bold');
      pdf.text('Sources', margin, yPosition);
      yPosition += 7;
      
      pdf.setFontSize(9);
      pdf.setFont('helvetica', 'normal');
      result.sources.forEach((source, index) => {
        if (yPosition > 280) {
          pdf.addPage();
          yPosition = margin;
        }
        const sourceText = `[${index + 1}] ${source.title || source.url}`;
        const sourceLines = pdf.splitTextToSize(sourceText, pageWidth - 2 * margin);
        sourceLines.forEach(line => {
          pdf.text(line, margin, yPosition);
          yPosition += 4;
        });
        yPosition += 2;
      });
    }
    
    pdf.save(`multi-agent-${topic.replace(/\s+/g, '-').toLowerCase()}.pdf`);
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Multi-Agent Orchestration</h1>
      <p className="text-gray-600 mb-8">
        Coordinate specialized agents (Planner, Research, Writer, Editor) to execute complex research workflows dynamically. Watch agents work in real-time.
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
              More steps = deeper analysis but longer execution time (first run ~60-90s, cached &lt;1s)
            </p>
          </div>
          
          <div className="flex space-x-3">
            <button
              type="submit"
              disabled={loading}
              className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Orchestrating Agents...' : 'Start Multi-Agent Workflow'}
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
      
      {error && (
        <div className="card bg-red-50 border-red-200">
          <p className="text-red-700">Error: {error}</p>
        </div>
      )}
      
      {loading && !result && (
        <div className="card">
          {/* Current Progress Message */}
          {progressMessage && (
            <div className="mb-4 p-4 bg-primary-50 border-2 border-primary-500 rounded-lg">
              <div className="flex items-center space-x-3">
                <svg className="animate-spin h-5 w-5 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <p className="text-primary-700 font-semibold">{progressMessage}</p>
              </div>
            </div>
          )}

          {/* Execution Plan Progress */}
          <div className="max-w-2xl mx-auto">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Execution Plan</h3>
            <div className="space-y-3">
              {getExecutionPlan().map((step, idx) => {
                const stepNum = idx + 1;
                const isCompleted = completedSteps.has(stepNum);
                const isCurrent = currentStep === stepNum;
                
                return (
                  <div
                    key={idx}
                    className={`flex items-start space-x-3 p-3 rounded-lg transition-all ${
                      isCurrent
                        ? 'bg-primary-50 border-2 border-primary-500'
                        : isCompleted
                        ? 'bg-green-50 border-2 border-green-500'
                        : 'bg-gray-50 border-2 border-gray-200'
                    }`}
                  >
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold flex-shrink-0 ${
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
                      ) : isCompleted ? '✓' : stepNum}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-medium ${
                        isCurrent ? 'text-primary-700' : isCompleted ? 'text-green-700' : 'text-gray-600'
                      }`}>
                        {step}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
      
      {progressMessage && result && (
        <div className={`card mb-6 ${progressMessage.includes('Cache hit') ? 'bg-green-50 border-green-200' : 'bg-blue-50 border-blue-200'}`}>
          <div className="flex items-center space-x-3">
            {!progressMessage.includes('Cache hit') && <LoadingSpinner size="sm" />}
            <p className={`font-medium ${progressMessage.includes('Cache hit') ? 'text-green-700' : 'text-blue-700'}`}>{progressMessage}</p>
          </div>
        </div>
      )}
      
      {/* Fixed Execution Plan - always visible */}
      <div className="card bg-yellow-50">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Execution Plan</h2>
        <ol className="list-decimal list-inside space-y-2">
          {getExecutionPlan().map((step, index) => (
            <li key={index} className="text-gray-700">
              {step}
            </li>
          ))}
        </ol>
      </div>
      
      {/* Final Output Only - Industry Standard (like Perplexity/Claude) */}
      {result && result.final_report && (
        <div className="space-y-6">
          <div className="card">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-800">Research Summary</h2>
              <button
                onClick={downloadPDF}
                className="text-primary-600 hover:text-primary-700 flex items-center space-x-2 font-medium"
              >
                <ArrowDownTrayIcon className="h-5 w-5" />
                <span>Download PDF</span>
              </button>
            </div>
            <div className="prose max-w-none">
              <ReactMarkdown>{result.final_report}</ReactMarkdown>
            </div>
          </div>
          
          {/* Sources Section - Industry Standard */}
          {result.sources && result.sources.length > 0 && (
            <div className="card bg-gray-50">
              <h3 className="text-lg font-bold text-gray-800 mb-4">Sources</h3>
              <div className="space-y-3">
                {result.sources.map((source, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-white rounded border border-gray-200">
                    <span className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-xs font-bold">
                      {index + 1}
                    </span>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{source.title || source.name}</p>
                      {source.url && (
                        <a 
                          href={source.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-xs text-primary-600 hover:text-primary-700 underline"
                        >
                          {source.url}
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MultiAgentWorkflow;
