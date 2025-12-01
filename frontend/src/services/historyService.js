const HISTORY_KEY = 'workflow_history';
const MAX_HISTORY_ITEMS = 100;

export const historyService = {
  saveExecution(workflowType, topic, result, executionTime, status = 'completed') {
    const history = this.getHistory();
    
    const entry = {
      id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      workflowType,
      topic,
      result,
      executionTime,
      status,
      timestamp: new Date().toISOString(),
      cacheHit: result?.cacheHit || false
    };
    
    history.unshift(entry);
    
    if (history.length > MAX_HISTORY_ITEMS) {
      history.splice(MAX_HISTORY_ITEMS);
    }
    
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    
    return entry;
  },
  
  getHistory() {
    try {
      const data = localStorage.getItem(HISTORY_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Error reading history:', error);
      return [];
    }
  },
  
  getById(id) {
    const history = this.getHistory();
    return history.find(item => item.id === id);
  },
  
  deleteById(id) {
    const history = this.getHistory();
    const filtered = history.filter(item => item.id !== id);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(filtered));
    return filtered;
  },
  
  clearHistory() {
    localStorage.removeItem(HISTORY_KEY);
  },
  
  exportHistory() {
    const history = this.getHistory();
    const dataStr = JSON.stringify(history, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `workflow-history-${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  },
  
  getStats() {
    const history = this.getHistory();
    
    const stats = {
      total: history.length,
      byWorkflow: {},
      byStatus: {},
      cacheHits: 0,
      avgExecutionTime: 0
    };
    
    let totalTime = 0;
    
    history.forEach(item => {
      stats.byWorkflow[item.workflowType] = (stats.byWorkflow[item.workflowType] || 0) + 1;
      stats.byStatus[item.status] = (stats.byStatus[item.status] || 0) + 1;
      
      if (item.cacheHit) {
        stats.cacheHits++;
      }
      
      if (item.executionTime) {
        totalTime += item.executionTime;
      }
    });
    
    if (history.length > 0) {
      stats.avgExecutionTime = (totalTime / history.length).toFixed(2);
    }
    
    return stats;
  }
};
