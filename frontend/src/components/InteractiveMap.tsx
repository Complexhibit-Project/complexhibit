'use client';

import { useEffect, useRef } from 'react';
import { MapPin, ExternalLink } from 'lucide-react';

interface InteractiveMapProps {
  lat: number;
  long: number;
  label?: string;
}

interface MapInstance {
  remove: () => void;
}

export default function InteractiveMap({ lat, long, label }: InteractiveMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<MapInstance | null>(null);

  useEffect(() => {
    // Dynamically import Leaflet to avoid SSR issues
    const loadMap = async () => {
      if (!mapRef.current || mapInstanceRef.current) return;

      const L = (await import('leaflet')).default;
      
      // Inject Leaflet CSS via link element
      if (!document.querySelector('link[href*="leaflet"]')) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
        document.head.appendChild(link);
      }

      // Fix for default marker icon issue in webpack
      delete (L.Icon.Default.prototype as unknown as { _getIconUrl: unknown })._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
        iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
      });

      // Create map
      const map = L.map(mapRef.current).setView([lat, long], 15);
      mapInstanceRef.current = map;

      // Add tile layer (OpenStreetMap)
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(map);

      // Add marker
      const marker = L.marker([lat, long]).addTo(map);
      if (label) {
        marker.bindPopup(`<b>${label}</b>`).openPopup();
      }
    };

    loadMap();

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [lat, long, label]);

  const googleMapsUrl = `https://www.google.com/maps/search/?api=1&query=${lat},${long}`;

  return (
    <div className="space-y-3">
      {/* Interactive Map */}
      <div 
        ref={mapRef} 
        className="h-64 w-full rounded-lg overflow-hidden border border-gray-200 shadow-sm z-0"
        style={{ minHeight: '256px' }}
      />
      
      {/* Coordinates and Google Maps Link */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-gray-50 p-3 rounded-lg">
        <div className="flex items-center gap-4 text-sm font-mono text-gray-700">
          <span className="flex items-center gap-1">
            <MapPin className="h-4 w-4 text-indigo-500" />
            <span title="Latitude">{lat.toFixed(6)}</span>
          </span>
          <span title="Longitude">{long.toFixed(6)}</span>
        </div>
        <a 
          href={googleMapsUrl} 
          target="_blank" 
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors shadow-sm"
        >
          <ExternalLink className="h-4 w-4" />
          View on Google Maps
        </a>
      </div>
    </div>
  );
}
