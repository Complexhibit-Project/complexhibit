"use client";

import { useState } from "react";
import { FileDown, Loader2 } from "lucide-react";
import { toPng } from "html-to-image";
import jsPDF from "jspdf";

interface PDFDownloadButtonProps {
  targetRef: React.RefObject<HTMLDivElement | null>;
  label: string;
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  fileName?: string;
  className?: string;
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  type?: string;
}

export function PDFDownloadButton({ targetRef, label, fileName, className }: PDFDownloadButtonProps) {
  const [loading, setLoading] = useState(false);

  const handleDownload = async () => {
    if (!targetRef.current) return;
    setLoading(true);
    
    try {
      // 1. Convert DOM to PNG using html-to-image
      // We skip fonts to avoid CORS issues and complexity, letting browser fallback
      const dataUrl = await toPng(targetRef.current, {
        cacheBust: true,
        backgroundColor: '#ffffff',
        // Filter out buttons from the screenshot
        filter: (node) => {
          if (node.tagName === 'BUTTON') return false;
          return true;
        }
      });
      
      // 2. Add image to PDF
      const pdf = new jsPDF({
        orientation: "portrait",
        unit: "mm",
        format: "a4"
      });
      
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      
      const imgProps = pdf.getImageProperties(dataUrl);
      const imgWidth = imgProps.width;
      const imgHeight = imgProps.height;
      
      // Calculate scaling to fit width, maintaining aspect ratio
      const ratio = Math.min(pdfWidth / imgWidth, (pdfHeight - 20) / imgHeight);
      
      const width = imgWidth * ratio;
      const height = imgHeight * ratio;
      
      // Center horizontally
      const x = (pdfWidth - width) / 2;
      const y = 10; // 10mm margin top
      
      pdf.addImage(dataUrl, 'PNG', x, y, width, height);

      // 3. Save
      const safeLabel = label.replace(/[^a-z0-9]/gi, '_').toLowerCase();
      pdf.save(fileName || `${safeLabel}_detail.pdf`);
      
    } catch (err) {
      console.error("PDF generation failed", err);
      // @ts-expect-error - Error message type
      alert(`Could not generate PDF: ${err?.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleDownload}
      disabled={loading}
      className={`
        flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200 shadow-sm
        ${loading 
          ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
          : 'bg-white/90 backdrop-blur-sm border border-gray-200 text-gray-700 hover:bg-gray-50 hover:border-gray-300 hover:shadow-md'
        }
        ${className || ''}
      `}
    >
      {loading ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : (
        <FileDown className="h-4 w-4 text-red-600" />
      )}
      <span>{loading ? "Generating..." : "Export PDF"}</span>
    </button>
  );
}
