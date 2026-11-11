"use client";

import { API_URL } from "@/lib/config";
import { useState, useEffect, useRef, useCallback } from "react";
import { Search, X, Loader2 } from "lucide-react";

interface AsyncFilterSelectProps {
  label?: string; // Optional label, usually placeholder is enough
  entityType: "artwork" | "actant" | "institution" | "exhibition";
  value: string; // The URI
  onChange: (key: string, value: string) => void; 
  filterKey: string;
  placeholder?: string;
}

// Map entity types to API endpoints - reusing existing ones
const endpointMap: Record<string, string> = {
  artwork: "/all_artworks",
  actant: "/all_persons", 
  institution: "/all_institutions",
  exhibition: "/all_exhibitions",
};

export default function AsyncFilterSelect({
  entityType,
  value,
  onChange,
  filterKey,
  placeholder = "Search...",
}: AsyncFilterSelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [options, setOptions] = useState<Array<{ uri: string; label: string }>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedLabel, setSelectedLabel] = useState(""); // Store label separately

  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

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
      // Using existing list endpoints which support q=...
      const response = await fetch(`${apiUrl}${endpoint}?q=${encodeURIComponent(query)}&page_size=10`);
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

  // Debounce effect
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      searchEntities(searchQuery);
    }, 300);
    return () => clearTimeout(timeoutId);
  }, [searchQuery, searchEntities]);

  // Handle click outside
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
    onChange(filterKey, item.uri);
    setSelectedLabel(item.label);
    setSearchQuery("");
    setIsOpen(false);
  };

  const handleClear = () => {
    onChange(filterKey, "");
    setSelectedLabel("");
    setSearchQuery("");
  };

  return (
    <div className="relative min-w-[200px]" ref={dropdownRef}>
      {/* Input / Display Area */}
      {value ? (
        // Selected State
        <div className="flex items-center justify-between px-4 py-2 border border-blue-300 bg-blue-50 rounded-lg text-sm text-blue-800">
           <span className="truncate max-w-[150px]">{selectedLabel || value}</span>
           <button onClick={handleClear} className="ml-2 hover:text-blue-600">
             <X className="h-4 w-4" />
           </button>
        </div>
      ) : (
        // Search State
        <div className="relative">
          <input
            ref={inputRef}
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => setIsOpen(true)}
            placeholder={placeholder}
            className="w-full px-4 py-2 border border-gray-200 rounded-lg text-sm focus:ring-1 focus:ring-indigo-500 outline-none"
          />
           {isLoading ? (
             <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 animate-spin text-gray-400" />
           ) : (
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
           )}
        </div>
      )}

      {/* Dropdown */}
      {isOpen && !value && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {searchQuery.length < 2 ? (
            <div className="px-4 py-3 text-sm text-gray-500">To search, type...</div>
          ) : options.length === 0 && !isLoading ? (
            <div className="px-4 py-3 text-sm text-gray-500">No results.</div>
          ) : (
            options.map((item) => (
              <button
                key={item.uri}
                onClick={() => handleSelect(item)}
                className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 truncate"
                title={item.label}
              >
                {item.label}
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}
