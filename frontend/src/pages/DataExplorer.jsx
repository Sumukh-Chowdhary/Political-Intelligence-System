import React, { useState, useEffect, useCallback } from 'react';
import api from '../api/client';

const TABS = [
  { id: 'house',  label: 'House Results',  endpoint: '/api/v1/house-results' },
  { id: 'census', label: 'Census Data',    endpoint: '/api/v1/census-data'   },
  { id: 'pvi',    label: 'State PVI',      endpoint: '/api/v1/state-pvi'     },
];

const ITEMS_PER_PAGE = 50;

// Columns to display per tab (avoids showing 200-column census tables)
const DISPLAY_COLS = {
  house:  ['year', 'state', 'district', 'candidate', 'party', 'votes', 'total_votes'],
  census: ['district_id', 'district_name', 'total_population', 'median_age',
           'white_pct', 'black_pct', 'hispanic_pct', 'median_household_income',
           'college_grad_pct', 'poverty_rate_pct', 'unemployment_rate_pct'],
  pvi:    ['state', 'pvi_score', 'pvi_label', 'state_lean', 'avg_dem_pct', 'avg_rep_pct'],
};

function PartyBadge({ value }) {
  if (value === 'D' || value === 'Democrat')
    return <span className="text-blue-600 bg-blue-50 px-2.5 py-1 rounded-lg font-bold text-xs">DEM</span>;
  if (value === 'R' || value === 'Republican')
    return <span className="text-rose-600 bg-rose-50 px-2.5 py-1 rounded-lg font-bold text-xs">REP</span>;
  return <span>{value === null || value === undefined ? '—' : String(value)}</span>;
}

function formatCell(key, val) {
  if (key === 'party') return <PartyBadge value={val} />;
  if (val === null || val === undefined) return <span className="text-slate-300">—</span>;
  if (typeof val === 'number') return val.toLocaleString();
  return String(val);
}

export default function DataExplorer() {
  const [activeTab, setActiveTab] = useState('house');
  const [data, setData]           = useState([]);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState(null);
  const [page, setPage]           = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalRows, setTotalRows]   = useState(0);

  // House-only filters
  const [states, setStates] = useState([]);
  const [years, setYears]   = useState([]);
  const [stateFilter, setStateFilter] = useState('');
  const [yearFilter, setYearFilter]   = useState('');

  // ── fetch metadata for house tab ─────────────────────────────────────────
  useEffect(() => {
    if (activeTab !== 'house') return;
    api.get('/api/v1/house-results/meta')
      .then(r => {
        setStates(r.data.states || []);
        setYears(r.data.years || []);
      })
      .catch(() => {});
  }, [activeTab]);

  // ── fetch page data ───────────────────────────────────────────────────────
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const tab = TABS.find(t => t.id === activeTab);
      const params = new URLSearchParams({ page, limit: ITEMS_PER_PAGE });

      if (activeTab === 'house') {
        if (stateFilter) params.append('state', stateFilter);
        if (yearFilter)  params.append('year',  yearFilter);
      }

      const res = await api.get(`${tab.endpoint}?${params}`);
      const body = res.data;

      setData(body.data || []);
      setTotalRows(body.total_rows ?? body.data?.length ?? 0);
      setTotalPages(body.total_pages ?? 1);
    } catch (err) {
      setError('Failed to load data — check that the backend is running.');
      setData([]);
    } finally {
      setLoading(false);
    }
  }, [activeTab, page, stateFilter, yearFilter]);

  useEffect(() => { fetchData(); }, [fetchData]);

  // ── tab switch resets state ───────────────────────────────────────────────
  const switchTab = (id) => {
    setActiveTab(id);
    setPage(1);
    setStateFilter('');
    setYearFilter('');
    setData([]);
  };

  const clearFilters = () => { setStateFilter(''); setYearFilter(''); setPage(1); };

  const displayCols = data.length ? DISPLAY_COLS[activeTab] : [];

  return (
    <div className="flex flex-col h-full w-full animate-in fade-in duration-500">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Data Explorer</h1>
        <p className="text-slate-400 text-sm mt-1">Raw dataset views for auditing and validation.</p>
      </div>

      {/* Tab bar */}
      <div className="flex gap-2 mb-6 bg-[#f8f7fa] p-1.5 rounded-2xl w-fit border border-slate-100">
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => switchTab(tab.id)}
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

      {/* House filters */}
      {activeTab === 'house' && (
        <div className="mb-4 flex gap-3 items-center flex-wrap">
          <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-xl border border-slate-200">
            <span className="text-xs font-semibold text-slate-500">State</span>
            <select
              value={stateFilter || 'all'}
              onChange={e => { setStateFilter(e.target.value === 'all' ? '' : e.target.value); setPage(1); }}
              className="text-sm font-medium text-slate-700 bg-transparent focus:outline-none"
            >
              <option value="all">All States</option>
              {states.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>

          <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-xl border border-slate-200">
            <span className="text-xs font-semibold text-slate-500">Year</span>
            <select
              value={yearFilter || 'all'}
              onChange={e => { setYearFilter(e.target.value === 'all' ? '' : e.target.value); setPage(1); }}
              className="text-sm font-medium text-slate-700 bg-transparent focus:outline-none"
            >
              <option value="all">All Years</option>
              {years.map(y => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>

          {(stateFilter || yearFilter) && (
            <button
              onClick={clearFilters}
              className="text-xs font-medium text-red-500 hover:text-red-700 px-3 py-2 rounded-lg hover:bg-red-50 transition-colors"
            >
              Clear Filters
            </button>
          )}
        </div>
      )}

      {/* Table card */}
      <div className="flex-1 bg-white rounded-[30px] border border-slate-100 shadow-sm overflow-hidden flex flex-col">
        {/* Card header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div className="text-sm font-semibold text-slate-700">
            {TABS.find(t => t.id === activeTab)?.label}
            {totalRows > 0 && (
              <span className="ml-2 text-xs font-normal text-slate-400">
                ({totalRows.toLocaleString()} total records)
              </span>
            )}
          </div>
          {error && (
            <span className="text-xs text-red-500 bg-red-50 px-3 py-1 rounded-lg">{error}</span>
          )}
        </div>

        {/* Table body */}
        <div className="flex-1 overflow-auto">
          {loading ? (
            <div className="h-full flex items-center justify-center text-slate-400 gap-2">
              <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Loading…
            </div>
          ) : data.length > 0 ? (
            <table className="w-full text-left border-collapse">
              <thead className="bg-white sticky top-0 shadow-sm z-10">
                <tr>
                  {displayCols.map(key => (
                    <th key={key} className="px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100 bg-white whitespace-nowrap">
                      {key.replace(/_/g, ' ')}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {data.map((row, i) => (
                  <tr key={i} className="hover:bg-slate-50/80 transition-colors">
                    {displayCols.map(key => (
                      <td key={key} className="px-6 py-3.5 text-sm font-medium text-slate-600 whitespace-nowrap">
                        {formatCell(key, row[key])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="h-full flex items-center justify-center text-slate-400">
              No data available.
            </div>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-slate-100 flex items-center justify-between">
            <span className="text-xs text-slate-400">
              Page {page} of {totalPages} · {totalRows.toLocaleString()} records
            </span>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(1)}
                disabled={page === 1}
                className="px-3 py-1 text-xs font-medium text-slate-600 border border-slate-200 rounded-lg disabled:opacity-40 hover:bg-slate-50"
              >
                «
              </button>
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1 text-sm font-medium text-slate-600 border border-slate-200 rounded-lg disabled:opacity-40 hover:bg-slate-50"
              >
                Previous
              </button>
              <span className="px-4 py-1 text-sm font-medium text-slate-700 bg-slate-50 rounded-lg border border-slate-200">
                {page}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-3 py-1 text-sm font-medium text-slate-600 border border-slate-200 rounded-lg disabled:opacity-40 hover:bg-slate-50"
              >
                Next
              </button>
              <button
                onClick={() => setPage(totalPages)}
                disabled={page === totalPages}
                className="px-3 py-1 text-xs font-medium text-slate-600 border border-slate-200 rounded-lg disabled:opacity-40 hover:bg-slate-50"
              >
                »
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}