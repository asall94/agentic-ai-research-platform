import React, { useState, useEffect, useCallback } from 'react';
import { historyService } from '../services/historyService';
import { 
  ClockIcon, 
  TrashIcon, 
  ArrowDownTrayIcon,
  FunnelIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon as PendingIcon,
  MagnifyingGlassIcon,
  DocumentTextIcon,
  UsersIcon,
  BoltIcon
} from '@heroicons/react/24/outline';

const History = () => {
  const [history, setHistory] = useState([]);
  const [filteredHistory, setFilteredHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedWorkflow, setSelectedWorkflow] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedItem, setExpandedItem] = useState(null);

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [history, selectedWorkflow, selectedStatus, searchTerm]);

  const loadHistory = () => {
    const data = historyService.getHistory();
    setHistory(data);
    setStats(historyService.getStats());
  };

  const applyFilters = useCallback(() => {
    let filtered = [...history];

    if (selectedWorkflow !== 'all') {
      filtered = filtered.filter(item => item.workflowType === selectedWorkflow);
    }

    if (selectedStatus !== 'all') {
      filtered = filtered.filter(item => item.status === selectedStatus);
    }

    if (searchTerm) {
      filtered = filtered.filter(item => 
        item.topic.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredHistory(filtered);
  }, [history, selectedWorkflow, selectedStatus, searchTerm]);

  const handleDelete = (id, event) => {
    event.stopPropagation();
    if (window.confirm('Delete this execution from history?')) {
      historyService.deleteById(id);
      loadHistory();
    }
  };

  const handleClearAll = () => {
    if (window.confirm('Clear all history? This cannot be undone.')) {
      historyService.clearHistory();
      loadHistory();
    }
  };

  const handleExport = () => {
    historyService.exportHistory();
  };

  const toggleExpand = (id) => {
    setExpandedItem(expandedItem === id ? null : id);
  };

  const getWorkflowIcon = (type) => {
    switch(type) {
      case 'reflection': return DocumentTextIcon;
      case 'tool-research': return MagnifyingGlassIcon;
      case 'multi-agent': return UsersIcon;
      default: return DocumentTextIcon;
    }
  };

  const getWorkflowName = (type) => {
    switch(type) {
      case 'reflection': return 'Simple Reflection';
      case 'tool-research': return 'Tool Research';
      case 'multi-agent': return 'Multi-Agent';
      default: return type;
    }
  };

  const getStatusIcon = (status) => {
    switch(status) {
      case 'completed': return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'failed': return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default: return <PendingIcon className="h-5 w-5 text-yellow-500" />;
    }
  };

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatExecutionTime = (ms) => {
    if (!ms) return 'N/A';
    if (ms < 1000) return `${Math.round(ms)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Workflow History</h1>
        <p className="text-gray-600">View and manage your past workflow executions</p>
      </div>

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
            <div className="text-sm text-gray-600 mb-1">Total Executions</div>
            <div className="text-2xl font-bold text-gray-800">{stats.total}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
            <div className="text-sm text-gray-600 mb-1">Cache Hits</div>
            <div className="text-2xl font-bold text-green-600">
              {stats.cacheHits}
              <span className="text-sm text-gray-500 ml-2">
                ({stats.total > 0 ? Math.round((stats.cacheHits / stats.total) * 100) : 0}%)
              </span>
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
            <div className="text-sm text-gray-600 mb-1">Avg Execution Time</div>
            <div className="text-2xl font-bold text-blue-600">{stats.avgExecutionTime}s</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
            <div className="text-sm text-gray-600 mb-1">Success Rate</div>
            <div className="text-2xl font-bold text-purple-600">
              {stats.total > 0 
                ? Math.round(((stats.byStatus.completed || 0) / stats.total) * 100) 
                : 0}%
            </div>
          </div>
        </div>
      )}

      <div className="card mb-6">
        <div className="flex flex-wrap gap-4 items-center justify-between">
          <div className="flex gap-4 flex-wrap flex-1">
            <div className="flex items-center gap-2">
              <FunnelIcon className="h-5 w-5 text-gray-500" />
              <select 
                value={selectedWorkflow}
                onChange={(e) => setSelectedWorkflow(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="all">All Workflows</option>
                <option value="reflection">Simple Reflection</option>
                <option value="tool-research">Tool Research</option>
                <option value="multi-agent">Multi-Agent</option>
              </select>
            </div>

            <select 
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">All Status</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>

            <input
              type="text"
              placeholder="Search by topic..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1 min-w-[200px] px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleExport}
              className="btn btn-secondary flex items-center gap-2"
              disabled={history.length === 0}
            >
              <ArrowDownTrayIcon className="h-5 w-5" />
              Export
            </button>
            <button
              onClick={handleClearAll}
              className="btn btn-danger flex items-center gap-2"
              disabled={history.length === 0}
            >
              <TrashIcon className="h-5 w-5" />
              Clear All
            </button>
          </div>
        </div>
      </div>

      {filteredHistory.length === 0 ? (
        <div className="card text-center py-12">
          <ClockIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-600 mb-2">No History Found</h3>
          <p className="text-gray-500">
            {history.length === 0 
              ? 'Start executing workflows to build your history.' 
              : 'No executions match your filters.'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredHistory.map((item) => {
            const WorkflowIcon = getWorkflowIcon(item.workflowType);
            const isExpanded = expandedItem === item.id;
            
            return (
              <div 
                key={item.id} 
                className="card hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => toggleExpand(item.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="p-3 bg-primary-50 rounded-lg">
                      <WorkflowIcon className="h-6 w-6 text-primary-600" />
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-800">
                          {item.topic}
                        </h3>
                        <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">
                          {getWorkflowName(item.workflowType)}
                        </span>
                        {item.cacheHit && (
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded flex items-center gap-1">
                            <BoltIcon className="h-3 w-3" />
                            Cached
                          </span>
                        )}
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <div className="flex items-center gap-1">
                          <ClockIcon className="h-4 w-4" />
                          {formatDate(item.timestamp)}
                        </div>
                        <div>
                          Execution: {formatExecutionTime(item.executionTime)}
                        </div>
                        <div className="flex items-center gap-1">
                          {getStatusIcon(item.status)}
                          <span className="capitalize">{item.status}</span>
                        </div>
                      </div>

                      {isExpanded && item.result && (
                        <div className="mt-4 pt-4 border-t border-gray-200">
                          <h4 className="font-semibold text-gray-700 mb-2">Results:</h4>
                          <div className="bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto">
                            <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                              {typeof item.result === 'string' 
                                ? item.result 
                                : JSON.stringify(item.result, null, 2)}
                            </pre>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  <button
                    onClick={(e) => handleDelete(item.id, e)}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
                  >
                    <TrashIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default History;
