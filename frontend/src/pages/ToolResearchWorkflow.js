import React, { useState, useEffect, useRef } from 'react';
import { streamWorkflow } from '../services/streamingApi';
import { historyService } from '../services/historyService';
import { LoadingSpinner, StatusBadge } from '../components/WorkflowCard';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

const ToolResearchWorkflow = () => {
  const [topic, setTopic] = useState('');
  const [selectedTools, setSelectedTools] = useState(['arxiv', 'wikipedia', 'tavily']);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [currentStep, setCurrentStep] = useState(null);
  const [progressMessage, setProgressMessage] = useState('');
  const [progressSteps, setProgressSteps] = useState({});
  const [executionTime, setExecutionTime] = useState(0);
  const cleanupRef = useRef(null);
  
  const availableTools = [
    { id: 'arxiv', name: 'arXiv', description: 'Academic papers and research' },
    { id: 'wikipedia', name: 'Wikipedia', description: 'Encyclopedia knowledge' },
    { id: 'tavily', name: 'Tavily', description: 'Web search' }
  ];
  
  // Save to history when result is set and loading is complete
  useEffect(() => {
    if (result && !loading && executionTime > 0) {
      historyService.saveExecution('tool-research', topic, result, executionTime, 'completed');
    }
  }, [result, loading, executionTime, topic]);
  
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
    const startTime = Date.now();
    
    cleanupRef.current = streamWorkflow(
      'tool-research',
      { topic, tools: selectedTools.join(',') },
      {
        onProgress: (data) => {
          console.log('[Tool Research] Setting currentStep to:', data.step);
          setCurrentStep(data.step);
          setProgressMessage(data.message);
          console.log(`[Tool Research] ${data.step}: ${data.message}`);
        },
        onStepComplete: (data) => {
          console.log('[Tool Research] Step complete:', data.step, data.data);
          
          // Update progress steps with checkmark
          setProgressSteps(prev => ({
            ...prev,
            [data.step]: 'completed'
          }));
          
          // Don't clear currentStep here - let onProgress handle it for next step
          
          // Capture final result with all steps
          if (data.step === 'final') {
            console.log('[Tool Research] Setting final result:', data.data);
            setResult(data.data);
          }
          setProgressMessage('');
        },
        onComplete: () => {
          const execTime = Date.now() - startTime;
          setExecutionTime(execTime);
          setLoading(false);
          setCurrentStep(null);
          setProgressMessage('');
          console.log('[Tool Research] Workflow complete');
        },
        onError: (errorMsg) => {
          setError(errorMsg);
          setLoading(false);
          setCurrentStep(null);
          setProgressMessage('');
        },
        onCacheHit: (data) => {
          const cacheResult = { ...data, cacheHit: true };
          setResult(cacheResult);
          const execTime = Date.now() - startTime;
          setExecutionTime(execTime);
          setLoading(false);
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
        yPosition += 5; // Space before header
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
        yPosition += 3; // Space after header
        pdf.setFontSize(10);
        pdf.setFont('helvetica', 'normal');
        return;
      }
      
      // Bold text (**text**) - properly wrapped
      const boldRegex = /\*\*(.+?)\*\*/g;
      if (boldRegex.test(line)) {
        // Split line into segments (normal and bold)
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
              // Save current line and start new one
              wrappedLines.push([...currentLineParts]);
              currentLineParts = [{ text: wordWithSpace.trimEnd(), bold: segment.bold }];
              currentWidth = pdf.getTextWidth(word);
            } else {
              currentLineParts.push({ text: wordWithSpace.trimEnd(), bold: segment.bold });
              currentWidth += wordWidth;
            }
          });
        });
        
        // Add remaining parts
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
        // Regular line without formatting
        const cleanLine = line
          .replace(/^[-*+]\s/, '• ') // Bullet points
          .replace(/\[(.+?)\]\(.+?\)/g, '$1') // Links
          .replace(/`(.+?)`/g, '$1'); // Inline code
        
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
          yPosition += 6; // Increased empty line spacing between paragraphs
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
    pdf.text('Tool Research Workflow - Research Summary', margin, yPosition);
    yPosition += 10;
    
    // Topic
    pdf.setFontSize(12);
    pdf.setFont('helvetica', 'normal');
    pdf.text(`Topic: ${topic}`, margin, yPosition);
    yPosition += 10;
    
    // Research content with formatting
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    const content = result.revised_report || result.research_report || '';
    yPosition = addFormattedTextToPDF(pdf, content, pageWidth, margin, yPosition);
    
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
    
    pdf.save(`research-${topic.replace(/\s+/g, '-').toLowerCase()}.pdf`);
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Tool-Enhanced Research</h1>
      <p className="text-gray-600 mb-8">
        Search across arXiv, Wikipedia, and Tavily to synthesize comprehensive research reports. Results stream in real-time.
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
          
          <div className="flex space-x-3">
            <button
              type="submit"
              disabled={loading || selectedTools.length === 0}
              className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Researching...' : 'Start Research'}
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
          
          {/* Progress Steps Visualization */}
          <div className="max-w-2xl mx-auto">
            <div className="space-y-3">
              {['research', 'reflection', 'revised', 'formatting'].map((step, idx) => {
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
      
      {result && (
        <div className="space-y-6">
          {/* Main Research Output - Industry Standard */}
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
              <ReactMarkdown>{result.revised_report || result.research_report}</ReactMarkdown>
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
                          className="text-xs text-primary-600 hover:text-primary-700 underline break-all"
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
          
          {/* Execution Stats */}
          {result.execution_time && (
            <div className="card bg-green-50 border-green-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">
                    ⏱️ Execution time: <span className="font-semibold">{result.execution_time?.toFixed(2)}s</span>
                  </p>
                  {result.cacheHit && (
                    <p className="text-sm text-green-600 mt-1">Cache hit - instant result</p>
                  )}
                </div>
                {result.sources && (
                  <p className="text-sm text-gray-600">
                    <span className="font-semibold">{result.sources.length}</span> sources referenced
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ToolResearchWorkflow;
