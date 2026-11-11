"use client";

import { useRef } from "react";
import Link from "next/link";
import { Network } from "lucide-react";
import { CopyUri } from "@/components/CopyUri";
import { PDFDownloadButton } from "@/components/pdf/PDFDownloadButton";
import { DetailExportButton } from "@/components/detail"; // Assuming this is exported from index
import { RelationshipGraph } from "@/components/graph/RelationshipGraph";
import { unCamel } from "@/lib/utils";

interface DetailClientProps {
  label: string;
  type: string;
  fullUri: string;
  properties: Record<string, unknown>;
  sparqlQueries: string[];
  children: React.ReactNode;
  entityType?: string;
}

export function DetailClient({
  label,
  type,
  fullUri,
  properties,
  sparqlQueries,
  children,
  entityType
}: DetailClientProps) {
  const cardRef = useRef<HTMLDivElement>(null);

  const getDisplayType = () => {
    if ((type === 'person' || type === 'actant' || type === 'actor' || type === 'human_actant') && entityType) {
      return entityType;
    }
    return unCamel(type);
  };

  return (
    <div className="bg-white shadow-xl rounded-2xl overflow-hidden border border-gray-100" ref={cardRef}>
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-8 py-10 text-white">
        <div className="flex flex-col gap-3 mb-4">
          <div className="flex items-center gap-3 opacity-90">
            <span className="uppercase tracking-wider text-xs font-bold bg-white/20 px-3 py-1 rounded-full">
              {getDisplayType()}
            </span>
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">{label}</h1>
          <div className="mt-2 flex items-center gap-3 flex-wrap no-print">
            <CopyUri uri={fullUri} label="URI" />

            <Link
              href={`/graph?uri=${encodeURIComponent(fullUri)}&label=${encodeURIComponent(label)}`}
              className="inline-flex items-center gap-1.5 rounded-full bg-white/20 px-3 py-1 text-xs font-semibold text-white transition hover:bg-white/30"
            >
              <Network className="h-3.5 w-3.5" />
              Explore in graph
            </Link>

            <DetailExportButton
              entityLabel={label}
              entityType={type}
              entityData={properties}
              sparqlQueries={sparqlQueries}
            />
            
            <div className="hidden md:block">
              <PDFDownloadButton
                targetRef={cardRef}
                label={label}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="px-8 py-8">
        {children}
        <RelationshipGraph uri={fullUri} label={label} />
      </div>
    </div>
  );
}
