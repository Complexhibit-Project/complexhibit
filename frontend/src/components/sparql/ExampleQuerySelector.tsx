"use client";

import { useState, useRef, useEffect } from "react";
import { BookOpen, ChevronDown, Search, Loader2 } from "lucide-react";
import { ExampleQuery, getCategoryLabel, getCategoryColor } from "@/lib/exampleQueries";
import { getExampleQueries, ExampleQueryResponse } from "@/lib/api";

interface ExampleQuerySelectorProps {
  /** Callback when a query is selected */
  onSelect: (query: string) => void;
  /** Optional CSS class */
  className?: string;
}

/**
 * Dropdown selector for predefined example SPARQL queries.
 * Groups queries by category and provides search functionality.
 */
export function ExampleQuerySelector({ onSelect, className = "" }: ExampleQuerySelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [queries, setQueries] = useState<ExampleQueryResponse[]>([]);
  const [loading, setLoading] = useState(false);
  
  const dropdownRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Fetch queries on mount
  useEffect(() => {
    const fetchQueries = async () => {
      setLoading(true);
      try {
        const resp = await getExampleQueries();
        setQueries(resp.data);
      } catch (err) {
        console.error("Failed to fetch example queries:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchQueries();
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchTerm("");
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Focus search input when opening
  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isOpen]);

  const handleSelectQuery = (query: ExampleQueryResponse) => {
    onSelect(query.query);
    setIsOpen(false);
    setSearchTerm("");
  };

  // Filter queries by search term
  const filteredQueries = queries.filter(q => 
    q.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (q.description && q.description.toLowerCase().includes(searchTerm.toLowerCase())) ||
    q.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Group by category
  const groupedQueries = filteredQueries.reduce((acc, query) => {
    if (!acc[query.category]) {
      acc[query.category] = [];
    }
    acc[query.category].push(query);
    return acc;
  }, {} as Record<string, ExampleQueryResponse[]>);

  return (
    <div className={`relative inline-block ${className}`} ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="
          flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm
          bg-gradient-to-r from-indigo-50 to-purple-50 
          border border-indigo-200 text-indigo-700 
          hover:from-indigo-100 hover:to-purple-100 hover:border-indigo-300
          transition-all duration-200 shadow-sm hover:shadow-md cursor-pointer
        "
        aria-label="Select example query"
        aria-haspopup="true"
        aria-expanded={isOpen}
      >
        <BookOpen className="h-4 w-4" />
        <span>Example Queries</span>
        <ChevronDown className={`h-4 w-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div 
          className="
            absolute left-0 mt-2 w-96 z-50 max-h-[480px]
            bg-white/95 backdrop-blur-xl rounded-xl shadow-2xl 
            border border-gray-100 overflow-hidden
            animate-in fade-in-0 zoom-in-95 duration-200
          "
          role="menu"
        >
          {/* Search Input */}
          <div className="p-3 border-b border-gray-100">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                ref={searchInputRef}
                type="text"
                placeholder="Search queries..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="
                  w-full pl-10 pr-4 py-2 text-sm
                  bg-gray-50 border border-gray-200 rounded-lg
                  focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
                  placeholder:text-gray-400
                "
              />
            </div>
          </div>

          {/* Query List */}
          <div className="max-h-[380px] overflow-y-auto">
            {loading ? (
              <div className="flex items-center justify-center p-8 text-gray-400">
                <Loader2 className="h-6 w-6 animate-spin" />
              </div>
            ) : Object.keys(groupedQueries).length === 0 ? (
              <div className="p-4 text-center text-gray-500 text-sm">
                No queries match your search
              </div>
            ) : (
              Object.entries(groupedQueries).map(([category, catQueries]) => (
                <div key={category}>
                  {/* Category Header */}
                  <div className="px-4 py-2 bg-gray-50 border-b border-gray-100">
                    <span className={`text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded ${getCategoryColor(category as ExampleQuery['category'])}`}>
                      {getCategoryLabel(category as ExampleQuery['category'])}
                    </span>
                  </div>
                  
                  {/* Queries in Category */}
                  {catQueries.map((query) => (
                    <button
                      key={query.id}
                      onClick={() => handleSelectQuery(query)}
                      className="
                        w-full px-4 py-3 text-left
                        hover:bg-indigo-50 transition-colors cursor-pointer
                        border-b border-gray-50 last:border-0
                      "
                      role="menuitem"
                    >
                      <div className="font-medium text-sm text-gray-900">
                        {query.name}
                      </div>
                      <div className="text-xs text-gray-500 mt-0.5 line-clamp-2">
                        {query.description}
                      </div>
                    </button>
                  ))}
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          <div className="p-3 border-t border-gray-100 bg-gray-50 text-xs text-gray-500 text-center">
            {queries.length} example queries available
          </div>
        </div>
      )}
    </div>
  );
}

export default ExampleQuerySelector;
