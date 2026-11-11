"use client";

import { Download, ChevronDown, FileSpreadsheet, FileJson } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { trackEvent } from "@/lib/metrics";

interface DetailDownloadButtonProps {
  /** Label of the entity */
  entityLabel: string;
  /** Type of the entity */
  entityType: string;
  /** All entity data to export */
  entityData: Record<string, unknown>;
  /** Optional additional related entities */
  relatedData?: Record<string, unknown[]>;
}

/**
 * Download button specifically styled for detail page headers.
 * Inherits the header's color scheme with a semi-transparent appearance.
 */
export function DetailDownloadButton({
  entityLabel,
  entityType,
  entityData,
  relatedData = {}
}: DetailDownloadButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const prepareExportData = () => {
    const exportData: Record<string, unknown> = {
      type: entityType,
      label: entityLabel,
      exportedAt: new Date().toISOString(),
      ...entityData
    };

    // Add related data sections
    Object.entries(relatedData).forEach(([key, value]) => {
      if (value && value.length > 0) {
        exportData[key] = value;
      }
    });

    return exportData;
  };

  const sanitizeFilename = (name: string): string => {
    return name
      .replace(/[^a-zA-Z0-9\s-_]/g, '')
      .replace(/\s+/g, '_')
      .slice(0, 50);
  };

  const downloadAsJSON = () => {
    const data = prepareExportData();
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${sanitizeFilename(entityLabel)}_${entityType}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    setIsOpen(false);
    
    trackEvent("download", { 
      format: "json", 
      type: entityType, 
      label: entityLabel 
    });
  };

  const downloadAsCSV = () => {
    const data = prepareExportData();
    
    // Flatten nested objects for CSV
    const flattened: Record<string, string> = {};
    const flatten = (obj: unknown, prefix = '') => {
      if (obj === null || obj === undefined) return;
      if (typeof obj === 'object' && !Array.isArray(obj)) {
        Object.entries(obj as Record<string, unknown>).forEach(([key, value]) => {
          const newKey = prefix ? `${prefix}_${key}` : key;
          if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
            flatten(value, newKey);
          } else if (Array.isArray(value)) {
            flattened[newKey] = value.map(v => 
              typeof v === 'object' ? JSON.stringify(v) : String(v)
            ).join('; ');
          } else {
            flattened[newKey] = String(value ?? '');
          }
        });
      }
    };
    flatten(data);

    // Create CSV with headers
    const headers = Object.keys(flattened);
    const values = Object.values(flattened).map(v => 
      v.includes(',') || v.includes('"') || v.includes('\n') 
        ? `"${v.replace(/"/g, '""')}"` 
        : v
    );
    const csv = `${headers.join(',')}\n${values.join(',')}`;

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${sanitizeFilename(entityLabel)}_${entityType}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    setIsOpen(false);
    
    trackEvent("download", { 
      format: "csv", 
      type: entityType, 
      label: entityLabel 
    });
  };

  return (
    <div className="relative inline-block" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="
          flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium
          bg-white/20 hover:bg-white/30 text-white/90 hover:text-white
          backdrop-blur-sm border border-white/20
          transition-all duration-200 cursor-pointer
        "
        aria-label="Download entity data"
        aria-haspopup="true"
        aria-expanded={isOpen}
      >
        <Download className="h-4 w-4" />
        <span>Download</span>
        <ChevronDown className={`h-3 w-3 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div 
          className="
            absolute right-0 mt-2 w-44 z-50
            bg-white rounded-xl shadow-2xl 
            border border-gray-100 overflow-hidden
            animate-in fade-in-0 zoom-in-95 duration-200
          "
          role="menu"
        >
          <button
            onClick={downloadAsJSON}
            className="
              w-full flex items-center gap-3 px-4 py-3 text-left text-sm text-gray-700
              hover:bg-indigo-50 hover:text-indigo-700 transition-colors cursor-pointer
            "
            role="menuitem"
          >
            <FileJson className="h-4 w-4 text-amber-600" />
            <span className="font-medium">JSON</span>
          </button>
          
          <div className="border-t border-gray-100" />
          
          <button
            onClick={downloadAsCSV}
            className="
              w-full flex items-center gap-3 px-4 py-3 text-left text-sm text-gray-700
              hover:bg-indigo-50 hover:text-indigo-700 transition-colors cursor-pointer
            "
            role="menuitem"
          >
            <FileSpreadsheet className="h-4 w-4 text-emerald-600" />
            <span className="font-medium">CSV</span>
          </button>
        </div>
      )}
    </div>
  );
}

export default DetailDownloadButton;
