import React from 'react';
import { CheckCircleIcon, XCircleIcon, ClockIcon } from '@heroicons/react/24/solid';

const WorkflowCard = ({ title, description, icon: Icon, onClick, color = "primary" }) => {
  const colorClasses = {
    primary: "from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700",
    secondary: "from-secondary-500 to-secondary-600 hover:from-secondary-600 hover:to-secondary-700",
    accent: "from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700"
  };
  
  return (
    <div
      onClick={onClick}
      className={`card cursor-pointer transform transition duration-300 hover:scale-105 hover:shadow-2xl bg-gradient-to-br ${colorClasses[color]} text-white`}
    >
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          <Icon className="h-12 w-12 opacity-90" />
        </div>
        <div className="flex-1">
          <h3 className="text-xl font-bold mb-2">{title}</h3>
          <p className="text-sm opacity-90">{description}</p>
        </div>
      </div>
    </div>
  );
};

const StatusBadge = ({ status }) => {
  const statusConfig = {
    completed: { icon: CheckCircleIcon, color: 'green', text: 'Completed' },
    failed: { icon: XCircleIcon, color: 'red', text: 'Failed' },
    running: { icon: ClockIcon, color: 'yellow', text: 'Running' },
  };
  
  const config = statusConfig[status] || statusConfig.running;
  const Icon = config.icon;
  
  return (
    <span className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-sm font-medium bg-${config.color}-100 text-${config.color}-800`}>
      <Icon className="h-4 w-4" />
      <span>{config.text}</span>
    </span>
  );
};

const LoadingSpinner = ({ size = "md" }) => {
  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-8 w-8",
    lg: "h-12 w-12"
  };
  
  return (
    <div className="flex justify-center items-center">
      <div className={`${sizeClasses[size]} border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin`}></div>
    </div>
  );
};

export { WorkflowCard, StatusBadge, LoadingSpinner };
