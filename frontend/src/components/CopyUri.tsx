"use client";

import { Check, Copy } from "lucide-react";
import { useState } from "react";

interface CopyUriProps {
  uri: string;
  label?: string;
  className?: string;
}

export function CopyUri({ uri, label, className = "" }: CopyUriProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(uri);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  return (
    <div className={`flex items-center gap-2 max-w-full ${className}`}>
        {label && <span className="text-xs font-semibold uppercase opacity-70">{label}:</span>}
        <div className="flex items-center gap-2 bg-black/20 rounded-full px-3 py-1 overflow-hidden max-w-full">
            <span className="text-xs font-mono truncate" title={uri}>
                {uri}
            </span>
            <button 
                onClick={handleCopy}
                className="hover:bg-white/10 p-1 rounded-full transition-colors flex-shrink-0"
                title="Copy URI"
            >
                {copied ? <Check className="h-3 w-3 text-green-300" /> : <Copy className="h-3 w-3 text-white/70" />}
            </button>
        </div>
    </div>
  );
}
