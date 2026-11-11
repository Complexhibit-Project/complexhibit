"use client";

import Link from "next/link";
import Image from "next/image";
import { ArrowRight, ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";
import { buildDetailHref } from "@/lib/entity-routing";


interface ItemCardProps {
  uri: string;
  label: string;
  description?: string;
  type: string;
  imageUrl?: string;
  subtitle?: string;
  extra?: Record<string, unknown>;
  icon?: React.ElementType;
  color?: string;
}

// Client component wrapper for the expandable part
function ExpandableExtra({ extra }: { extra: Record<string, unknown> }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const MAX_VISIBLE_TAGS = 3;
  
  // Check if there's any content to show
  const hasContent = Object.entries(extra).some(([, v]) => 
    v && (!Array.isArray(v) || (v as unknown[]).length > 0)
  );
  
  if (!hasContent) return null;
  
  return (
    <div className="mt-auto pt-4 border-t border-gray-100">
      {!isExpanded ? (
        <button
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setIsExpanded(true);
          }}
          className="flex items-center gap-1 text-indigo-600 hover:text-indigo-800 font-medium text-xs transition-colors"
        >
          <ChevronDown className="h-3 w-3" />
          Show details
        </button>
      ) : (
        <div className="text-xs text-gray-500 flex flex-col gap-2.5">
          {Object.entries(extra).map(([k, v]) => {
            if (!v || (Array.isArray(v) && v.length === 0)) return null;
            
            const isArray = Array.isArray(v);
            const visibleItems = isArray ? v.slice(0, MAX_VISIBLE_TAGS) : v;
            const hiddenCount = isArray ? Math.max(0, v.length - MAX_VISIBLE_TAGS) : 0;
            
            return (
              <div key={k} className="flex flex-wrap items-baseline gap-2">
                <span className="font-bold text-gray-800 text-xs uppercase tracking-wide">{k}:</span>
                {isArray ? (
                  <div className="flex flex-wrap gap-1.5">
                    {(visibleItems as unknown[]).map((val: unknown, i: number) => (
                      <span key={i} className="bg-gradient-to-r from-indigo-50 to-purple-50 px-3 py-1.5 rounded-lg text-indigo-700 border border-indigo-200/50 text-xs font-medium shadow-sm hover:shadow-md transition-shadow">
                        {String(val)}
                      </span>
                    ))}
                    {hiddenCount > 0 && (
                      <span className="bg-gray-100 px-3 py-1.5 rounded-lg text-gray-600 border border-gray-200/50 text-xs font-medium">
                        +{hiddenCount} more
                      </span>
                    )}
                  </div>
                ) : (
                  <span className="text-gray-700 font-medium text-sm">{String(v)}</span>
                )}
              </div>
            );
          })}
          
          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              setIsExpanded(false);
            }}
            className="self-start mt-2 flex items-center gap-1 text-indigo-600 hover:text-indigo-800 font-medium text-xs transition-colors"
          >
            <ChevronUp className="h-3 w-3" />
            Hide details
          </button>
        </div>
      )}
    </div>
  );
}

export default function ItemCard({ uri, label, description, type, imageUrl, subtitle, extra, icon: Icon, color }: ItemCardProps) {
  // Extract ID from URI or use a safe fallback
  const id = uri.split("/").pop() || "";

  // Get display type - use entity_type subtypes for person entities, otherwise use main type
  const getDisplayType = () => {
    if (type === 'person' || type === 'actant' || type === 'actor' || type === 'human_actant') {
      // Extract entity type from extra if available (Person or Group)
      const entityType = extra?.['Type'] || extra?.['entity_type'];
      if (Array.isArray(entityType)) {
        return entityType[0] || type.toUpperCase();
      }
      return entityType || type.toUpperCase();
    }
    return type.toUpperCase();
  };

  const displayType = getDisplayType();

  return (
    <Link 
      href={buildDetailHref(type, id)}
      className="group relative flex flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-md hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 hover:border-transparent hover:ring-2 hover:ring-indigo-400/50"
    >
      {/* Gradient overlay on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 via-purple-500/5 to-pink-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none z-10" />
      
      {imageUrl ? (
        <div className="aspect-h-3 aspect-w-4 bg-gradient-to-br from-gray-100 to-gray-200 sm:aspect-none sm:h-48 relative overflow-hidden">
           <Image
            src={imageUrl}
            alt={label}
            fill
            unoptimized
            className="object-cover object-center transition-all duration-700 group-hover:scale-110 group-hover:rotate-1"
          />
           <div className="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
           <div className="absolute top-3 right-3 glass text-gray-800 text-[10px] uppercase font-bold px-3 py-1.5 rounded-lg backdrop-blur-md shadow-lg border border-white/40">
             {displayType}
           </div>
        </div>
      ) : (
        Icon ? (
          <div className={`aspect-h-3 aspect-w-4 sm:aspect-none sm:h-48 relative overflow-hidden flex items-center justify-center ${color ? color : "bg-gradient-to-br from-gray-50 to-gray-100"} transition-all duration-500`}>
             <Icon className={`h-20 w-20 text-black transition-all duration-500 group-hover:scale-110 group-hover:rotate-6 opacity-80`} />
             {/* Decorative circles */}
             <div className={`absolute top-0 left-0 w-32 h-32 ${color ? color : "bg-gray-300"} rounded-full opacity-5 -translate-x-16 -translate-y-16 group-hover:scale-150 transition-transform duration-700`} />
             <div className={`absolute bottom-0 right-0 w-24 h-24 ${color ? color : "bg-gray-300"} rounded-full opacity-5 translate-x-12 translate-y-12 group-hover:scale-150 transition-transform duration-700`} />
             <div className="absolute top-3 right-3 glass-dark text-white text-[10px] uppercase font-bold px-3 py-1.5 rounded-lg backdrop-blur-md shadow-lg border border-white/20">
               {displayType}
             </div>
          </div>
        ) : (
          <div className="aspect-h-3 aspect-w-4 bg-gradient-to-br from-gray-50 to-gray-100 sm:aspect-none sm:h-48 relative overflow-hidden">
               <Image 
                  src={`https://placehold.co/600x400/f1f5f9/475569?text=${type.charAt(0).toUpperCase() + type.slice(1)}`}
                  alt="Placeholder"
                  fill
                  className="object-cover opacity-70 group-hover:opacity-100 transition-all duration-500 group-hover:scale-105"
               />
               <div className="absolute top-3 right-3 glass text-gray-800 text-[10px] uppercase font-bold px-3 py-1.5 rounded-lg backdrop-blur-md shadow-lg border border-white/40">
                 {type}
               </div>
          </div>
        )
      )}
      
      <div className="flex flex-1 flex-col p-6 relative z-20">
        <h3 className="text-xl font-bold text-gray-900 group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-indigo-600 group-hover:to-purple-600 group-hover:bg-clip-text line-clamp-2 leading-tight mb-2 transition-all duration-300">
          {label}
        </h3>
        
        {subtitle && (
            <p className="text-xs font-semibold text-indigo-600 mb-3 uppercase tracking-wider bg-indigo-50 px-3 py-1 rounded-full inline-block self-start">
                {subtitle}
            </p>
        )}

        {description && (
          <p className="text-sm text-gray-600 line-clamp-3 mb-4 flex-1 leading-relaxed">{description}</p>
        )}
        
        {extra && <ExpandableExtra extra={extra} />}

        <div className="mt-5 flex items-center text-sm font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent group-hover:translate-x-2 transition-all duration-300">
          View Details <ArrowRight className="ml-2 h-4 w-4 text-indigo-600 group-hover:text-purple-600 transition-colors" />
        </div>
      </div>
    </Link>
  );
}

