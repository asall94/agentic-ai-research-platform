import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { WorkflowCard } from '../components/WorkflowCard';
import { healthService } from '../services/api';
import { 
  DocumentTextIcon, 
  MagnifyingGlassIcon, 
  UsersIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';

const Home = () => {
  const navigate = useNavigate();
  const [health, setHealth] = useState(null);
  
  useEffect(() => {
    loadHealthStatus();
  }, []);
  
  const loadHealthStatus = async () => {
    try {
      const data = await healthService.checkHealth();
      setHealth(data);
    } catch (error) {
      console.error('Health check failed:', error);
    }
  };
  
  const workflows = [
    {
      id: 'reflection',
      title: 'Simple Reflection',
      description: 'Draft → Critique → Revision workflow for iterative content improvement',
      icon: DocumentTextIcon,
      color: 'primary',
      route: '/workflows/reflection'
    },
    {
      id: 'tool-research',
      title: 'Tool-Enhanced Research',
      description: 'Research with arXiv, Tavily, Wikipedia → Reflect → Export HTML',
      icon: MagnifyingGlassIcon,
      color: 'secondary',
      route: '/workflows/tool-research'
    },
    {
      id: 'multi-agent',
      title: 'Multi-Agent Orchestration',
      description: 'Plan → Research → Write → Edit with specialized agents',
      icon: UsersIcon,
      color: 'accent',
      route: '/workflows/multi-agent'
    }
  ];
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">
          Welcome to the Agentic Research Platform
        </h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Choose a workflow to start your research journey. Powered by advanced AI agents 
          that can reflect, use tools, and collaborate to produce high-quality research content.
        </p>
      </div>
      
      {health && (
        <div className="mb-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <CheckCircleIcon className="h-5 w-5 text-green-600" />
              <span className="font-semibold text-gray-700">System Status: Healthy</span>
            </div>
            <div className="flex space-x-4 text-sm text-gray-600">
              {Object.entries(health.tools_available || {}).map(([tool, available]) => (
                <div key={tool} className="flex items-center space-x-1">
                  {available ? (
                    <CheckCircleIcon className="h-4 w-4 text-green-500" />
                  ) : (
                    <XCircleIcon className="h-4 w-4 text-red-500" />
                  )}
                  <span className="capitalize">{tool}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        {workflows.map((workflow) => (
          <WorkflowCard
            key={workflow.id}
            title={workflow.title}
            description={workflow.description}
            icon={workflow.icon}
            color={workflow.color}
            onClick={() => navigate(workflow.route)}
          />
        ))}
      </div>
      
      <div className="card bg-gradient-to-r from-gray-50 to-gray-100">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Getting Started</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">1</span>
              <h3 className="font-semibold text-gray-800">Choose Workflow</h3>
            </div>
            <p className="text-sm text-gray-600 ml-10">
              Select the workflow that best fits your research needs
            </p>
          </div>
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">2</span>
              <h3 className="font-semibold text-gray-800">Enter Topic</h3>
            </div>
            <p className="text-sm text-gray-600 ml-10">
              Provide your research topic and configure parameters
            </p>
          </div>
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">3</span>
              <h3 className="font-semibold text-gray-800">Get Results</h3>
            </div>
            <p className="text-sm text-gray-600 ml-10">
              Monitor agents in real-time and export your research
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
