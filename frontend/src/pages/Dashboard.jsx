// src/pages/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import api from '../api/client';

export default function Dashboard() {
  const [stats, setStats] = useState({
    total_elections: 14781,
    districts: 435,
    states: 50,
    years: "1976-2024"
  });

  return (
    <div className="flex flex-col h-full w-full animate-in fade-in duration-500">
      <div className="mb-8">
        <div className="flex items-center gap-2 text-sm font-medium mb-2">
          <span className="text-slate-400">Political Intelligence</span>
          <svg className="w-4 h-4 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
          <span className="text-slate-800">Dashboard</span>
        </div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Election Overview</h1>
        <p className="text-slate-400 text-sm mt-1">Historical data scope and baseline election statistics.</p>
      </div>

      <div className="grid grid-cols-4 gap-6 mb-8">
        {[
          { title: "Total Elections", value: stats.total_elections, bg: "bg-[#f3f0ff]", text: "text-purple-600" },
          { title: "Districts", value: stats.districts, bg: "bg-[#e0f2fe]", text: "text-blue-600" },
          { title: "States", value: stats.states, bg: "bg-[#f1f5f9]", text: "text-slate-600" },
          { title: "Year Range", value: stats.years, bg: "bg-[#fef3c7]", text: "text-amber-600" }
        ].map((item) => (
          <div key={item.title} className={`${item.bg} rounded-3xl p-6 relative overflow-hidden group`}>
            <div className="relative z-10">
              <span className="text-sm font-bold text-slate-700">{item.title}</span>
              <div className="mt-6 text-4xl font-black text-slate-800 tracking-tighter">{item.value.toLocaleString()}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-[2fr_1fr] gap-6 flex-1">
        <div className="bg-[#f7f7f7] rounded-[30px] p-8 border border-slate-100 flex flex-col">
          <h2 className="text-lg font-bold text-slate-800 mb-6">Historical Trends Placeholder</h2>
          <div className="flex-1 border-2 border-dashed border-slate-200 rounded-2xl flex items-center justify-center bg-white">
            <span className="text-slate-400 font-medium">Chart Visualization Area</span>
          </div>
        </div>
        <div className="bg-[#f7f7f7] rounded-[30px] p-8 border border-slate-100 flex flex-col">
          <h2 className="text-lg font-bold text-slate-800 mb-6">Distribution</h2>
          <div className="flex-1 border-2 border-dashed border-slate-200 rounded-2xl flex items-center justify-center bg-white">
             <span className="text-slate-400 font-medium">Donut Chart Area</span>
          </div>
        </div>
      </div>
    </div>
  );
}