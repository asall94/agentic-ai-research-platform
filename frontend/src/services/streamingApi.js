const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

/**
 * Stream workflow execution with SSE
 * @param {string} workflowType - 'reflection', 'tool-research', or 'multi-agent'
 * @param {object} params - Query parameters (topic, model, tools, etc.)
 * @param {object} callbacks - Event callbacks: onProgress, onStepComplete, onComplete, onError
 */
export function streamWorkflow(workflowType, params, callbacks) {
  const queryParams = new URLSearchParams(params).toString();
  const url = `${API_URL}/workflows/${workflowType}/stream?${queryParams}`;
  
  const eventSource = new EventSource(url);
  
  eventSource.onopen = () => {
    console.log(`[SSE] Connected to ${workflowType} stream`);
  };
  
  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'start':
          console.log('[SSE] Workflow started:', data);
          break;
          
        case 'progress':
          if (callbacks.onProgress) {
            callbacks.onProgress(data);
          }
          break;
          
        case 'step_complete':
          if (callbacks.onStepComplete) {
            callbacks.onStepComplete(data);
          }
          break;
          
        case 'complete':
          console.log('[SSE] Workflow completed');
          if (callbacks.onComplete) {
            callbacks.onComplete();
          }
          eventSource.close();
          break;
          
        case 'error':
          console.error('[SSE] Workflow error:', data.message);
          if (callbacks.onError) {
            callbacks.onError(data.message);
          }
          eventSource.close();
          break;
          
        default:
          console.warn('[SSE] Unknown event type:', data.type);
      }
    } catch (error) {
      console.error('[SSE] Failed to parse event data:', error, event.data);
    }
  };
  
  eventSource.onerror = (error) => {
    console.error('[SSE] Connection error:', error);
    if (callbacks.onError) {
      callbacks.onError('Stream connection failed. Please try again.');
    }
    eventSource.close();
  };
  
  // Return cleanup function
  return () => {
    console.log('[SSE] Closing connection');
    eventSource.close();
  };
}
