"use client";

import { useState, useRef, useEffect } from "react";
import { Download, ChevronDown, FileSpreadsheet, FileJson, FileCode, Database, FileText } from "lucide-react";
import { 
  downloadAsCSV, 
  downloadAsJSON, 
  downloadAsHTML, 
  downloadAsRDF, 
  downloadAsNTriples, 
  getTimestampFilename 
} from "@/lib/downloadUtils";
import { trackEvent } from "@/lib/metrics";

type DownloadFormat = "csv" | "json" | "html" | "rdf" | "ntriples";

interface DownloadButtonProps {
  /** Data to download */
  data: Record<string, unknown>[];
  /** Base filename for download (without extension) */
  filename?: string;
  /** The SPARQL query to include in downloads */
  sparqlQuery?: string;
  /** Whether the button is disabled */
  disabled?: boolean;
  /** Optional CSS class for custom styling */
  className?: string;
}

const formatOptions: { 
  id: DownloadFormat; 
  label: string; 
  description: string; 
  icon: React.ElementType; 
  color: string 
}[] = [
  { id: "csv", label: "CSV", description: "Spreadsheet format", icon: FileSpreadsheet, color: "text-emerald-600" },
  { id: "json", label: "JSON", description: "Structured data", icon: FileJson, color: "text-amber-600" },
  { id: "html", label: "HTML", description: "Styled table", icon: FileCode, color: "text-blue-600" },
  { id: "rdf", label: "RDF/XML", description: "Semantic web", icon: Database, color: "text-purple-600" },
  { id: "ntriples", label: "N-Triples", description: "Triple format", icon: FileText, color: "text-rose-600" },
];

/**
 * A dropdown button for downloading SPARQL results in multiple formats.
 * Features glassmorphism styling per ui-ux-pro-max guidelines.
 */
export function DownloadButton({ 
  data, 
  filename = "export", 
  sparqlQuery,
  disabled = false,
  className = ""
}: DownloadButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleDownload = (format: DownloadFormat) => {
    const timestampedFilename = getTimestampFilename(filename);
    
    trackEvent("download", { 
      format, 
      filename: timestampedFilename,
      type: "search_results",
      count: data?.length || 0
    });

    switch (format) {
      case "csv":
        downloadAsCSV(data, timestampedFilename, sparqlQuery);
        break;
      case "json":
        downloadAsJSON(data, timestampedFilename, sparqlQuery);
        break;
      case "html":
        downloadAsHTML(data, timestampedFilename, sparqlQuery);
        break;
      case "rdf":
        downloadAsRDF(data, timestampedFilename, sparqlQuery);
        break;
      case "ntriples":
        downloadAsNTriples(data, timestampedFilename, sparqlQuery);
        break;
    }
    
    setIsOpen(false);
  };

  const isDisabled = disabled || !data || data.length === 0;

  return (
    <div className={`relative inline-block ${className}`} ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={isDisabled}
        className={`
          flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm
          transition-all duration-200 shadow-sm
          ${isDisabled 
            ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
            : 'bg-white/90 backdrop-blur-sm border border-gray-200 text-gray-700 hover:bg-gray-50 hover:border-gray-300 hover:shadow-md cursor-pointer'
          }
        `}
        aria-label="Download results"
        aria-haspopup="true"
        aria-expanded={isOpen}
      >
        <Download className="h-4 w-4" />
        <span>Download</span>
        <ChevronDown className={`h-4 w-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div 
          className="
            absolute right-0 mt-2 w-52 z-50
            bg-white/95 backdrop-blur-xl rounded-xl shadow-2xl 
            border border-gray-100 overflow-hidden
            animate-in fade-in-0 zoom-in-95 duration-200
          "
          role="menu"
        >
          {formatOptions.map((format, index) => {
            const Icon = format.icon;
            return (
              <div key={format.id}>
                {index > 0 && <div className="border-t border-gray-100" />}
                <button
                  onClick={() => handleDownload(format.id)}
                  className="
                    w-full flex items-center gap-3 px-4 py-3 text-left text-sm text-gray-700
                    hover:bg-indigo-50 hover:text-indigo-700 transition-colors cursor-pointer
                  "
                  role="menuitem"
                >
                  <Icon className={`h-4 w-4 ${format.color}`} />
                  <div>
                    <div className="font-medium">{format.label}</div>
                    <div className="text-xs text-gray-500">{format.description}</div>
                  </div>
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default DownloadButton;
