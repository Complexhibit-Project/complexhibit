'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { ArrowLeft, Filter, MapPin, Calendar, Building2, User, X, Palette, Loader2 } from 'lucide-react';

const Map = dynamic(() => import('@/components/ui/map').then(mod => mod.Map), { 
  ssr: false,
  loading: () => <div className="h-full w-full bg-slate-50 flex items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-indigo-600" /></div>
});
const MapClusterLayer = dynamic(() => import('@/components/ui/map').then(mod => mod.MapClusterLayer), { ssr: false });
const MapPopup = dynamic(() => import('@/components/ui/map').then(mod => mod.MapPopup), { ssr: false });
const MapControls = dynamic(() => import('@/components/ui/map').then(mod => mod.MapControls), { ssr: false });
import { getMapEntities, getMapMeta } from '@/lib/api';
import DateRangeSlider from '@/components/ui/slider';
import useDebounce from '@/hooks/useDebounce';
import { ClusterPopup } from '@/components/map/ClusterPopup';
import { buildDetailHref } from '@/lib/entity-routing';

interface MapEntity {
  id: string;
  uri: string;
  type: string;
  label: string;
  lat: number;
  long: number;
  date_start?: string;
  date_end?: string;
  // Pre-calculated years for fast filtering
  startYear?: number;
  endYear?: number;
}

interface GeoJsonFeature {
  type: 'Feature';
  geometry: {
    type: 'Point';
    coordinates: [number, number];
  };
  properties: MapEntity;
}

interface GeoJsonCollection {
  type: 'FeatureCollection';
  features: GeoJsonFeature[];
}

const typeColors: Record<string, string> = {
  exhibition: '#6366f1', // indigo
  institution: '#10b981', // emerald
  person: '#f59e0b', // amber
  artwork: '#ec4899', // pink
};

const typeIcons: Record<string, typeof MapPin> = {
  exhibition: Calendar,
  institution: Building2,
  person: User,
  artwork: Palette,
};

export default function MapPage() {
  const [entities, setEntities] = useState<MapEntity[]>([]);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [showFilters, setShowFilters] = useState(true);
  const [selectedTypes, setSelectedTypes] = useState<Set<string>>(new Set());
  const [loadedTypes, setLoadedTypes] = useState<Set<string>>(new Set([]));
  const [isFetching, setIsFetching] = useState(false);
  
  // Date State
  const [minYear, setMinYear] = useState<number>(1900);
  const [maxYear, setMaxYear] = useState<number>(new Date().getFullYear());
  const [sliderRange, setSliderRange] = useState<[number, number]>([1900, new Date().getFullYear()]);
  
  // Debounce the slider value to prevent heavy recalculations during drag
  const debouncedRange = useDebounce(sliderRange, 300);

  // Popup state
  const [selectedEntity, setSelectedEntity] = useState<MapEntity | null>(null);

  // Cluster popup state
  const [clusterEntities, setClusterEntities] = useState<MapEntity[]>([]);
  const [clusterCoords, setClusterCoords] = useState<[number, number] | null>(null);
  // Pending zoom state removed as it was unused

  // Initial Data Load
  useEffect(() => {
    const init = async () => {
      setIsFetching(true);
      try {
        // 1. Get Metadata
        const meta = await getMapMeta();
        if (meta.min_year && meta.max_year) {
           setMinYear(meta.min_year);
           setMaxYear(meta.max_year);
           setSliderRange([meta.min_year, meta.max_year]);
        }

        // Don't load entities initially - lazy load when user selects types
        // This saves bandwidth especially on mobile devices

      } catch (e) {
        console.error("Failed to init map", e);
        setError("Failed to load map data");
      } finally {
        setIsFetching(false);
      }
    };
    init();
  }, []);

  const toggleType = (type: string) => {
    const newTypes = new Set(selectedTypes);
    if (newTypes.has(type)) {
      newTypes.delete(type);
    } else {
      newTypes.add(type);
    }
    setSelectedTypes(newTypes);
  };

  // Lazy load entities when types are selected
  useEffect(() => {
    const typesToLoad = Array.from(selectedTypes).filter(t => !loadedTypes.has(t));
    if (typesToLoad.length === 0) return;

    const loadTypes = async () => {
      setIsFetching(true);
      try {
        const res = await getMapEntities(typesToLoad);
        const rawEntities = res.data || [];
        
        // Pre-process entities for performance
        const processed = rawEntities.map((e: MapEntity) => {
          let startYear = e.date_start ? parseInt(e.date_start.substring(0, 4)) : undefined;
          let endYear = e.date_end ? parseInt(e.date_end.substring(0, 4)) : undefined;

          // Fallbacks
          if (endYear === undefined && startYear !== undefined) endYear = startYear;
          if (startYear === undefined && endYear !== undefined) startYear = endYear;

          return {
            ...e,
            startYear,
            endYear
          };
        });

        setEntities(prev => [...prev, ...processed]);
        setLoadedTypes(prev => {
          const newLoaded = new Set(prev);
          typesToLoad.forEach(t => newLoaded.add(t));
          return newLoaded;
        });
      } catch (e) {
        console.error("Failed to load entity types", e);
      } finally {
        setIsFetching(false);
      }
    };

    loadTypes();
  }, [selectedTypes, loadedTypes]);
    
  // Filter entities - Optimized
  const filteredEntities = useMemo(() => {
    const [from, to] = debouncedRange;
    
    return entities.filter(entity => {
      // 1. Type filter (fastest check)
      if (!selectedTypes.has(entity.type)) return false;
      
      // 2. Date filter (numeric comparison)
      // Entities without dates are currently excluded if they don't match the range? 
      // User requirement: "barrita supongo que tendrá que tener como fecha mínima la fecha mínima que tengamos registrada"
      // Usually, if an entity has NO dates, it shouldn't show up when filtering by date, OR it should always show.
      // Let's decided: If it has valid years, check range. If no years, SHOW IT? Or HIDE IT?
      // Hiding it makes the most sense for a "time filter".
      
      if (entity.startYear === undefined && entity.endYear === undefined) {
         // Always show entities without dates - they're not time-bound
         return true; 
      }
      
      // Overlap logic:
      // Entity Interval: [start, end]
      // Filter Interval: [from, to]
      // Overlap if: start <= to AND end >= from
      
      // Safe check because TS doesn't know we checked undefined above (mostly)
      const s = entity.startYear || 0;
      const e = entity.endYear || s;

      return s <= to && e >= from;
    });
  }, [entities, selectedTypes, debouncedRange]);

  // Convert to GeoJSON - Memoized
  const geoJsonData: GeoJsonCollection = useMemo(() => ({
    type: 'FeatureCollection',
    features: filteredEntities.map(entity => ({
      type: 'Feature' as const,
      geometry: {
        type: 'Point' as const,
        coordinates: [entity.long, entity.lat] as [number, number],
      },
      properties: entity,
    })),
  }), [filteredEntities]);

  const handlePointClick = useCallback((
    feature: GeoJSON.Feature<GeoJSON.Point, Record<string, unknown> | null>
  ) => {
    setSelectedEntity(feature.properties as unknown as MapEntity);
    // Close cluster popup when clicking individual point
    setClusterEntities([]);
    setClusterCoords(null);
  }, []);

  // Handle cluster click to show popup with grouped entities
  const handleClusterClick = useCallback(async (
    clusterId: number,
    coordinates: [number, number],
    pointCount: number,
    getLeaves: (limit?: number) => Promise<GeoJSON.Feature<GeoJSON.Point>[]>
  ) => {
    // Use MapLibre's getClusterLeaves to get actual entities in the cluster
    try {
      const leaves = await getLeaves(Math.min(pointCount, 500));
      
      // Convert GeoJSON features to MapEntity format
      const clusterItems: MapEntity[] = leaves.map(feature => ({
        ...feature.properties,
        lat: feature.geometry.coordinates[1],
        long: feature.geometry.coordinates[0],
      })) as MapEntity[];

      if (clusterItems.length > 0) {
        setClusterEntities(clusterItems);
        setClusterCoords(coordinates);
        // Clear single entity popup
        setSelectedEntity(null);
      }
    } catch (err) {
      console.error('Failed to get cluster leaves:', err);
    }
  }, []);

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      exhibition: 'Exhibitions',
      institution: 'Institutions',
      person: 'Persons',
      artwork: 'Artworks',
    };
    return labels[type] || type;
  };

  const getDetailUrl = (entity: MapEntity) => {
    const cleanId = entity.id.replace(/_(residence|birth)$/, '');
    const type = entity.type === 'person' ? 'actant' : entity.type;
    return buildDetailHref(type, cleanId);
  };

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center p-8 bg-white rounded-xl shadow-lg border border-red-100 max-w-md">
           <div className="text-red-500 mb-4 flex justify-center"><X className="h-12 w-12" /></div>
          <h3 className="text-lg font-bold text-gray-900 mb-2">Something went wrong</h3>
          <p className="text-gray-600 mb-6">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Reload Page
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="relative h-[calc(100vh-64px)] w-full overflow-hidden bg-slate-50">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-20 bg-white/90 backdrop-blur-md border-b border-gray-200 px-6 py-4 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="text-gray-600 hover:text-indigo-600 flex items-center gap-1 transition-colors">
              <ArrowLeft className="h-4 w-4" /> <span className="font-medium">Home</span>
            </Link>
            <div className="h-6 w-px bg-gray-300 mx-2 hidden sm:block"></div>
            <h1 className="text-xl font-bold text-gray-900 hidden sm:block">Explore the Map</h1>
          </div>
          
          <div className="flex items-center gap-4">
             {!isFetching && (
                <div className="hidden sm:flex items-center gap-2 text-sm font-medium text-gray-600 bg-white/50 px-3 py-1.5 rounded-full border border-gray-200/50 backdrop-blur-sm shadow-sm transition-all animate-in fade-in zoom-in duration-300">
                  <span className="font-bold text-indigo-600">{filteredEntities.length}</span> entities loaded
                </div>
             )}
            
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 font-medium text-sm shadow-sm ${
                showFilters 
                  ? 'bg-indigo-600 text-white shadow-indigo-200 hover:bg-indigo-700' 
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              <Filter className="h-4 w-4" />
              {showFilters ? 'Hide Filters' : 'Filters'}
            </button>
          </div>
        </div>
      </div>

      {/* Filter Panel */}
      <div className={`absolute top-20 right-6 z-20 w-80 transition-all duration-300 ease-in-out transform ${showFilters ? 'translate-x-0 opacity-100' : 'translate-x-[120%] opacity-0'}`}>
        <div className="bg-white/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-bold text-gray-900 flex items-center gap-2">
                <Filter className="h-4 w-4 text-indigo-500" />
                Refine View
            </h3>
            <button onClick={() => setShowFilters(false)} className="text-gray-400 hover:text-gray-600 transition-colors p-1 hover:bg-gray-100 rounded-full">
              <X className="h-4 w-4" />
            </button>
          </div>
          
          {/* Type filters */}
          <div className="mb-8">
            <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Entity Types</h4>
            <div className="space-y-2.5">
              {['exhibition', 'institution', 'person', 'artwork'].map(type => {
                const Icon = typeIcons[type] || MapPin;
                const isSelected = selectedTypes.has(type);
                const color = typeColors[type];
                
                return (
                  <label 
                    key={type} 
                    className={`flex items-center gap-3 p-2.5 rounded-lg cursor-pointer transition-all duration-200 border ${
                        isSelected 
                          ? 'bg-indigo-50/50 border-indigo-200 shadow-sm' 
                          : 'bg-gray-50/50 border-gray-200 hover:bg-gray-100 hover:border-gray-300'
                    }`}
                  >
                    <div className="relative flex items-center justify-center">
                        <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleType(type)}
                        className="peer appearance-none h-4 w-4 rounded border-2 border-gray-300 bg-white checked:bg-indigo-600 checked:border-indigo-600 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1 transition-colors"
                        />
                        <div className="pointer-events-none absolute inset-0 flex items-center justify-center text-white opacity-0 peer-checked:opacity-100">
                             <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4"><path d="M20 6L9 17l-5-5"></path></svg>
                        </div>
                    </div>
                    
                    <div className="p-1.5 rounded-md" style={{ backgroundColor: `${color}20` }}>
                        <Icon className="h-4 w-4" style={{ color: color }} />
                    </div>
                    <span className={`text-sm font-medium ${isSelected ? 'text-gray-900' : 'text-gray-600'}`}>
                        {getTypeLabel(type)}
                    </span>
                  </label>
                );
              })}
            </div>
          </div>
          
          {/* Date Range Slider */}
          <div>
            <div className="flex items-center justify-between mb-4">
                 <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Time Period</h4>
                 <div className="text-xs font-medium text-indigo-600 bg-indigo-50 px-2 py-1 rounded">
                    {debouncedRange[0]} — {debouncedRange[1]}
                 </div>
            </div>
            
            <div className="px-1 pb-2">
                <DateRangeSlider
                    min={minYear}
                    max={maxYear}
                    value={sliderRange}
                    onChange={setSliderRange}
                />
            </div>
            <div className="flex justify-between text-[10px] text-gray-400 font-medium mt-1">
                <span>{minYear}</span>
                <span>{maxYear}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Map */}
      <div className="h-full w-full pt-0">
        <Map
          center={[40, -3]} // Centered roughly on Europe/Spain as per user context
          zoom={3}
          minZoom={2}
          maxZoom={18}
        >
          <MapControls 
            position="bottom-right" 
            showZoom 
            showLocate
            showFullscreen
          />
          
          {geoJsonData.features.length > 0 && (
            <MapClusterLayer
              data={geoJsonData}
              clusterMaxZoom={14}
              clusterRadius={50}
              clusterColors={(() => {
                // If only one type selected, use its color. Else default purple.
                if (selectedTypes.size === 1) {
                  const type = Array.from(selectedTypes)[0];
                  const color = typeColors[type];
                  return [color, color, color] as [string, string, string];
                }
                return ['#9ca3af', '#6b7280', '#4b5563']; // Neutral gray gradient for mixed types
              })()}
              clusterThresholds={[10, 50]}
              pointColor={[
                'match',
                ['get', 'type'],
                'exhibition', '#6366f1',
                'institution', '#10b981',
                'person', '#f59e0b',
                'artwork', '#ec4899',
                '#6b7280'
              ] as unknown as string}
              onPointClick={handlePointClick}
              onClusterClick={handleClusterClick}
            />
          )}

          {/* Popup for selected entity */}
          {selectedEntity && (
            <MapPopup
              longitude={selectedEntity.long}
              latitude={selectedEntity.lat}
              onClose={() => setSelectedEntity(null)}
              closeButton
            >
              <div className="min-w-[220px] p-1">
                <div className="flex items-center gap-2 mb-3">
                  <span 
                    className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide rounded-full text-white shadow-sm"
                    style={{ backgroundColor: typeColors[selectedEntity.type] || '#6b7280' }}
                  >
                    {selectedEntity.type}
                  </span>
                </div>
                <h3 className="font-bold text-gray-900 text-sm leading-tight mb-2 line-clamp-2">{selectedEntity.label}</h3>
                
                {(selectedEntity.date_start || selectedEntity.date_end) && (
                  <div className="flex items-center gap-2 text-xs text-gray-500 mb-3 bg-gray-50 p-2 rounded-lg border border-gray-100">
                    <Calendar className="h-3 w-3" />
                    <span>
                      {selectedEntity.date_start || '?'} 
                      <span className="mx-1 text-gray-300">➜</span> 
                      {selectedEntity.date_end || 'Present'}
                    </span>
                  </div>
                )}
                
                <Link
                  href={getDetailUrl(selectedEntity)}
                  className="block w-full text-center bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold py-2 rounded-lg transition-colors"
                >
                  View Details
                </Link>
              </div>
            </MapPopup>
          )}
        </Map>
      </div>

      {/* Central Loading Overlay */}
      {isFetching && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-white/40 backdrop-blur-sm transition-all duration-300 animate-in fade-in">
          <div className="bg-white/90 px-6 py-4 rounded-2xl shadow-xl border border-white/50 flex flex-col items-center gap-3 animate-bounce-slight">
            <div className="relative">
              <div className="h-12 w-12 rounded-full border-4 border-indigo-100 border-t-indigo-600 animate-spin"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="h-2 w-2 bg-indigo-600 rounded-full animate-pulse"></div>
              </div>
            </div>
            <div className="flex flex-col items-center">
              <span className="text-sm font-bold text-gray-800">Loading Map Data</span>
              <span className="text-xs text-gray-500">Fetching entities...</span>
            </div>
          </div>
        </div>
      )}

      {/* Legend - Floating Bottom Left */}
      <div className="absolute bottom-6 left-6 z-10 bg-white/95 backdrop-blur-md rounded-xl shadow-lg border border-gray-100 p-4 transition-opacity hover:opacity-100 opacity-90 hidden sm:block">
        <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Legend</h4>
        <div className="space-y-2">
          {Object.entries(typeColors).map(([type, color]) => {
            return (
              <div key={type} className="flex items-center gap-2.5">
                <span 
                  className="w-2.5 h-2.5 rounded-full shadow-sm ring-1 ring-white"
                  style={{ backgroundColor: color }}
                />
                <span className="text-xs font-medium text-gray-600 capitalize">{type}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Cluster Popup */}
      {clusterEntities.length > 0 && clusterCoords && (
        <ClusterPopup
          entities={clusterEntities}
          coordinates={clusterCoords}
          onClose={() => {
            setClusterEntities([]);
            setClusterCoords(null);
          }}
          onZoomIn={() => {
            // Close popup and zoom to location
            setClusterEntities([]);
            setClusterCoords(null);
            // The map will zoom in via default behavior when clicking cluster again
          }}
        />
      )}
    </div>
  );
}
