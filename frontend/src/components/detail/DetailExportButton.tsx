"use client";

import { useState, useRef, useEffect } from "react";
import { Download, ChevronDown, FileCode, FileType } from "lucide-react";
import { downloadAsJSON } from "@/lib/downloadUtils";

interface DetailExportButtonProps {
  entityLabel: string;
  entityType: string;
  entityData: Record<string, unknown>;
  sparqlQueries: string[];
}

export function DetailExportButton({ 
  entityLabel, 
  entityType, 
  entityData,
  sparqlQueries 
}: DetailExportButtonProps) {
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



  const handleHtmlDownload = () => {
    // 1. Getting the current full HTML of the page
    const docClone = document.documentElement.cloneNode(true) as HTMLElement;
    
    // 2. Remove script tags to avoid re-execution or errors
    const scripts = docClone.querySelectorAll('script');
    scripts.forEach(script => script.remove());

    // 3. Remove next.js specific hydration data
    const nextData = docClone.querySelector('#__NEXT_DATA__');
    if (nextData) nextData.remove();
    
    // 4. Remove UI elements that shouldn't be in the snapshot (buttons, inputs)
    // We can mark elements with a class 'no-export' to exclude them
    const noExports = docClone.querySelectorAll('.no-export, .no-print, button, nav');
    noExports.forEach(el => el.remove());

    // 5. Inject Tailwind via CDN to ensure styles work offline/standalone
    const head = docClone.querySelector('head');
    if (head) {
      const tailwindScript = document.createElement('script');
      tailwindScript.src = "https://cdn.tailwindcss.com";
      head.appendChild(tailwindScript);
      
      // Add custom styles to fix some layout issues in standalone mode
      const style = document.createElement('style');
      style.textContent = `
        body { margin: 0; padding: 0; background-color: #f3f4f6; }
        .glass { background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px); }
      `;
      head.appendChild(style);
    }

    // 6. Append SPARQL queries at the bottom of the body
    const body = docClone.querySelector('body');
    if (body) {
      const queriesSection = document.createElement('div');
      queriesSection.className = "mt-12 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 bg-white rounded-xl shadow-sm border border-gray-200";
      queriesSection.innerHTML = `
        <h2 class="text-2xl font-bold mb-6 text-gray-800 border-b border-gray-100 pb-2">Data Provenance: SPARQL Queries</h2>
        <div class="space-y-6">
          ${sparqlQueries.map((query, idx) => `
            <div>
              <h3 class="font-medium text-gray-600 mb-2">Query ${idx + 1}</h3>
              <pre class="bg-gray-50 p-4 rounded-lg border border-gray-200 text-xs font-mono overflow-x-auto whitespace-pre-wrap">${query.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>
            </div>
          `).join('')}
        </div>
        <div class="mt-8 pt-4 border-t border-gray-100 text-center text-sm text-gray-500">
          Exported from Complexhibit Knowledge Graph • ${new Date().toLocaleString()}
        </div>
      `;
      body.appendChild(queriesSection);
    }

    const htmlContent = `<!DOCTYPE html>\n${docClone.outerHTML}`;
    
    const blob = new Blob([htmlContent], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${entityType}_${entityLabel.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.html`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    setIsOpen(false);
  };

  const handleJsonDownload = () => {
    downloadAsJSON(
      [entityData], 
      `${entityType}_${entityLabel.replace(/[^a-z0-9]/gi, '_').toLowerCase()}`,
      sparqlQueries.join("\n\n")
    );
    setIsOpen(false);
  };

  return (
    <div className="relative inline-block" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 rounded-full font-medium text-sm bg-white/20 backdrop-blur-md border border-white/30 text-white hover:bg-white/30 transition-all duration-200 shadow-lg cursor-pointer no-export no-print"
      >
        <Download className="h-4 w-4" />
        <span>Export</span>
        <ChevronDown className={`h-4 w-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 z-50 bg-white/95 backdrop-blur-xl rounded-xl shadow-2xl border border-gray-100 overflow-hidden animate-in fade-in-0 zoom-in-95 duration-200 text-gray-700 no-export no-print">
{/* PDF Export Removed per user request */}
          
          <button
            onClick={handleHtmlDownload}
            className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-gray-50 transition-colors cursor-pointer group"
          >
            <div className="p-2 bg-blue-50 text-blue-600 rounded-lg group-hover:bg-blue-100 transition-colors">
              <FileCode className="h-4 w-4" />
            </div>
            <div>
              <div className="font-medium text-gray-900">Download HTML</div>
              <div className="text-xs text-gray-500">Standalone webpage</div>
            </div>
          </button>

          <button
            onClick={handleJsonDownload}
            className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-gray-50 transition-colors cursor-pointer group"
          >
            <div className="p-2 bg-amber-50 text-amber-600 rounded-lg group-hover:bg-amber-100 transition-colors">
              <FileType className="h-4 w-4" />
            </div>
            <div>
              <div className="font-medium text-gray-900">Download JSON</div>
              <div className="text-xs text-gray-500">Raw data & queries</div>
            </div>
          </button>
        </div>
      )}

      {/* Hidden print-only section for SPARQL queries */}
      <div className="hidden print:block fixed bottom-0 left-0 w-full p-8 bg-white text-black break-before-page">
        <h2 className="text-xl font-bold mb-4 border-b border-gray-300 pb-2">Data Provenance: SPARQL Queries</h2>
        {sparqlQueries.map((query, idx) => (
          <div key={idx} className="mb-6">
            <h3 className="font-semibold text-sm text-gray-600 mb-2">Query {idx + 1}</h3>
            <pre className="bg-gray-50 p-4 rounded border border-gray-200 text-xs font-mono whitespace-pre-wrap break-inside-avoid">
              {query}
            </pre>
          </div>
        ))}
        <div className="text-center text-xs text-gray-400 mt-8 border-t border-gray-100 pt-4">
          Exported from Complexhibit Knowledge Graph • {new Date().toLocaleDateString()}
        </div>
      </div>

      <style jsx global>{`
        @media print {
          /* Hide non-printable elements */
          nav, header, footer, button, .no-print, .no-export { display: none !important; }
          
          /* Force background colors and graphics */
          body { 
            background: white !important; 
            color: black !important; 
            -webkit-print-color-adjust: exact !important; 
            print-color-adjust: exact !important; 
          }
          
          /* Allow background images and colors to be printed */
          * { 
            -webkit-print-color-adjust: exact !important; 
            print-color-adjust: exact !important; 
          }

          /* Restore some layout styles for print that emulate the screen */
          .bg-indigo-50 { background-color: #eef2ff !important; }
          .bg-purple-100 { background-color: #f3e8ff !important; }
          .bg-green-100 { background-color: #dcfce7 !important; }
          .bg-blue-100 { background-color: #dbeafe !important; }
          .bg-amber-100 { background-color: #fef3c7 !important; }
          .bg-pink-100 { background-color: #fce7f3 !important; }
          .bg-gray-100 { background-color: #f3f4f6 !important; }
          
          /* Gradients need to be forced or approximated */
          .bg-gradient-to-r { 
            background: linear-gradient(to right, #4f46e5, #9333ea) !important; 
            color: white !important;
          }
          .text-white { color: white !important; }

          /* Make container full width but respect padding */
          .container, .max-w-7xl { 
            max-width: 100% !important; 
            width: 100% !important; 
            margin: 0 !important; 
            padding: 0 !important; 
          }
          
          /* Flatten shadows and borders */
          .shadow-xl, .shadow-lg, .shadow-sm { 
            box-shadow: none !important; 
            border: 1px solid #eee !important; 
          }
          
          /* Ensure text is readable */
          h1 { font-size: 24pt !important; font-weight: 800 !important; margin-bottom: 0.5rem !important; }
          h2 { font-size: 18pt !important; color: #333 !important; margin-top: 1.5rem !important; border-bottom: 2px solid #eee !important; }
          p, li, span, div { font-size: 10pt !important; line-height: 1.4 !important; }
          a { text-decoration: none !important; color: black !important; }
          
          /* Avoid breaking inside sections */
          section, .card, .bg-white { 
            break-inside: avoid; 
            page-break-inside: avoid;
            margin-bottom: 1.5rem !important; 
          }

          /* Fix grid layouts for print */
          .grid { display: block !important; }
          .lg\\:grid-cols-3 > div { margin-bottom: 2rem; }
          .lg\\:col-span-1 { width: 100% !important; }
          .lg\\:col-span-2 { width: 100% !important; }
        }
      `}</style>
    </div>
  );
}
