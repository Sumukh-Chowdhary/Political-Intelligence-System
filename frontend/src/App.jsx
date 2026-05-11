// src/App.jsx
import React, { useState, useEffect } from 'react';
import api from './api/client';
import Dashboard from './pages/Dashboard';
import ModelPerformance from './pages/ModelPerformance';
import Predictions from './pages/Predictions';
import DataExplorer from './pages/DataExplorer';

export default function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [apiStatus, setApiStatus] = useState('checking');

  const menu = [
    { id: 'dashboard', label: 'Dashboard', icon: 'M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z' },
    { id: 'model', label: 'Model Performance', icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
    { id: 'predictions', label: 'Predictions', icon: 'M13 10V3L4 14h7v7l9-11h-7z' },
    { id: 'explorer', label: 'Data Explorer', icon: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z' }
  ];

  useEffect(() => {
    const checkApi = async () => {
      try {
        await api.get('/');
        setApiStatus('connected');
      } catch (err) {
        setApiStatus('disconnected');
      }
    };
    checkApi();
  }, []);

  return (
    <div className="min-h-screen bg-[#d7d7d9] p-4 md:p-8 flex items-center justify-center font-sans text-slate-800">
      <div className="w-full max-w-[1500px] h-[900px] bg-white rounded-[40px] shadow-2xl flex overflow-hidden border-[8px] border-white/50">
        
        <div className="w-[280px] bg-[#f8f7fa] p-6 flex flex-col justify-between border-r border-slate-100/50">
          <div>
            <div className="flex items-center gap-3 px-2 mb-10">
              <div className="w-10 h-10 rounded-xl bg-slate-900 text-white flex items-center justify-center font-bold text-xl shadow-md">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
                </svg>
              </div>
              <span className="font-bold text-lg tracking-tight">PoliDash</span>
            </div>
            
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4 px-2">Main Menu</div>
            <div className="space-y-1">
              {menu.map((item) => (
                <button 
                  key={item.id}
                  onClick={() => setCurrentPage(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3.5 rounded-2xl text-sm font-medium transition-all duration-300 ${
                    currentPage === item.id 
                      ? "bg-white shadow-sm text-slate-900" 
                      : "text-slate-500 hover:bg-white/60 hover:text-slate-700"
                  }`}
                >
                  <svg className={`w-5 h-5 ${currentPage === item.id ? 'text-slate-800' : 'text-slate-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
                  </svg>
                  {item.label}
                </button>
              ))}
            </div>
          </div>
          
          <div>
            <div className="bg-white rounded-2xl p-4 shadow-sm border border-slate-100 mb-6">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-500">API Status</span>
                <span className="flex h-3 w-3 relative">
                  <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${apiStatus === 'connected' ? 'bg-emerald-400' : 'bg-rose-400'}`}></span>
                  <span className={`relative inline-flex rounded-full h-3 w-3 ${apiStatus === 'connected' ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
                </span>
              </div>
              <div className="text-sm font-bold text-slate-800 mt-1 capitalize">{apiStatus}</div>
            </div>

            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4 px-2">Account</div>
            <div className="flex items-center gap-3 px-2">
              <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-slate-300 to-slate-200 border-2 border-white shadow-sm"></div>
              <div>
                <div className="text-sm font-bold text-slate-800">System Admin</div>
                <div className="text-[11px] text-slate-400 font-medium">Political Intelligence</div>
              </div>
            </div>
          </div>
        </div>

        <div className="flex-1 bg-white p-10 overflow-auto flex flex-col">
          {currentPage === 'dashboard' && <Dashboard />}
          {currentPage === 'model' && <ModelPerformance />}
          {currentPage === 'predictions' && <Predictions />}
          {currentPage === 'explorer' && <DataExplorer />}
        </div>
      </div>
    </div>
  );
}