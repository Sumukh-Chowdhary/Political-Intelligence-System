import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import api from '../api/client';

export default function Map() {
  const navigate = useNavigate();
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const geoJsonLayerRef = useRef(null);

  const [predictions, setPredictions] = useState([]);
  const [summary, setSummary] = useState({ democrat_projections: 0, republican_projections: 0 });
  const [hoveredState, setHoveredState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [geoData, setGeoData] = useState(null);

  const fipsToState = {
    '01': 'Alabama', '02': 'Alaska', '04': 'Arizona', '05': 'Arkansas', '06': 'California',
    '08': 'Colorado', '09': 'Connecticut', '10': 'Delaware', '12': 'Florida', '13': 'Georgia',
    '15': 'Hawaii', '16': 'Idaho', '17': 'Illinois', '18': 'Indiana', '19': 'Iowa',
    '20': 'Kansas', '21': 'Kentucky', '22': 'Louisiana', '23': 'Maine', '24': 'Maryland',
    '25': 'Massachusetts', '26': 'Michigan', '27': 'Minnesota', '28': 'Mississippi', '29': 'Missouri',
    '30': 'Montana', '31': 'Nebraska', '32': 'Nevada', '33': 'New Hampshire', '34': 'New Jersey',
    '35': 'New Mexico', '36': 'New York', '37': 'North Carolina', '38': 'North Dakota', '39': 'Ohio',
    '40': 'Oklahoma', '41': 'Oregon', '42': 'Pennsylvania', '44': 'Rhode Island', '45': 'South Carolina',
    '46': 'South Dakota', '47': 'Tennessee', '48': 'Texas', '49': 'Utah', '50': 'Vermont',
    '51': 'Virginia', '53': 'Washington', '54': 'West Virginia', '55': 'Wisconsin', '56': 'Wyoming'
  };

  const getStateCodeFromName = (stateName) => {
    const stateMap = {
      'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
      'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
      'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
      'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
      'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
      'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
      'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
      'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
      'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
      'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
    };
    return stateMap[stateName] || '';
  };

  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    mapInstanceRef.current = L.map(mapContainerRef.current, {
      center: [39.8, -98.5],
      zoom: 4,
      zoomControl: false,
    });

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; CARTO',
      subdomains: 'abcd',
      maxZoom: 20
    }).addTo(mapInstanceRef.current);

    L.control.zoom({ position: 'bottomleft' }).addTo(mapInstanceRef.current);

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    let isMounted = true;
    const loadData = async () => {
      try {
        const [predRes, sumRes, mapRes] = await Promise.all([
          api.get('/api/v1/predictions?limit=500'),
          api.get('/api/v1/predictions/summary'),
          fetch('/us_districts.json').catch(() => ({ ok: false }))
        ]);
        
        if (!isMounted) return;

        setPredictions(predRes.data?.data || []);
        setSummary(sumRes.data || { democrat_projections: 0, republican_projections: 0 });
        
        if (mapRes.ok) {
          const mapJson = await mapRes.json();
          setGeoData(mapJson);
        }
      } catch (err) {
        console.error("Failed to load map data", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };
    loadData();
    return () => { isMounted = false; };
  }, []);

  useEffect(() => {
    if (!mapInstanceRef.current || !geoData || predictions.length === 0) return;

    if (geoJsonLayerRef.current) {
      mapInstanceRef.current.removeLayer(geoJsonLayerRef.current);
      geoJsonLayerRef.current = null;
    }

    const getStyle = (feature) => {
      const stateName = fipsToState[feature.properties.STATEFP];
      if (!stateName) return { fillColor: '#CBD5E1', weight: 1, color: '#ffffff', fillOpacity: 0.7 };
      
      const stateCode = getStateCodeFromName(stateName);
      let districtNum = feature.properties.CD119FP;
      if (districtNum === '00') districtNum = 'AL';
      
      const apiDistrictIdShort = `${stateCode}-${districtNum}`;
      const apiDistrictIdLong = `${stateName}-${districtNum}`;
      
      const prediction = predictions.find(p => p.district === apiDistrictIdShort || p.district === apiDistrictIdLong);

      let color = '#CBD5E1';
      if (prediction) {
        color = prediction.predicted_winner === 'Democrat' ? '#3B82F6' : '#EF4444';
      }

      return { fillColor: color, weight: 1, opacity: 1, color: '#ffffff', fillOpacity: 0.8 };
    };

    geoJsonLayerRef.current = L.geoJSON(geoData, {
      style: getStyle,
      onEachFeature: (feature, layer) => {
        layer.on({
          mouseover: (e) => {
            const stateName = fipsToState[feature.properties.STATEFP];
            if (!stateName) return;
            const stateCode = getStateCodeFromName(stateName);

            e.target.setStyle({ fillOpacity: 1, weight: 3, color: '#1e293b' });
            e.target.bringToFront();
            
            const stateData = predictions.filter(p => p.state === stateCode || p.state === stateName);
            
            setHoveredState({
              name: stateName,
              code: stateCode,
              districts: stateData
            });
          },
          mouseout: (e) => {
            if (geoJsonLayerRef.current) {
              geoJsonLayerRef.current.resetStyle(e.target);
            }
            setHoveredState(null);
          },
          click: () => {
            const stateName = fipsToState[feature.properties.STATEFP];
            if (!stateName) return;
            const stateCode = getStateCodeFromName(stateName);
            
            let districtNum = feature.properties.CD119FP;
            if (districtNum === '00') districtNum = 'AL';
            const districtId = `${stateCode}-${districtNum}`;
            
            window.open(`/district/${districtId}`, '_blank');
          }
        });
      }
    }).addTo(mapInstanceRef.current);

    setTimeout(() => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.invalidateSize();
      }
    }, 100);

  }, [geoData, predictions]);

  if (loading) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-slate-50 rounded-[32px]">
        <div className="flex flex-col items-center gap-3">
          <svg className="animate-spin w-8 h-8 text-slate-400" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="text-sm font-medium text-slate-500">Loading map data...</span>
        </div>
      </div>
    );
  }

  const totalProcessed = (summary.democrat_projections || 0) + (summary.republican_projections || 0);
  const demWidth = totalProcessed > 0 ? ((summary.democrat_projections / totalProcessed) * 100) : 50;
  const repWidth = totalProcessed > 0 ? ((summary.republican_projections / totalProcessed) * 100) : 50;

  return (
    <div className="flex flex-col h-full w-full">
      <header className="mb-6 bg-white rounded-[24px] p-5 shadow-sm border border-slate-200 flex items-center justify-between">
        <div className="flex items-center gap-4 w-2/3">
          <div className="text-center w-24">
            <p className="text-[10px] font-bold text-blue-600 uppercase tracking-wider">Democrats</p>
            <p className="text-3xl font-black text-blue-700 leading-none mt-1">{summary.democrat_projections || 0}</p>
          </div>
          <div className="flex-1 h-4 bg-slate-100 rounded-full overflow-hidden flex shadow-inner">
            <div style={{ width: `${demWidth}%` }} className="bg-blue-500 h-full transition-all duration-1000" />
            <div style={{ width: `${repWidth}%` }} className="bg-red-500 h-full transition-all duration-1000" />
          </div>
          <div className="text-center w-24">
            <p className="text-[10px] font-bold text-red-600 uppercase tracking-wider">Republicans</p>
            <p className="text-3xl font-black text-red-700 leading-none mt-1">{summary.republican_projections || 0}</p>
          </div>
        </div>
        <h1 className="text-2xl font-black text-slate-800 tracking-tight">2024 Election Forecast</h1>
      </header>

      <div className="flex flex-1 gap-6 overflow-hidden">
        <div className="flex-[3] bg-white rounded-[32px] border border-slate-200 shadow-inner relative overflow-hidden min-h-[500px]">
          <div ref={mapContainerRef} className="absolute inset-0 w-full h-full z-10" />
        </div>

        <aside className="flex-1 bg-slate-900 rounded-[32px] p-8 text-white shadow-xl flex flex-col overflow-y-auto">
          {hoveredState ? (
            <div className="animate-in fade-in slide-in-from-right-4 duration-300 h-full flex flex-col">
              <div className="mb-8">
                <h2 className="text-4xl font-black tracking-tight mb-2">{hoveredState.name}</h2>
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800 border border-slate-700">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  <span className="text-xs font-medium text-slate-300">Live Forecast Active</span>
                </div>
              </div>
              
              <div className="space-y-8 flex-1">
                <div className="bg-slate-800/80 rounded-[24px] p-6 border border-slate-700 shadow-inner">
                  <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-4">District Breakdown</h3>
                  <div className="flex justify-between items-end">
                    <div>
                      <p className="text-4xl font-black text-blue-500">
                        {hoveredState.districts.filter(d => d.predicted_winner === 'Democrat').length}
                      </p>
                      <p className="text-xs font-bold text-slate-400 tracking-wider mt-1">DEM SEATS</p>
                    </div>
                    <div className="text-right">
                      <p className="text-4xl font-black text-red-500">
                        {hoveredState.districts.filter(d => d.predicted_winner === 'Republican').length}
                      </p>
                      <p className="text-xs font-bold text-slate-400 tracking-wider mt-1">REP SEATS</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-center text-slate-500 px-6">
              <div className="w-16 h-16 mb-6 rounded-2xl bg-slate-800/50 border border-slate-700 flex items-center justify-center">
                <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path>
                </svg>
              </div>
              <p className="text-lg font-medium text-slate-300 mb-2">Explore the Map</p>
              <p className="text-sm text-slate-500">Hover over any district to view its live 2024 forecast.</p>
              <p className="text-xs text-slate-600 mt-3">Click on any district to open detailed analysis in new tab</p>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}