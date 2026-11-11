"use client";

/**
 * Interactive knowledge-graph explorer.
 *
 * Pick a starting resource (by search or via ?uri=… ) and traverse the RDF
 * graph: every node is an entity, every edge a predicate from the OntoExhibit
 * ontology. Double-click / "Expand" pulls a node's neighbours straight from the
 * triple store, so users discover the semantics by walking the graph.
 */

import { useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Search, Loader2, Maximize2, RotateCcw, ExternalLink, Network, X, Tag } from "lucide-react";
import useDebounce from "@/hooks/useDebounce";
import ForceGraph from "./ForceGraph";
import {
  fetchEgoNetwork,
  mergeGraph,
  stripLiterals,
  searchEntitiesByLabel,
  nodeColor,
  NODE_TYPE_COLORS,
  type GraphData,
  type GraphNode,
  type EntityHit,
} from "@/lib/graph";
import { parseEntityUri, buildDetailHref } from "@/lib/entity-routing";

const EMPTY: GraphData = { nodes: [], edges: [] };

const TYPE_LABELS: Record<string, string> = {
  exhibition: "Exhibition",
  artwork: "Artwork",
  actant: "Actor",
  institution: "Institution",
  catalog: "Catalog",
  company: "Company",
  other: "Other / intermediate",
  literal: "Attribute",
};

export default function GraphExplorer() {
  const params = useSearchParams();
  const [graph, setGraph] = useState<GraphData>(EMPTY);
  const [selected, setSelected] = useState<GraphNode | null>(null);
  const [loading, setLoading] = useState(false);
  const [expanding, setExpanding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [term, setTerm] = useState("");
  const debounced = useDebounce(term, 350);
  const [results, setResults] = useState<EntityHit[]>([]);
  const [searching, setSearching] = useState(false);
  const [showLiterals, setShowLiterals] = useState(false);

  const seed = useCallback(async (uri: string, label?: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchEgoNetwork(uri, label, 60, true);
      setGraph(data);
      setSelected(data.nodes.find((n) => n.isFocus) ?? null);
      setResults([]);
      setTerm("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load graph");
    } finally {
      setLoading(false);
    }
  }, []);

  // Seed from URL params (e.g. arriving from a detail page).
  useEffect(() => {
    const uri = params.get("uri");
    if (uri) seed(uri, params.get("label") ?? undefined);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Live label search.
  useEffect(() => {
    let active = true;
    if (debounced.trim().length < 2) {
      setResults([]);
      return;
    }
    setSearching(true);
    searchEntitiesByLabel(debounced)
      .then((hits) => active && setResults(hits))
      .catch(() => active && setResults([]))
      .finally(() => active && setSearching(false));
    return () => {
      active = false;
    };
  }, [debounced]);

  const expand = useCallback(
    async (node: GraphNode) => {
      // Literal (attribute) nodes are leaf values — nothing to expand.
      if (node.kind === "literal" || node.expanded) {
        setSelected(node);
        return;
      }
      setExpanding(true);
      setError(null);
      try {
        const addition = await fetchEgoNetwork(node.id, node.label, 60, true);
        setGraph((g) => mergeGraph(g, addition, node.id));
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to expand node");
      } finally {
        setExpanding(false);
      }
    },
    [],
  );

  // Hide attribute nodes unless the user opts in.
  const displayed = useMemo(() => (showLiterals ? graph : stripLiterals(graph)), [graph, showLiterals]);
  const isLiteralSelected = selected?.kind === "literal";
  const selectedDetail = selected && !isLiteralSelected ? parseEntityUri(selected.id) : null;

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight text-gray-900 flex items-center gap-2">
          <Network className="h-7 w-7 text-indigo-600" />
          Knowledge Graph Explorer
        </h1>
        <p className="mt-2 text-gray-600 max-w-3xl">
          Walk the semantic graph behind Complexhibit. Search for any resource, then
          click a node to inspect it and double-click (or press <em>Expand</em>) to pull
          its relationships from the triple store. Edges are the ontology predicates.
        </p>
      </div>

      {/* Search */}
      <div className="relative mb-6 max-w-xl">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            value={term}
            onChange={(e) => setTerm(e.target.value)}
            placeholder="Search entities by name (e.g. an exhibition, artist, museum…)"
            className="w-full rounded-xl border border-gray-200 bg-white py-3 pl-11 pr-10 text-sm shadow-sm focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100"
          />
          {searching && <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 animate-spin text-indigo-500" />}
          {term && !searching && (
            <button onClick={() => setTerm("")} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
        {results.length > 0 && (
          <ul className="absolute z-20 mt-1 max-h-72 w-full overflow-auto rounded-xl border border-gray-100 bg-white shadow-lg">
            {results.map((hit) => (
              <li key={hit.uri}>
                <button
                  onClick={() => seed(hit.uri, hit.label)}
                  className="flex w-full items-center gap-3 px-4 py-2.5 text-left hover:bg-indigo-50"
                >
                  <span className="h-3 w-3 flex-shrink-0 rounded-full" style={{ background: nodeColor(hit.type) }} />
                  <span className="truncate text-sm text-gray-800">{hit.label}</span>
                  <span className="ml-auto text-xs text-gray-400">{TYPE_LABELS[hit.type] ?? hit.type}</span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Attributes toggle */}
      <div className="mb-6">
        <button
          type="button"
          onClick={() => setShowLiterals((v) => !v)}
          aria-pressed={showLiterals}
          className={`inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium transition ${
            showLiterals
              ? "border-indigo-300 bg-indigo-50 text-indigo-700"
              : "border-gray-200 bg-white text-gray-600 hover:bg-gray-50"
          }`}
        >
          <span
            className={`flex h-4 w-7 items-center rounded-full px-0.5 transition ${
              showLiterals ? "justify-end bg-indigo-500" : "justify-start bg-gray-300"
            }`}
          >
            <span className="h-3 w-3 rounded-full bg-white" />
          </span>
          <Tag className="h-4 w-4" />
          Show attributes
        </button>
        <span className="ml-3 text-xs text-gray-400">data-property values (gender, dates, …) as attached nodes</span>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Graph canvas */}
        <div className="lg:col-span-2">
          <div className="relative rounded-2xl border border-gray-200 bg-white shadow-sm">
            {loading ? (
              <div className="flex h-[560px] items-center justify-center text-gray-400">
                <Loader2 className="mr-2 h-6 w-6 animate-spin" /> Loading graph…
              </div>
            ) : graph.nodes.length === 0 ? (
              <EmptyState />
            ) : (
              <>
                <ForceGraph
                  data={displayed}
                  selectedId={selected?.id}
                  onNodeClick={setSelected}
                  onNodeDoubleClick={expand}
                />
                {expanding && (
                  <div className="absolute right-4 top-4 flex items-center gap-2 rounded-full bg-white/90 px-3 py-1.5 text-xs font-medium text-indigo-600 shadow">
                    <Loader2 className="h-3.5 w-3.5 animate-spin" /> Expanding…
                  </div>
                )}
                <div className="absolute left-4 top-4 rounded-lg bg-white/85 px-3 py-1.5 text-xs text-gray-500 shadow-sm backdrop-blur">
                  {displayed.nodes.length} nodes · {displayed.edges.length} edges
                </div>
              </>
            )}
          </div>
          <Legend />
        </div>

        {/* Side panel */}
        <aside className="lg:col-span-1">
          <div className="sticky top-24 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
            {selected ? (
              <div>
                <div className="mb-3 flex items-center gap-2">
                  <span className="h-3.5 w-3.5 rounded-full" style={{ background: nodeColor(selected.type) }} />
                  <span className="text-xs font-medium uppercase tracking-wide text-gray-400">
                    {TYPE_LABELS[selected.type] ?? selected.type}
                  </span>
                </div>
                <h2 className="text-lg font-semibold text-gray-900 break-words">{selected.label}</h2>
                {isLiteralSelected ? (
                  <p className="mt-1 text-xs text-gray-400">Data-property value (literal). Attributes are leaf nodes — they can&apos;t be expanded.</p>
                ) : (
                  <p className="mt-1 break-all text-xs text-gray-400">{selected.id}</p>
                )}

                {!isLiteralSelected && (
                  <div className="mt-4 flex flex-col gap-2">
                    <button
                      onClick={() => expand(selected)}
                      disabled={selected.expanded || expanding}
                      className="flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-gray-300"
                    >
                      <Maximize2 className="h-4 w-4" />
                      {selected.expanded ? "Already expanded" : "Expand relationships"}
                    </button>
                    {selectedDetail && (
                      <Link
                        href={buildDetailHref(selectedDetail.type, selectedDetail.id)}
                        className="flex items-center justify-center gap-2 rounded-lg border border-gray-200 px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
                      >
                        <ExternalLink className="h-4 w-4" />
                        Open detail page
                      </Link>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="text-sm text-gray-500">
                <p className="font-medium text-gray-700">No node selected</p>
                <p className="mt-1">Search above to plant a starting point, then click any node to inspect it.</p>
              </div>
            )}

            {graph.nodes.length > 0 && (
              <button
                onClick={() => {
                  setGraph(EMPTY);
                  setSelected(null);
                }}
                className="mt-5 flex w-full items-center justify-center gap-2 rounded-lg border border-gray-100 px-3 py-2 text-xs text-gray-400 hover:text-gray-600"
              >
                <RotateCcw className="h-3.5 w-3.5" /> Clear graph
              </button>
            )}

            <div className="mt-6 border-t border-gray-100 pt-4 text-xs text-gray-400">
              <p className="font-medium text-gray-500">Tips</p>
              <ul className="mt-1 list-inside list-disc space-y-1">
                <li>Drag nodes to rearrange · scroll to zoom · drag canvas to pan</li>
                <li>Hover a node to highlight its direct relationships</li>
                <li>A small ring means the node can still be expanded</li>
              </ul>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}

function Legend() {
  return (
    <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2 px-1 text-xs text-gray-500">
      {Object.entries(NODE_TYPE_COLORS).map(([type, color]) => (
        <span key={type} className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full" style={{ background: color }} />
          {TYPE_LABELS[type] ?? type}
        </span>
      ))}
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex h-[560px] flex-col items-center justify-center px-6 text-center text-gray-400">
      <Network className="h-12 w-12 text-gray-300" />
      <p className="mt-4 max-w-sm text-sm">
        Search for a resource above to start exploring the knowledge graph. Every step
        reveals new connections drawn live from the triple store.
      </p>
    </div>
  );
}
