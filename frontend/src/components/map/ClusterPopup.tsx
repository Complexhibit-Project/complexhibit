"use client";

import { useState, useMemo } from "react";
import { X, MapPin, Calendar, Building2, User, Palette, ZoomIn, ChevronRight, Search } from "lucide-react";
import Link from "next/link";
import { buildDetailHref } from "@/lib/entity-routing";

interface ClusterEntity {
  id: string;
  uri: string;
  type: string;
  label: string;
  lat: number;
  long: number;
  date_start?: string;
  date_end?: string;
}

interface ClusterPopupProps {
  /** Entities in the cluster */
  entities: ClusterEntity[];
  /** Callback to close the popup */
  onClose: () => void;
  /** Callback to zoom into the cluster */
  onZoomIn: () => void;
  /** Coordinates of the cluster center */
  coordinates: [number, number];
}

const typeColors: Record<string, string> = {
  exhibition: '#6366f1',
  institution: '#10b981',
  person: '#f59e0b',
  artwork: '#ec4899',
};

const typeIcons: Record<string, React.ElementType> = {
  exhibition: Calendar,
  institution: Building2,
  person: User,
  artwork: Palette,
};

const typeLabels: Record<string, string> = {
  exhibition: 'Exhibitions',
  institution: 'Institutions',
  person: 'Persons',
  artwork: 'Artworks',
};

/**
 * Popup component showing entities grouped by type when clicking a map cluster.
 * Features search functionality for filtering large clusters.
 */
export function ClusterPopup({ entities, onClose, onZoomIn }: ClusterPopupProps) {
  const [searchQuery, setSearchQuery] = useState("");

  // Filter entities based on search query
  const filteredEntities = useMemo(() => {
    if (!searchQuery.trim()) return entities;
    const query = searchQuery.toLowerCase();
    return entities.filter(entity => 
      entity.label?.toLowerCase().includes(query) ||
      entity.type?.toLowerCase().includes(query)
    );
  }, [entities, searchQuery]);

  // Group filtered entities by type
  const grouped = useMemo(() => {
    return filteredEntities.reduce((acc, entity) => {
      if (!acc[entity.type]) {
        acc[entity.type] = [];
      }
      acc[entity.type].push(entity);
      return acc;
    }, {} as Record<string, ClusterEntity[]>);
  }, [filteredEntities]);

  const getDetailUrl = (entity: ClusterEntity) => {
    const cleanId = entity.id.replace(/_(residence|birth)$/, '');
    const type = entity.type === 'person' ? 'actant' : entity.type;
    return buildDetailHref(type, cleanId);
  };

  const totalCount = entities.length;
  const filteredCount = filteredEntities.length;
  const typeCount = Object.keys(grouped).length;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-2xl shadow-2xl border border-gray-100 w-full max-w-md max-h-[85vh] overflow-hidden animate-in zoom-in-95 duration-200 flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4 text-white flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-white/20 rounded-lg">
                <MapPin className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-bold text-lg">Cluster Contents</h3>
                <p className="text-sm text-white/80">
                  {totalCount} entities • {Object.keys(typeColors).filter(t => entities.some(e => e.type === t)).length} types
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors cursor-pointer"
              aria-label="Close popup"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Search Input */}
        <div className="px-4 py-3 border-b border-gray-100 bg-gray-50 flex-shrink-0">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search entities..."
              className="w-full pl-10 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white"
            />
          </div>
          {searchQuery && (
            <p className="mt-2 text-xs text-gray-500">
              Showing {filteredCount} of {totalCount} entities
            </p>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto min-h-0">
          {typeCount === 0 ? (
            <div className="px-6 py-8 text-center text-gray-500">
              <p>No entities match your search.</p>
            </div>
          ) : (
            Object.entries(grouped).map(([type, typeEntities]) => {
              const Icon = typeIcons[type] || MapPin;
              const color = typeColors[type] || '#6b7280';
              const label = typeLabels[type] || type;

              return (
                <div key={type} className="border-b border-gray-100 last:border-0">
                  {/* Type Header */}
                  <div 
                    className="px-4 py-3 bg-gray-50 flex items-center gap-3 sticky top-0 z-10"
                    style={{ borderLeft: `4px solid ${color}` }}
                  >
                    <div className="p-1.5 rounded-md" style={{ backgroundColor: `${color}20` }}>
                      <Icon className="h-4 w-4" style={{ color }} />
                    </div>
                    <span className="font-semibold text-gray-700">{label}</span>
                    <span 
                      className="ml-auto text-xs font-bold px-2 py-0.5 rounded-full text-white"
                      style={{ backgroundColor: color }}
                    >
                      {typeEntities.length}
                    </span>
                  </div>

                  {/* Entity List - show all, scroll for navigation */}
                  <div className="divide-y divide-gray-50 max-h-60 overflow-y-auto">
                    {typeEntities.map((entity) => (
                      <Link
                        key={entity.id}
                        href={getDetailUrl(entity)}
                        className="px-4 py-3 flex items-center gap-3 hover:bg-indigo-50 transition-colors group cursor-pointer"
                      >
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate group-hover:text-indigo-600 transition-colors">
                            {entity.label || 'Untitled'}
                          </p>
                          {entity.date_start && (
                            <p className="text-xs text-gray-500 mt-0.5">
                              {entity.date_start}{entity.date_end ? ` — ${entity.date_end}` : ''}
                            </p>
                          )}
                        </div>
                        <ChevronRight className="h-4 w-4 text-gray-400 group-hover:text-indigo-600 transition-colors flex-shrink-0" />
                      </Link>
                    ))}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-100 flex gap-3 flex-shrink-0">
          <button
            onClick={onZoomIn}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium text-sm cursor-pointer"
          >
            <ZoomIn className="h-4 w-4" />
            Zoom In
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2.5 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium text-sm cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default ClusterPopup;
