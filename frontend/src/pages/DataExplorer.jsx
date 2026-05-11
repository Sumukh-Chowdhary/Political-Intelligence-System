import React, { useState, useEffect } from 'react';
import api from '../api/client';

export default function DataExplorer() {
  const [activeTab, setActiveTab] = useState('house');
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [totalRows, setTotalRows] = useState(0);
  const [filters, setFilters] = useState({ state: '', year: '' });
  const [states, setStates] = useState([]);
  const [years, setYears] = useState([]);
  
  const tabs = [
    { id: 'house', label: 'House Results' },
    { id: 'census', label: 'Census Data' },
    { id: 'pvi', label: 'State PVI' }
  ];

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(false);
      try {
        let url = '';
        if (activeTab === 'house') {
          url = '/api/v1/house-results';
          const params = new URLSearchParams();
          if (filters.state) params.append('state', filters.state);
          if (filters.year) params.append('year', filters.year);
          if (params.toString()) url += `?${params.toString()}`;
        } else if (activeTab === 'census') {
          url = '/api/v1/census-data';
        } else {
          url = '/api/v1/state-pvi';
        }
        
        const response = await api.get(url);
        setData(response.data.data || []);
        setTotalRows(response.data.total_rows || 0);
      } catch (err) {
        console.error(`API fetch failed for ${activeTab}:`, err);
        setError(true);
        setData([]);
        setTotalRows(0);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [activeTab, filters.state, filters.year]);

  useEffect(() => {
    const fetchMetadata = async () => {
      if (activeTab === 'house' && data.length > 0) {
        const uniqueStates = [...new Set(data.map(item => item.state))].filter(Boolean);
        const uniqueYears = [...new Set(data.map(item => item.year))].filter(Boolean);
        setStates(uniqueStates);
        setYears(uniqueYears);
      }
    };
    fetchMetadata();
  }, [data, activeTab]);

  const handleStateFilter = (state) => {
    setFilters(prev => ({ ...prev, state: state === 'all' ? '' : state }));
  };

  const handleYearFilter = (year) => {
    setFilters(prev => ({ ...prev, year: year === 'all' ? '' : year }));
  };

  const clearFilters = () => {
    setFilters({ state: '', year: '' });
  };

  const getPartyBadge = (value) => {
    if (value === 'D' || value === 'Democrat') {
      return <span className="text-blue-600 bg-blue-50 px-2.5 py-1 rounded-lg font-bold text-xs">DEM</span>;
    }
    if (value === 'R' || value === 'Republican') {
      return <span className="text-rose-600 bg-rose-50 px-2.5 py-1 rounded-lg font-bold text-xs">REP</span>;
    }
    if (typeof value === 'number') {
      return value.toLocaleString();
    }
    return String(value);
  };

  return (
    <div className="flex flex-col h-full w-full animate-in fade-in duration-500">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Data Explorer</h1>
        <p className="text-slate-400 text-sm mt-1">Raw dataset views for auditing and validation.</p>
      </div>

      <div className="flex gap-2 mb-6 bg-[#f8f7fa] p-1.5 rounded-2xl w-fit border border-slate-100">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => {
              setActiveTab(tab.id);
              setFilters({ state: '', year: '' });
            }}
            className={`px-5 py-2.5 rounded-xl text-sm font-bold transition-all ${
              activeTab === tab.id 
                ? 'bg-white text-slate-900 shadow-sm' 
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'house' && (
        <div className="mb-4 flex gap-3 items-center flex-wrap">
          <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-xl border border-slate-200">
            <span className="text-xs font-semibold text-slate-500">Filter:</span>
            <select 
              onChange={(e) => handleStateFilter(e.target.value)}
              value={filters.state || 'all'}
              className="text-sm font-medium text-slate-700 bg-transparent focus:outline-none"
            >
              <option value="all">All States</option>
              {states.map(state => (
                <option key={state} value={state}>{state}</option>
              ))}
            </select>
          </div>
          
          <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-xl border border-slate-200">
            <select 
              onChange={(e) => handleYearFilter(e.target.value)}
              value={filters.year || 'all'}
              className="text-sm font-medium text-slate-700 bg-transparent focus:outline-none"
            >
              <option value="all">All Years</option>
              {years.map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>
          
          {(filters.state || filters.year) && (
            <button
              onClick={clearFilters}
              className="text-xs font-medium text-red-500 hover:text-red-700 px-3 py-2 rounded-lg hover:bg-red-50 transition-colors"
            >
              Clear Filters
            </button>
          )}
        </div>
      )}

      <div className="flex-1 bg-white rounded-[30px] border border-slate-100 shadow-sm overflow-hidden flex flex-col">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div className="text-sm font-semibold text-slate-700">
            {tabs.find(t => t.id === activeTab)?.label} Dataset
            {totalRows > 0 && (
              <span className="ml-2 text-xs font-normal text-slate-400">
                ({totalRows.toLocaleString()} total records)
              </span>
            )}
          </div>
          {error && (
             <div className="text-[11px] font-bold tracking-wider uppercase bg-red-100 text-red-700 px-3 py-1 rounded-full flex items-center gap-1.5">
               <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></span>
               API Error
             </div>
          )}
        </div>

        <div className="flex-1 overflow-auto">
          {loading ? (
            <div className="h-full w-full flex flex-col items-center justify-center text-slate-400 gap-3">
               <svg className="animate-spin w-8 h-8 text-slate-300" fill="none" viewBox="0 0 24 24">
                 <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                 <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
               </svg>
               <span className="text-sm font-medium">Loading dataset...</span>
            </div>
          ) : data.length > 0 ? (
            <table className="w-full text-left border-collapse">
              <thead className="bg-white sticky top-0 shadow-sm z-10">
                <tr>
                  {Object.keys(data[0]).slice(0, 10).map(key => (
                    <th key={key} className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100 bg-white">
                      {key.replace(/_/g, ' ')}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {data.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/80 transition-colors group">
                    {Object.values(row).slice(0, 10).map((val, idx2) => (
                      <td key={idx2} className="px-6 py-3.5 text-sm font-medium text-slate-600 whitespace-nowrap">
                        {getPartyBadge(val)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="h-full w-full flex flex-col items-center justify-center text-slate-400 text-sm font-medium gap-2">
              <svg className="w-12 h-12 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>No data available for this dataset.</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}