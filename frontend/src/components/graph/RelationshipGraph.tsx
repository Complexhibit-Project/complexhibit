"use client";

/**
 * Compact relationship graph embedded on entity detail pages.
 *
 * Lazily loads the focus entity's ego-network when scrolled into view and
 * renders it with the shared ForceGraph. Clicking a connected node jumps to the
 * full Knowledge Graph Explorer seeded at that node.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Network, Loader2, Maximize2 } from "lucide-react";
import { useIntersectionObserver } from "@/hooks/useIntersectionObserver";
import ForceGraph from "./ForceGraph";
import { fetchEgoNetwork, labelFromUri, typeFromUri, type GraphData, type GraphNode } from "@/lib/graph";

interface RelationshipGraphProps {
  uri: string;
  label: string;
}

export function RelationshipGraph({ uri, label }: RelationshipGraphProps) {
  const [ref, isVisible] = useIntersectionObserver({ rootMargin: "200px" });
  const router = useRouter();
  const [graph, setGraph] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(false);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    if (!isVisible || graph || loading || failed) return;
    setLoading(true);
    fetchEgoNetwork(uri, label, 40, true)
      .then((data) => setGraph(data))
      .catch(() => setFailed(true))
      .finally(() => setLoading(false));
  }, [isVisible, uri, label, graph, loading, failed]);

  const explorerHref = `/graph?uri=${encodeURIComponent(uri)}&label=${encodeURIComponent(label)}`;

  const handleNodeClick = (node: GraphNode) => {
    if (node.isFocus) return;
    router.push(`/graph?uri=${encodeURIComponent(node.id)}&label=${encodeURIComponent(node.label)}`);
  };

  // Always render the visualizer. On fetch failure, fall back to the focus node
  // alone so the section never silently disappears.
  const fallbackGraph: GraphData = {
    nodes: [
      { id: uri, label: label || labelFromUri(uri), type: typeFromUri(uri), kind: "entity", isFocus: true, expanded: true },
    ],
    edges: [],
  };
  const displayGraph = graph ?? (failed ? fallbackGraph : null);
  const relCount = displayGraph
    ? displayGraph.nodes.filter((n) => !n.isFocus && n.kind === "entity").length
    : 0;

  return (
    <div ref={ref} className="mt-8 border-t border-gray-100 pt-6">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900">
          <Network className="h-5 w-5 text-indigo-600" />
          Relationships
        </h2>
        <Link
          href={explorerHref}
          className="flex items-center gap-1.5 rounded-lg bg-indigo-50 px-3 py-1.5 text-sm font-medium text-indigo-600 transition hover:bg-indigo-100 no-print"
        >
          <Maximize2 className="h-4 w-4" />
          Open in explorer
        </Link>
      </div>

      {loading || !displayGraph ? (
        <div className="flex h-[360px] items-center justify-center rounded-2xl bg-slate-50 text-gray-400">
          <Loader2 className="mr-2 h-5 w-5 animate-spin" /> Loading relationships…
        </div>
      ) : (
        <>
          <ForceGraph data={displayGraph} height={360} onNodeClick={handleNodeClick} />
          <p className="mt-2 text-center text-xs text-gray-400 no-print">
            {failed
              ? "Couldn't load relationships · showing this item only"
              : relCount > 0
                ? `Click a connected node to keep exploring · ${relCount} direct relationship${relCount === 1 ? "" : "s"}`
                : "No linked entities · showing this item and its attributes"}
          </p>
        </>
      )}
    </div>
  );
}
