"use client";

import { useState } from "react";
import { FileText, Loader2 } from "lucide-react";
import { toPng } from "html-to-image";
import jsPDF from "jspdf";

interface MetricsPDFButtonProps {
  targetRef: React.RefObject<HTMLDivElement | null>;
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  fileName?: string;
  className?: string;
}

export function MetricsPDFButton({ targetRef, className }: MetricsPDFButtonProps) {
  const [loading, setLoading] = useState(false);

  const handleDownload = async () => {
    if (!targetRef.current) return;
    setLoading(true);
    
    try {
      const dataUrl = await toPng(targetRef.current, {
        cacheBust: true,
        backgroundColor: '#ffffff',
        // Hide buttons from export
        filter: (node) => {
          if (node.tagName === 'BUTTON') return false;
          return true;
        }
      });
      
      const pdf = new jsPDF({
        orientation: "landscape",
        unit: "mm",
        format: "a4"
      });
      
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      
      const imgProps = pdf.getImageProperties(dataUrl);
      const imgWidth = imgProps.width;
      const imgHeight = imgProps.height;
      
      const ratio = Math.min(pdfWidth / imgWidth, (pdfHeight - 20) / imgHeight);
      
      const width = imgWidth * ratio;
      const height = imgHeight * ratio;
      
      const x = (pdfWidth - width) / 2;
      const y = (pdfHeight - height) / 2;
      
      pdf.addImage(dataUrl, 'PNG', x, y, width, height);

      const dateStr = new Date().toISOString().split('T')[0];
      pdf.save(`metrics_${dateStr}.pdf`);
      
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
        flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors
        ${className || ''}
      `}
    >
      {loading ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : (
        <FileText className="h-4 w-4" />
      )}
      <span>{loading ? "Generating..." : "Export PDF"}</span>
    </button>
  );
}
