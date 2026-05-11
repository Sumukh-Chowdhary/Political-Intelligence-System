// src/pages/ModelPerformance.jsx
import React, { useState, useEffect } from 'react';
import api from '../api/client';

export default function ModelPerformance() {
  const [metrics, setMetrics] = useState({
    accuracy: 0,
    precision_winner: 0,
    recall_winner: 0,
    f1_score: 0
  });
  const [info, setInfo] = useState({
    model: '',
    features: 0,
    device: ''
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(false);
      try {
        const [metricsRes, infoRes] = await Promise.all([
          api.get('/api/v1/metrics'),
          api.get('/api/v1/info')
        ]);
        
        setMetrics(metricsRes.data);
        setInfo(infoRes.data);
        setError(false);
      } catch (err) {
        console.error('Failed to fetch model data:', err);
        setError(true);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const metricCards = [
    { title: "Accuracy", value: `${(metrics.accuracy * 100).toFixed(2)}%`, bg: "bg-[#dcfce7]", text: "text-emerald-600" },
    { title: "Precision", value: `${(metrics.precision_winner * 100).toFixed(0)}%`, bg: "bg-[#e0f2fe]", text: "text-blue-600" },
    { title: "Recall", value: `${(metrics.recall_winner * 100).toFixed(0)}%`, bg: "bg-[#f3f0ff]", text: "text-purple-600" },
    { title: "F1 Score", value: metrics.f1_score.toFixed(2), bg: "bg-[#f1f5f9]", text: "text-slate-600" }
  ];

  const modelDetails = [
    { label: "Algorithm", val: info.model || "PyTorch Neural Network" },
    { label: "Device", val: info.device || "CPU" },
    { label: "Features Used", val: info.features ? info.features.toLocaleString() : "Loading..." },
    { label: "Training Samples", val: "14,781" },
    { label: "Validation Samples", val: "3,696" },
    { label: "Best Score (LogLoss)", val: "0.1850" }
  ];

  const featureImportance = [
    { name: 'Candidate Votes', importance: 0.35 },
    { name: 'Total Votes', importance: 0.28 },
    { name: 'State PVI', importance: 0.15 },
    { name: 'Population', importance: 0.08 },
    { name: 'Median Age', importance: 0.06 },
    { name: 'Party Code', importance: 0.04 },
    { name: 'Income', importance: 0.02 },
    { name: 'Education', importance: 0.01 },
    { name: 'Density', importance: 0.005 },
    { name: 'Race Diversity', importance: 0.003 }
  ];

  if (loading) {
    return (
      <div className="flex flex-col h-full w-full">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Model Performance</h1>
          <p className="text-slate-400 text-sm mt-1">Validation metrics and neural network pipeline details.</p>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="flex flex-col items-center gap-3">
            <svg className="animate-spin w-8 h-8 text-slate-400" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span className="text-sm font-medium text-slate-500">Loading model metrics...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full w-full animate-in fade-in duration-500">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Model Performance</h1>
        <p className="text-slate-400 text-sm mt-1">Validation metrics and neural network pipeline details.</p>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-xl p-3 text-center">
          <span className="text-xs text-red-700">Failed to connect to API. Please check if backend is running on port 8000.</span>
        </div>
      )}

      <div className="grid grid-cols-4 gap-6 mb-8">
        {metricCards.map((item) => (
          <div key={item.title} className={`${item.bg} rounded-3xl p-6 transition-all hover:scale-105 duration-200`}>
            <span className="text-sm font-bold text-slate-700">{item.title}</span>
            <div className="mt-6 text-4xl font-black text-slate-800 tracking-tighter">{item.value}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-6 flex-1">
        <div className="bg-[#f7f7f7] rounded-[30px] p-8 border border-slate-100">
          <h2 className="text-lg font-bold text-slate-800 mb-6">Model Details</h2>
          <div className="space-y-3">
            {modelDetails.map((detail) => (
              <div key={detail.label} className="flex justify-between items-center bg-white p-4 rounded-2xl shadow-sm">
                <span className="text-sm font-semibold text-slate-500">{detail.label}</span>
                <span className="text-sm font-bold text-slate-800">{detail.val}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-[#f7f7f7] rounded-[30px] p-8 border border-slate-100 flex flex-col">
          <h2 className="text-lg font-bold text-slate-800 mb-6">Feature Importance</h2>
          <div className="flex-1 space-y-3">
            {featureImportance.map((feature, idx) => (
              <div key={idx} className="flex items-center gap-3">
                <div className="w-32 text-xs font-medium text-slate-600 truncate">
                  {feature.name}
                </div>
                <div className="flex-1 h-8 bg-white rounded-full overflow-hidden shadow-inner">
                  <div 
                    className="h-full bg-gradient-to-r from-blue-500 to-emerald-500 rounded-full flex items-center justify-end pr-3 text-xs font-bold text-white"
                    style={{ width: `${feature.importance * 100}%` }}
                  >
                    {feature.importance > 0.05 && `${(feature.importance * 100).toFixed(0)}%`}
                  </div>
                </div>
                <div className="w-12 text-right text-xs font-semibold text-slate-500">
                  {(feature.importance * 100).toFixed(1)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}