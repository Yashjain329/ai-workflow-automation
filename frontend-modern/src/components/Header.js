import React from 'react';
import './Header.css';

const Header = () => {
  return (
    <header className="bg-slate-800 border-b border-slate-700 px-6 py-4 flex items-center justify-between shadow-lg">
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white shadow-md">
          AI
        </div>
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide">Intelligent Workflow Automation</h1>
          <p className="text-xs text-slate-400">Operations Dashboard • v1.0</p>
        </div>
      </div>
      <div className="flex items-center space-x-4">
        <button id="refreshButton" className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-xs font-semibold rounded-lg transition-colors flex items-center space-x-2">
          <span>🔄 Refresh</span>
        </button>
        <button id="submitJobButton" className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white rounded-lg shadow-md transition-colors">
          + Submit Job
        </button>
      </div>
    </header>
  );
};

export default Header;