"use client";

/**
 * SearchableSelect component for selecting entities with search functionality.
 * Used in Insert forms to select related entities like artworks, exhibitors, etc.
 */

import { API_URL } from "@/lib/config";
import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Search, X, Loader2, ChevronDown, PlusCircle } from "lucide-react";

interface SearchableSelectProps {
  label: string;
  entityType: "artwork" | "actant" | "institution" | "exhibition";
  selected: Array<{ uri: string; label: string }>;
  onChange: (selected: Array<{ uri: string; label: string }>) => void;
  placeholder?: string;
  multiple?: boolean;
  required?: boolean;
}

// Map entity types to API endpoints (using correct English endpoints)
const endpointMap: Record<string, string> = {
  artwork: "/all_artworks",
  actant: "/all_persons",
  institution: "/all_institutions",
  exhibition: "/all_exhibitions",
};

// Map entity types to form route (for "Create New" functionality)
const formRouteMap: Record<string, string> = {
  artwork: "/insert?type=artwork",
  actant: "/insert?type=actant",
  institution: "/insert?type=institution",
  exhibition: "/insert?type=exhibition",
};

export function SearchableSelect({
  label,
  entityType,
  selected,
  onChange,
  placeholder = "Search...",
  multiple = true,
  required = false,
}: SearchableSelectProps) {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [options, setOptions] = useState<Array<{ uri: string; label: string }>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Handle creating a new entity when not found
  const handleCreateNew = () => {
    const route = formRouteMap[entityType];
    if (route) {
      // Navigate to the insert form for this entity type
      router.push(route);
    }
  };

  // Debounced search
  const searchEntities = useCallback(async (query: string) => {
    if (!query || query.length < 2) {
      setOptions([]);
      return;
    }

    setIsLoading(true);
    const apiUrl = API_URL;
    const endpoint = endpointMap[entityType];

    try {
      const response = await fetch(`${apiUrl}${endpoint}?q=${encodeURIComponent(query)}&limit=20`);
      if (response.ok) {
        const result = await response.json();
        const items = result.data || result.items || [];
        setOptions(items.map((item: { uri: string; label?: string; name?: string }) => ({
          uri: item.uri,
          label: item.label || item.name || item.uri,
        })));
      }
    } catch (err) {
      console.error(`Failed to search ${entityType}:`, err);
    } finally {
      setIsLoading(false);
    }
  }, [entityType]);

  // Debounce search
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      searchEntities(searchQuery);
    }, 300);
    return () => clearTimeout(timeoutId);
  }, [searchQuery, searchEntities]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = (item: { uri: string; label: string }) => {
    if (multiple) {
      // Add if not already selected
      if (!selected.find((s) => s.uri === item.uri)) {
        onChange([...selected, item]);
      }
    } else {
      onChange([item]);
      setIsOpen(false);
    }
    setSearchQuery("");
  };

  const handleRemove = (uri: string) => {
    onChange(selected.filter((s) => s.uri !== uri));
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label} {required && <span className="text-red-500">*</span>}
      </label>

      {/* Selected items */}
      {multiple && selected.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-2">
          {selected.map((item) => (
            <span
              key={item.uri}
              className="inline-flex items-center gap-1 px-2 py-1 bg-emerald-100 text-emerald-800 text-sm rounded-lg"
            >
              {item.label}
              <button
                type="button"
                onClick={() => handleRemove(item.uri)}
                className="hover:text-red-600"
              >
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Search input */}
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onFocus={() => setIsOpen(true)}
          placeholder={multiple ? placeholder : (selected[0]?.label || placeholder)}
          className="w-full px-4 py-3 pl-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
        />
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        {isLoading && (
          <Loader2 className="absolute right-10 top-1/2 -translate-y-1/2 h-4 w-4 animate-spin text-gray-400" />
        )}
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="absolute right-3 top-1/2 -translate-y-1/2"
        >
          <ChevronDown className={`h-4 w-4 text-gray-400 transition-transform ${isOpen ? "rotate-180" : ""}`} />
        </button>
      </div>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {searchQuery.length < 2 ? (
            <div className="px-4 py-3 text-sm text-gray-500">
              Type at least 2 characters to search...
            </div>
          ) : isLoading ? (
            <div className="px-4 py-3 text-sm text-gray-500 flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" /> Searching...
            </div>
          ) : options.length === 0 ? (
            <div className="px-4 py-3">
              <div className="text-sm text-gray-500 mb-2">
                No results found for &quot;{searchQuery}&quot;
              </div>
              <button
                type="button"
                onClick={handleCreateNew}
                className="flex items-center gap-1 text-sm text-emerald-600 hover:text-emerald-700 font-medium transition-colors"
              >
                <PlusCircle className="h-4 w-4" />
                Create new {entityType}
              </button>
            </div>
          ) : (
            options.map((item) => {
              const isSelected = selected.find((s) => s.uri === item.uri);
              return (
                <button
                  key={item.uri}
                  type="button"
                  onClick={() => handleSelect(item)}
                  disabled={!!isSelected}
                  className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-100 ${
                    isSelected ? "bg-emerald-50 text-emerald-700" : ""
                  }`}
                >
                  {item.label}
                  {isSelected && <span className="text-xs ml-2">(selected)</span>}
                </button>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}
