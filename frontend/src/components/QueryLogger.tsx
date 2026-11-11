"use client";

import { useEffect } from "react";

interface QueryLoggerProps {
  query?: string;
  type?: string;
}

export default function QueryLogger({ query, type }: QueryLoggerProps) {
  const DEBUG = false; // Set to true to enable logging

  useEffect(() => {
    if (!DEBUG) return;

    if (query) {
      console.log(`[SPARQL QUERY - ${type || 'General'}]:\n`, query);
    } else {
      console.log(`[QueryLogger] No query prop received for ${type}`);
    }
  }, [DEBUG, query, type]);

  return null; // Render nothing
}
