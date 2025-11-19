import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white py-6 mt-12">
      <div className="container mx-auto px-4 text-center">
        <p className="text-sm text-gray-400">
          Advanced Agentic Research Platform v1.0.0
        </p>
        <p className="text-xs text-gray-500 mt-2">
          Multi-agent research system with reflection, tool usage and orchestration
        </p>
      </div>
    </footer>
  );
};

export default Footer;
