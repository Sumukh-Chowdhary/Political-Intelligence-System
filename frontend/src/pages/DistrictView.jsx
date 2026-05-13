import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import api from '../api/client';

const stateToFips = {
  'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06', 
  'CO': '08', 'CT': '09', 'DE': '10', 'FL': '12', 'GA': '13',
  'HI': '15', 'ID': '16', 'IL': '17', 'IN': '18', 'IA': '19', 
  'KS': '20', 'KY': '21', 'LA': '22', 'ME': '23', 'MD': '24',
  'MA': '25', 'MI': '26', 'MN': '27', 'MS': '28', 'MO': '29', 
  'MT': '30', 'NE': '31', 'NV': '32', 'NH': '33', 'NJ': '34',
  'NM': '35', 'NY': '36', 'NC': '37', 'ND': '38', 'OH': '39', 
  'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44', 'SC': '45',
  'SD': '46', 'TN': '47', 'TX': '48', 'UT': '49', 'VT': '50',
  'VA': '51', 'WA': '53', 'WV': '54', 'WI': '55', 'WY': '56'
};

export default function DistrictView() {
  const { stateCode } = useParams();
  const navigate = useNavigate();
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const geoJsonLayerRef = useRef(null);

  const [predictions, setPredictions] = useState([]);
  const [activeDistrict, setActiveDistrict] = useState(null);
  const [loading, setLoading] = useState(true);
  const [districtMapData, setDistrictMapData] = useState(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;
    if (mapContainerRef.current._leaflet_id) {
      mapContainerRef.current._leaflet_id = null;
    }

    mapInstanceRef.current = L.map(mapContainerRef.current, {
      center: [39.0, -96.0],
      zoom: 4,
      zoomControl: false
    });

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
        const [mapRes, predRes] = await Promise.all([
          fetch('/us_districts.json'),
          api.get(`/api/v1/predictions?state=${stateCode}&limit=500`).catch(() => ({ data: { data: [] } }))
        ]);

        if (!isMounted) return;

        const fullMapData = await mapRes.json();
        const targetFips = stateToFips[stateCode];

        const filteredFeatures = fullMapData.features.filter(
          feature => feature.properties.STATEFP === targetFips
        );

        setDistrictMapData({
          type: "FeatureCollection",
          features: filteredFeatures
        });

        setPredictions(predRes.data?.data || []);
      } catch (err) {
        console.error("Error loading district data:", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    if (stateCode && stateToFips[stateCode]) {
      loadData();
    }
    return () => { isMounted = false; };
  }, [stateCode]);

  useEffect(() => {
    if (!mapInstanceRef.current || !districtMapData || districtMapData.features.length === 0) return;

    if (geoJsonLayerRef.current) {
      mapInstanceRef.current.removeLayer(geoJsonLayerRef.current);
    }

    const getDistrictStyle = (feature) => {
      let districtNum = feature.properties.CD119FP;
      if (!districtNum) return { fillColor: '#CBD5E1', weight: 1, color: '#ffffff', fillOpacity: 0.8 };
      
      const formattedNum = districtNum === '00' ? 'AL' : districtNum;
      const apiDistrictId = `${stateCode}-${formattedNum}`;
      
      const prediction = predictions.find(p => p.district === apiDistrictId);
      
      let color = '#CBD5E1';
      if (prediction) {
        color = prediction.predicted_winner === 'Democrat' ? '#3B82F6' : '#EF4444';
      }

      return { fillColor: color, weight: 1, color: '#ffffff', fillOpacity: 0.9 };
    };

    geoJsonLayerRef.current = L.geoJSON(districtMapData, {
      style: getDistrictStyle,
      onEachFeature: (feature, layer) => {
        layer.on({
          mouseover: (e) => {
            e.target.setStyle({ weight: 3, fillOpacity: 1, color: '#1e293b' });
            e.target.bringToFront();
            const districtNum = feature.properties.CD119FP;
            if (districtNum) {
                setActiveDistrict(`${stateCode}-${districtNum === '00' ? 'AL' : districtNum}`);
            }
          },
          mouseout: (e) => {
            if (geoJsonLayerRef.current) geoJsonLayerRef.current.resetStyle(e.target);
          }
        });
      }
    }).addTo(mapInstanceRef.current);

    // Safely zoom to the state
    if (geoJsonLayerRef.current.getBounds().isValid()) {
      mapInstanceRef.current.fitBounds(geoJsonLayerRef.current.getBounds(), { padding: [30, 30] });
    }

    setTimeout(() => {
      if (mapInstanceRef.current) mapInstanceRef.current.invalidateSize();
    }, 100);

  }, [districtMapData, predictions, stateCode]);

  if (loading) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-slate-50 rounded-[32px]">
        <svg className="animate-spin w-8 h-8 text-slate-400 mr-3" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span className="text-sm font-medium text-slate-500">Loading district map...</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full w-full gap-4">
      <div className="flex items-center gap-4">
        <button 
          onClick={() => navigate('/map')} 
          className="px-5 py-2.5 bg-white border border-slate-200 rounded-xl shadow-sm hover:bg-slate-50 font-semibold text-slate-600 transition-colors"
        >
          &larr; Back to National Map
        </button>
        <h1 className="text-2xl font-black text-slate-800">{stateCode} Congressional Districts</h1>
      </div>

      <div className="flex flex-1 gap-6 overflow-hidden">
        <div className="flex-[3] bg-[#E2E8F0] rounded-[32px] shadow-inner overflow-hidden relative border border-slate-200 min-h-[500px]">
           <div ref={mapContainerRef} className="absolute inset-0 w-full h-full z-10" />
        </div>

        <aside className="flex-[1] bg-slate-900 rounded-[32px] p-8 text-white shadow-xl flex flex-col border border-slate-800">
           <h2 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-6 border-b border-slate-700 pb-4">District Details</h2>
           {activeDistrict ? (
               <div className="animate-in fade-in slide-in-from-right-4 duration-300">
                   <p className="text-5xl font-black tracking-tight mb-8">{activeDistrict}</p>
                   
                   {(() => {
                       const detail = predictions.find(p => p.district === activeDistrict);
                       if (detail) {
                           return (
                               <div className="p-6 rounded-[24px] bg-slate-800/80 border border-slate-700 shadow-inner">
                                   <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Predicted Winner</p>
                                   <p className={`text-3xl font-black ${detail.predicted_winner === 'Democrat' ? 'text-blue-400' : 'text-red-400'}`}>
                                       {detail.predicted_winner}
                                   </p>
                                   
                                   <div className="mt-6 pt-6 border-t border-slate-700">
                                      <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Win Probability</p>
                                      <div className="flex items-center gap-3">
                                        <div className="flex-1 h-3 bg-slate-900 rounded-full overflow-hidden border border-slate-700">
                                          <div 
                                            className={`h-full ${detail.predicted_winner === 'Democrat' ? 'bg-blue-500' : 'bg-red-500'}`} 
                                            style={{ width: `${(detail.win_probability * 100)}%` }}
                                          />
                                        </div>
                                        <span className="text-lg font-bold text-white">
                                          {(detail.win_probability * 100).toFixed(1)}%
                                        </span>
                                      </div>
                                   </div>
                               </div>
                           )
                       }
                       return <p className="text-slate-400 italic">No prediction data available for this district.</p>;
                   })()}
               </div>
           ) : (
             <div className="h-full flex flex-col items-center justify-center text-center text-slate-500">
                <div className="w-16 h-16 mb-6 rounded-2xl bg-slate-800/50 border border-slate-700 flex items-center justify-center shadow-inner">
                  <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122"></path>
                  </svg>
                </div>
               <p className="text-lg font-medium text-slate-300 mb-2">Select a District</p>
               <p className="text-sm">Hover over any district on the map to see its specific polling and forecast data.</p>
             </div>
           )}
        </aside>
      </div>
    </div>
  );
}