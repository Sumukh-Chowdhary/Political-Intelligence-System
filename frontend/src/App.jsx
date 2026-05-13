import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import api from './api/client';
import Dashboard from './pages/Dashboard';
import ModelPerformance from './pages/ModelPerformance';
import Predictions from './pages/Predictions';
import DataExplorer from './pages/DataExplorer';
import Map from './pages/Map';
import DistrictView from './pages/DistrictView';
import DistrictDetail from './pages/DistrictDetail';

function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [apiStatus, setApiStatus] = useState('checking');

  const menu = [
    { path: '/', label: 'Dashboard', icon: 'M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6z' },
    { path: '/model', label: 'Model Performance', icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
    { path: '/predictions', label: 'Predictions', icon: 'M13 10V3L4 14h7v7l9-11h-7z' },
    { path: '/map', label: 'Election Map', icon: 'M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7' },
    { path: '/explorer', label: 'Data Explorer', icon: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z' }
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

  const isActive = (path) => {
    if (path === '/map' && location.pathname.startsWith('/state/')) return true;
    return location.pathname === path;
  };

  return (
    <div className="w-[280px] bg-[#f8f7fa] p-6 flex flex-col justify-between border-r border-slate-200">
      <div>
        <div className="flex items-center gap-3 px-2 mb-10">
          <div className="w-10 h-10 rounded-xl bg-slate-900 text-white flex items-center justify-center font-bold text-xl shadow-md">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
            </svg>
          </div>
          <span className="font-bold text-xl tracking-tight">PoliDash</span>
        </div>
        
        <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4 px-2">Main Menu</div>
        <div className="space-y-2">
          {menu.map((item) => (
            <button 
              key={item.path}
              onClick={() => navigate(item.path)}
              className={`w-full flex items-center gap-3 px-4 py-3.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive(item.path)
                  ? "bg-white shadow-sm text-slate-900 border border-slate-200/60" 
                  : "text-slate-500 hover:bg-slate-200/50 hover:text-slate-800 border border-transparent"
              }`}
            >
              <svg className={`w-5 h-5 ${isActive(item.path) ? 'text-slate-800' : 'text-slate-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
              </svg>
              {item.label}
            </button>
          ))}
        </div>
      </div>
      
      <div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-slate-200 mb-6">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500">API Status</span>
            <span className="flex h-3 w-3 relative">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${apiStatus === 'connected' ? 'bg-emerald-400' : 'bg-rose-400'}`}></span>
              <span className={`relative inline-flex rounded-full h-3 w-3 ${apiStatus === 'connected' ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
            </span>
          </div>
          <div className="text-sm font-bold text-slate-800 mt-1 capitalize">{apiStatus}</div>
        </div>

        <div className="flex items-center gap-3 px-2">
          <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-slate-300 to-slate-200 border border-slate-300 shadow-sm"></div>
          <div>
            <div className="text-sm font-bold text-slate-800">System Admin</div>
            <div className="text-[11px] text-slate-500 font-medium">Political Intelligence</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <div className="flex h-screen w-screen overflow-hidden bg-white font-sans text-slate-800">
        <Sidebar />
        <main className="flex-1 h-full overflow-y-auto bg-white flex flex-col p-6 md:p-10">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/model" element={<ModelPerformance />} />
            <Route path="/predictions" element={<Predictions />} />
            <Route path="/explorer" element={<DataExplorer />} />
            <Route path="/map" element={<Map />} />
            <Route path="/state/:stateCode" element={<DistrictView />} />
            <Route path="/district/:districtId" element={<DistrictDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}