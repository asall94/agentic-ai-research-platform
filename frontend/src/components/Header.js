import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { BeakerIcon, HomeIcon, Cog6ToothIcon } from '@heroicons/react/24/outline';

const Header = () => {
  const location = useLocation();
  
  const isActive = (path) => location.pathname === path;
  
  return (
    <header className="bg-gradient-to-r from-primary-600 to-secondary-600 text-white shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-3">
            <BeakerIcon className="h-8 w-8" />
            <div>
              <h1 className="text-2xl font-bold">Agentic Research Platform</h1>
              <p className="text-sm text-primary-100">Multi-Agent AI Research System</p>
            </div>
          </Link>
          
          <nav className="flex space-x-6">
            <Link
              to="/"
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition ${
                isActive('/') 
                  ? 'bg-white/20 font-semibold' 
                  : 'hover:bg-white/10'
              }`}
            >
              <HomeIcon className="h-5 w-5" />
              <span>Home</span>
            </Link>
            
            <Link
              to="/history"
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition ${
                isActive('/history') 
                  ? 'bg-white/20 font-semibold' 
                  : 'hover:bg-white/10'
              }`}
            >
              <Cog6ToothIcon className="h-5 w-5" />
              <span>History</span>
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
