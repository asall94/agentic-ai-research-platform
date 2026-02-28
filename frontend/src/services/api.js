import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // 5 minutes
});

export const workflowService = {
  // Tool Research Workflow
  executeToolResearchWorkflow: async (data) => {
    const response = await apiClient.post('/workflows/tool-research', data);
    return response.data;
  },

  // Multi-Agent Workflow (Q5)
  executeMultiAgentWorkflow: async (data) => {
    const response = await apiClient.post('/workflows/multi-agent', data);
    return response.data;
  },
};

export const healthService = {
  checkHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};

export default apiClient;
