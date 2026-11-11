"use client";

/**
 * InfiniteList component with cursor-based pagination.
 * 
 * Provides a paginated list view with search and filtering capabilities.
 * Uses intersection observer for infinite scroll loading.
 */

import { useEffect, useState, useCallback } from "react";
import { getFromType, fetchFromApi } from "@/lib/api";
import ItemCard from "@/components/ItemCard";
import EntityFilters, { FILTER_OPTION_ENDPOINTS } from "@/components/EntityFilters";
import { useIntersectionObserver } from "@/hooks/useIntersectionObserver";
import { cleanLabel } from "@/lib/utils";
import { Search, Loader2, Calendar, Building2, Users, Image as ImageIcon, BookOpen, Briefcase } from "lucide-react";
import type { FilterOptions, Entity } from "@/lib/types";
import { getCardExtra } from "@/lib/entity-helpers";

const TYPE_CONFIG: Record<string, { icon: React.ElementType, color: string }> = {
  exhibition: { icon: Calendar, color: "bg-blue-500" },
  artwork: { icon: ImageIcon, color: "bg-purple-500" },
  institution: { icon: Building2, color: "bg-green-500" },
  actant: { icon: Users, color: "bg-orange-500" },
  person: { icon: Users, color: "bg-orange-500" },
  human_actant: { icon: Users, color: "bg-orange-500" },
  actor: { icon: Users, color: "bg-orange-500" },
  catalog: { icon: BookOpen, color: "bg-amber-500" },
  company: { icon: Briefcase, color: "bg-teal-500" },
};


interface InfiniteListProps {
  initialData: Entity[];
  initialCursor: string | null;
  type: string;
}

export default function InfiniteList({ initialData, initialCursor, type }: InfiniteListProps) {
  const [items, setItems] = useState<Entity[]>(initialData);
  const [cursor, setCursor] = useState<string | null>(initialCursor);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [hasMore, setHasMore] = useState(!!initialCursor);
  const [filterOptions, setFilterOptions] = useState<FilterOptions>({});
  const [isInitialMount, setIsInitialMount] = useState(true);
  
  // Ref for intersection observer (infinite scroll trigger)
  const [ref, isIntersecting] = useIntersectionObserver({ threshold: 0.1 });

  // Load more items when scrolling
  const loadMore = useCallback(async () => {
    if (isLoading || !cursor) return;
    
    setIsLoading(true);
    try {
      const params: Record<string, string> = { cursor, ...filters };
      if (searchQuery) params.q = searchQuery;
      
      const response = await getFromType(type, params);
      
      if (response?.data) {
        const newItems = Array.isArray(response.data) ? response.data : [];
        setItems((prev) => [...prev, ...newItems]);
        setCursor(response.next_cursor || null);
        setHasMore(!!response.next_cursor);
      } else {
        setHasMore(false);
      }
    } catch (error) {
      console.error("Error loading more items:", error);
    } finally {
      setIsLoading(false);
    }
  }, [cursor, isLoading, type, searchQuery, filters]);

  // Trigger loadMore when bottom is reached
  useEffect(() => {
    if (isIntersecting && hasMore && !isLoading) {
      loadMore();
    }
  }, [isIntersecting, hasMore, isLoading, loadMore]);

  // Handle search input
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setCursor(null);
  };

  // Handle filter changes
  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setCursor(null);
  };

  // Refetch when search or filters change (with debounce)
  useEffect(() => {
    // Skip on initial mount to preserve server-rendered data
    if (isInitialMount && !searchQuery && Object.keys(filters).length === 0) {
      setIsInitialMount(false);
      return;
    }
    setIsInitialMount(false);
    
    const timeoutId = setTimeout(async () => {
      setIsLoading(true);
      try {
        const params: Record<string, string> = { ...filters };
        if (searchQuery) params.q = searchQuery;

        const response = await getFromType(type, params);
        
        if (response?.data) {
          const newItems = Array.isArray(response.data) ? response.data : [];
          setItems(newItems);
          setCursor(response.next_cursor || null);
          setHasMore(!!response.next_cursor);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [searchQuery, filters, type, isInitialMount]);

  // Fetch filter options on mount
  useEffect(() => {
    const endpoints = FILTER_OPTION_ENDPOINTS[type] || [];
    
    endpoints.forEach(async (filterType) => {
      try {
        const res = await fetchFromApi(`/filter_options/${filterType}`);
        if (res?.data) {
          setFilterOptions(prev => ({ ...prev, [filterType]: res.data }));
        }
      } catch (e) {
        console.error(`Failed to fetch options for ${filterType}`, e);
      }
    });
  }, [type]);

  // Helper to parse "Name:::URI|Name2:::URI2" format - MOVED TO HELPER
  // Helper to parse simple piped strings - MOVED TO HELPER
  // Build extra info for cards based on entity type - MOVED TO HELPER

  return (
    <div className="space-y-8">
      {/* Search & Filters */}
      <div className="max-w-4xl mx-auto space-y-4">
        {/* Main Search */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm shadow-sm transition-shadow hover:shadow-md"
            placeholder={`Search ${type}s...`}
            value={searchQuery}
            onChange={handleSearch}
          />
        </div>

        {/* Entity-specific Filters */}
        <EntityFilters
          type={type}
          filters={filters}
          filterOptions={filterOptions}
          onFilterChange={handleFilterChange}
        />
      </div>

      {/* Results Status */}
      <div className="text-center text-sm text-gray-500">
        Showing {items.length} results {hasMore && "..."}
      </div>

      {/* Results Grid */}
      {items.length === 0 && !isLoading ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No items found matching your search.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {items.map((item: Entity, index: number) => (
            <ItemCard
              key={`${item.uri}-${index}`}
              uri={item.uri}
              label={cleanLabel(item.label || item.title || "Untitled")}
              type={type}
              description={item.description || item.abstract}
              imageUrl={item.image || item.img}
              subtitle=""
              extra={getCardExtra(item, type)}
              icon={TYPE_CONFIG[type]?.icon || ImageIcon}
              color={TYPE_CONFIG[type]?.color || "bg-gray-500"}
            />
          ))}
        </div>
      )}

      {/* Loading / Infinite Scroll Sentinel */}
      <div ref={ref} className="py-8 flex justify-center items-center h-20">
        {isLoading && (
          <div className="flex items-center gap-2 text-indigo-600">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span>Loading more...</span>
          </div>
        )}
        {!hasMore && items.length > 0 && (
          <div className="text-gray-400 text-sm italic">
            You&apos;ve reached the end of the list.
          </div>
        )}
      </div>
    </div>
  );
}
