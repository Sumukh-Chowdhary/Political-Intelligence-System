// React Dashboard Component - src/App.jsx
// Political Intelligence System Frontend

import React, { useState, useEffect } from 'react';
import './App.css';
import api from './api/client';

// Import page components
import Dashboard from './pages/Dashboard';
import ModelPerformance from './pages/ModelPerformance';
import Predictions from './pages/Predictions';
import DataExplorer from './pages/DataExplorer';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [apiStatus, setApiStatus] = useState(null);

  useEffect(() => {
    // Check API health on mount
    checkApiHealth();
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await api.get('/health');
      setApiStatus(response.data);
      setLoading(false);
    } catch (error) {
      console.error('API health check failed:', error);
      setApiStatus({ status: 'unhealthy', error: error.message });
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="App">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1>🇺🇸 Political Intelligence System</h1>
          <p>Election Outcome Prediction with ML</p>
        </div>
        <div className="api-status">
          {apiStatus?.status === 'healthy' ? (
            <span className="status-healthy">✓ API Connected</span>
          ) : (
            <span className="status-error">✗ API Disconnected</span>
          )}
        </div>
      </header>

      {/* Navigation */}
      <nav className="app-nav">
        <button
          className={`nav-button ${currentPage === 'dashboard' ? 'active' : ''}`}
          onClick={() => setCurrentPage('dashboard')}
        >
          📊 Dashboard
        </button>
        <button
          className={`nav-button ${currentPage === 'model' ? 'active' : ''}`}
          onClick={() => setCurrentPage('model')}
        >
          🎓 Model Performance
        </button>
        <button
          className={`nav-button ${currentPage === 'predictions' ? 'active' : ''}`}
          onClick={() => setCurrentPage('predictions')}
        >
          🔮 Predictions
        </button>
        <button
          className={`nav-button ${currentPage === 'explorer' ? 'active' : ''}`}
          onClick={() => setCurrentPage('explorer')}
        >
          🔍 Data Explorer
        </button>
      </nav>

      {/* Main Content */}
      <main className="app-main">
        {currentPage === 'dashboard' && <Dashboard />}
        {currentPage === 'model' && <ModelPerformance />}
        {currentPage === 'predictions' && <Predictions />}
        {currentPage === 'explorer' && <DataExplorer />}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>Political Intelligence System | Built with React & FastAPI</p>
        <p>Data: 1976-2024 House Elections</p>
      </footer>
    </div>
  );
}

export default App;


// ============================================================================
// src/api/client.js - API Client Configuration
// ============================================================================

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  config => {
    console.log('API Request:', config.url);
    return config;
  },
  error => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

export default api;


// ============================================================================
// src/pages/Dashboard.jsx - Dashboard Page
// ============================================================================

import React, { useState, useEffect } from 'react';
import api from '../api/client';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStatistics();
  }, []);

  const fetchStatistics = async () => {
    try {
      const response = await api.get('/api/v1/statistics');
      setStats(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="page-content">
      <h2>📊 Election Dashboard</h2>
      
      {stats && (
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-value">{stats.total_elections}</div>
            <div className="metric-label">Total Elections</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{stats.districts}</div>
            <div className="metric-label">Districts</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{stats.states}</div>
            <div className="metric-label">States</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{stats.years}</div>
            <div className="metric-label">Year Range</div>
          </div>
        </div>
      )}
      
      <div className="charts-grid">
        <div className="chart-container">
          <h3>Elections by Year</h3>
          {/* Add Plotly chart here */}
        </div>
        <div className="chart-container">
          <h3>Party Distribution</h3>
          {/* Add Plotly chart here */}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;


// ============================================================================
// src/pages/ModelPerformance.jsx - Model Metrics Page
// ============================================================================

import React, { useState, useEffect } from 'react';
import api from '../api/client';

function ModelPerformance() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await api.get('/api/v1/metrics');
      setMetrics(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="page-content">
      <h2>🎓 Model Performance</h2>
      
      {metrics && (
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-value">{(metrics.accuracy * 100).toFixed(2)}%</div>
            <div className="metric-label">Accuracy</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{(metrics.precision_winner * 100).toFixed(0)}%</div>
            <div className="metric-label">Precision (Winner)</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{(metrics.recall_winner * 100).toFixed(0)}%</div>
            <div className="metric-label">Recall (Winner)</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{metrics.f1_score.toFixed(2)}</div>
            <div className="metric-label">F1 Score</div>
          </div>
        </div>
      )}
      
      <div className="details-section">
        <h3>Model Details</h3>
        <ul>
          <li><strong>Algorithm:</strong> XGBoost (GPU-accelerated)</li>
          <li><strong>Training Samples:</strong> 14,781</li>
          <li><strong>Features:</strong> 244</li>
          <li><strong>Best Score (LogLoss):</strong> 0.1850</li>
        </ul>
      </div>
    </div>
  );
}

export default ModelPerformance;


// ============================================================================
// src/pages/Predictions.jsx - Make Predictions
// ============================================================================

import React, { useState } from 'react';
import api from '../api/client';

function Predictions() {
  const [formData, setFormData] = useState({
    party: 'D',
    candidate_votes: 50000,
    total_votes: 200000,
    district_id: 1,
    state: 'CA',
    year: 2024,
  });
  
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await api.post('/api/v1/predict', formData);
      setPrediction(response.data);
    } catch (error) {
      console.error('Prediction failed:', error);
      alert('Prediction failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-content">
      <h2>🔮 Make Predictions</h2>
      
      <div className="prediction-container">
        <form className="prediction-form" onSubmit={handlePredict}>
          <div className="form-group">
            <label>Party</label>
            <select
              name="party"
              value={formData.party}
              onChange={handleChange}
            >
              <option value="D">Democratic</option>
              <option value="R">Republican</option>
              <option value="O">Other</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>Candidate Votes</label>
            <input
              type="number"
              name="candidate_votes"
              value={formData.candidate_votes}
              onChange={handleChange}
              min="0"
            />
          </div>
          
          <div className="form-group">
            <label>Total District Votes</label>
            <input
              type="number"
              name="total_votes"
              value={formData.total_votes}
              onChange={handleChange}
              min="1"
            />
          </div>
          
          <div className="form-group">
            <label>State</label>
            <input
              type="text"
              name="state"
              value={formData.state}
              onChange={handleChange}
              maxLength="2"
            />
          </div>
          
          <div className="form-group">
            <label>Year</label>
            <input
              type="number"
              name="year"
              value={formData.year}
              onChange={handleChange}
              min="1976"
              max="2024"
            />
          </div>
          
          <button type="submit" disabled={loading} className="predict-button">
            {loading ? 'Predicting...' : 'Make Prediction'}
          </button>
        </form>
        
        {prediction && (
          <div className="prediction-result">
            <h3>Prediction Result</h3>
            <div className={`result-badge ${prediction.is_winner ? 'winner' : 'non-winner'}`}>
              {prediction.is_winner ? '🎉 WINNER' : '❌ Non-Winner'}
            </div>
            <div className="confidence-bar">
              <div
                className="confidence-fill"
                style={{ width: `${prediction.probability * 100}%` }}
              />
            </div>
            <p>Confidence: {(prediction.confidence * 100).toFixed(1)}%</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Predictions;


// ============================================================================
// src/pages/DataExplorer.jsx - Explore Data
// ============================================================================

import React, { useState, useEffect } from 'react';
import api from '../api/client';

function DataExplorer() {
  const [activeTab, setActiveTab] = useState('house');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchData(activeTab);
  }, [activeTab]);

  const fetchData = async (tab) => {
    setLoading(true);
    try {
      let response;
      if (tab === 'house') {
        response = await api.get('/api/v1/house-results');
      } else if (tab === 'census') {
        response = await api.get('/api/v1/census-data');
      } else {
        response = await api.get('/api/v1/state-pvi');
      }
      setData(response.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-content">
      <h2>🔍 Data Explorer</h2>
      
      <div className="tabs">
        <button
          className={`tab-button ${activeTab === 'house' ? 'active' : ''}`}
          onClick={() => setActiveTab('house')}
        >
          House Results
        </button>
        <button
          className={`tab-button ${activeTab === 'census' ? 'active' : ''}`}
          onClick={() => setActiveTab('census')}
        >
          Census Data
        </button>
        <button
          className={`tab-button ${activeTab === 'pvi' ? 'active' : ''}`}
          onClick={() => setActiveTab('pvi')}
        >
          State PVI
        </button>
      </div>
      
      {loading ? (
        <div>Loading...</div>
      ) : (
        <div className="data-table">
          {data && (
            <>
              <p>Total rows: {data.total_rows} | Displayed: {data.returned}</p>
              <table>
                <thead>
                  <tr>
                    {data.data && data.data[0] && Object.keys(data.data[0]).map(key => (
                      <th key={key}>{key}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.data && data.data.map((row, idx) => (
                    <tr key={idx}>
                      {Object.values(row).map((val, idx2) => (
                        <td key={idx2}>{String(val).substring(0, 50)}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default DataExplorer;


// ============================================================================
// src/App.css - Styles
// ============================================================================
/*
.App {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f5f5f5;
}

.app-header {
  background: linear-gradient(135deg, #1f77b4 0%, #2ca02c 100%);
  color: white;
  padding: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.header-content h1 {
  margin: 0;
  font-size: 2em;
}

.app-nav {
  display: flex;
  background: white;
  border-bottom: 2px solid #ddd;
  padding: 0 2rem;
  gap: 1rem;
}

.nav-button {
  background: none;
  border: none;
  padding: 1rem 1.5rem;
  font-size: 1rem;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
}

.nav-button:hover,
.nav-button.active {
  color: #1f77b4;
  border-bottom-color: #1f77b4;
}

.app-main {
  flex: 1;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.page-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin: 2rem 0;
}

.metric-card {
  background: #f0f2f6;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
  border-left: 4px solid #1f77b4;
}

.metric-value {
  font-size: 2em;
  font-weight: bold;
  color: #1f77b4;
}

.metric-label {
  color: #666;
  margin-top: 0.5rem;
}

.app-footer {
  background: #333;
  color: white;
  padding: 2rem;
  text-align: center;
  border-top: 2px solid #1f77b4;
}
*/
