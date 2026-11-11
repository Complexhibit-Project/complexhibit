/**
 * Knowledge-graph data layer.
 *
 * Turns the RDF triple store into an interactive node/edge graph by querying
 * the "ego network" of any resource (its incoming and outgoing relations) via
 * the public SPARQL endpoint. Predicates become edge labels, so the semantics
 * of the OntoExhibit ontology are shown directly.
 */

import { executeSparql } from "./api";
import { parseEntityUri, normalizeDetailType } from "./entity-routing";

export interface GraphNode {
  id: string; // the resource IRI, or a synthetic key for literal nodes
  label: string;
  type: string; // normalized entity type (exhibition, artwork, actant, …) or "other"
  /** "entity" (an IRI resource) or "literal" (a data-property value). */
  kind?: "entity" | "literal";
  /** Whether this node's neighbours have already been loaded into the graph. */
  expanded?: boolean;
  /** True for the node the user started exploring from. */
  isFocus?: boolean;
}

export interface GraphEdge {
  source: string; // IRI
  target: string; // IRI
  label: string; // human-readable predicate
  predicate: string; // full predicate IRI
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

/** Entity types we give first-class colours/icons to (mirrors the home page). */
export const NODE_TYPE_COLORS: Record<string, string> = {
  exhibition: "#6366f1", // indigo
  artwork: "#a855f7", // purple
  actant: "#f97316", // orange
  institution: "#22c55e", // green
  catalog: "#f59e0b", // amber
  company: "#14b8a6", // teal
  other: "#64748b", // slate
  literal: "#9ca3af", // gray — data-property values
};

export function nodeColor(type: string): string {
  return NODE_TYPE_COLORS[type] ?? NODE_TYPE_COLORS.other;
}

/** True when a resource IRI is a reification sub-resource (e.g. .../exhibition_making,
 * .../residence, .../role) rather than a first-class entity. */
export function isIntermediateUri(uri: string): boolean {
  const parsed = parseEntityUri(uri);
  return !!parsed && parsed.id.split("/").filter(Boolean).length > 1;
}

/** Derive a normalized entity type from a resource IRI. */
export function typeFromUri(uri: string): string {
  const parsed = parseEntityUri(uri);
  if (parsed) {
    // Reification sub-resources carry a multi-segment id — they are structural
    // intermediate nodes, not entities, so colour them as "other".
    if (parsed.id.split("/").filter(Boolean).length > 1) return "other";
    return normalizeDetailType(parsed.type);
  }

  // Fall back to the fragment/path keyword for intermediate nodes
  // (roles, makings, places, dates, ontology classes…).
  const frag = uri.split(/[#/]/).filter(Boolean).pop()?.toLowerCase() ?? "";
  if (frag.includes("place") || frag.includes("site") || frag.includes("territor")) return "institution";
  if (frag.includes("work") || frag.includes("obra")) return "artwork";
  if (frag.includes("actant") || frag.includes("person") || frag.includes("actor")) return "actant";
  if (frag.includes("exhib")) return "exhibition";
  return "other";
}

function prettifySegment(segment: string): string {
  const decoded = decodeURIComponent(segment).replace(/[-_]/g, " ").trim();
  return decoded ? decoded.charAt(0).toUpperCase() + decoded.slice(1) : decoded;
}

/** Shorten a predicate IRI into a readable label, e.g. `…#hasCurator` → "has curator". */
export function shortenPredicate(predicate: string): string {
  let frag = predicate.split(/[#/]/).filter(Boolean).pop() ?? predicate;
  frag = frag.replace(/^P\d+_/, ""); // strip CIDOC-CRM codes like "P14_"
  frag = frag.replace(/_/g, " ");
  frag = frag.replace(/([a-z])([A-Z])/g, "$1 $2"); // split camelCase
  return frag.trim().toLowerCase();
}

/** Best-effort readable label from an IRI when rdfs:label is absent. For
 * intermediate sub-resources, use the trailing role segment (e.g. "Residence")
 * instead of the opaque hash id. */
export function labelFromUri(uri: string): string {
  const parsed = parseEntityUri(uri);
  if (parsed) {
    const segs = parsed.id.split("/").filter(Boolean);
    return prettifySegment(segs.length > 1 ? segs[segs.length - 1] : parsed.id);
  }
  const frag = uri.split(/[#/]/).filter(Boolean).pop() ?? uri;
  return prettifySegment(frag);
}

const PREFIXES = `PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>`;

/** Build the ego-network query for a focus resource. When `includeLiterals` is
 * set, a third branch returns the resource's data-property (literal) values. */
export function buildEgoNetworkQuery(focusUri: string, limit = 60, includeLiterals = false): string {
  const literalBranch = includeLiterals
    ? ` UNION {
    <${focusUri}> ?pred ?node .
    FILTER(isLiteral(?node))
    FILTER(?pred != rdfs:label)
    BIND("lit" AS ?dir)
  }`
    : "";
  return `${PREFIXES}
SELECT ?dir ?pred ?node ?nodeLabel WHERE {
  {
    <${focusUri}> ?pred ?node .
    FILTER(isIRI(?node))
    FILTER(?pred != rdf:type)
    BIND("out" AS ?dir)
  } UNION {
    ?node ?pred <${focusUri}> .
    FILTER(isIRI(?node))
    FILTER(?pred != rdf:type)
    BIND("in" AS ?dir)
  }${literalBranch}
  OPTIONAL { ?node rdfs:label ?nodeLabel }
}
LIMIT ${limit}`;
}

type EgoRow = {
  dir?: string;
  pred?: string;
  node?: string;
  nodeLabel?: string;
};

/** Synthetic id for a literal (data-property) node, unique per subject+predicate+value. */
function literalNodeId(subject: string, predicate: string, value: string): string {
  return `lit::${subject}::${predicate}::${value}`;
}

/**
 * Fetch the ego network of `focusUri` and return it as graph data, including the
 * focus node itself. `focusLabel` is used when the store has no rdfs:label.
 * Set `includeLiterals` to also pull the focus resource's data-property values.
 */
export async function fetchEgoNetwork(
  focusUri: string,
  focusLabel?: string,
  limit = 60,
  includeLiterals = false,
): Promise<GraphData> {
  const query = buildEgoNetworkQuery(focusUri, limit, includeLiterals);
  const res = await executeSparql(query);
  const rows: EgoRow[] = Array.isArray(res?.data) ? res.data : [];

  const nodes = new Map<string, GraphNode>();
  const edges: GraphEdge[] = [];
  const edgeKeys = new Set<string>();

  nodes.set(focusUri, {
    id: focusUri,
    label: focusLabel || labelFromUri(focusUri),
    type: typeFromUri(focusUri),
    kind: "entity",
    isFocus: true,
    expanded: true,
  });

  for (const row of rows) {
    const node = row.node;
    const pred = row.pred;
    if (!node || !pred) continue;

    // Literal data property → attribute node attached to the focus.
    if (row.dir === "lit") {
      const litId = literalNodeId(focusUri, pred, node);
      if (!nodes.has(litId)) {
        nodes.set(litId, { id: litId, label: node, type: "literal", kind: "literal" });
      }
      const key = `${focusUri}|${pred}|${litId}`;
      if (!edgeKeys.has(key)) {
        edgeKeys.add(key);
        edges.push({ source: focusUri, target: litId, label: shortenPredicate(pred), predicate: pred });
      }
      continue;
    }

    if (node === focusUri) continue;

    if (!nodes.has(node)) {
      nodes.set(node, {
        id: node,
        label: row.nodeLabel?.trim() || labelFromUri(node),
        type: typeFromUri(node),
        kind: "entity",
      });
    } else if (row.nodeLabel?.trim() && nodes.get(node)!.label === labelFromUri(node)) {
      nodes.get(node)!.label = row.nodeLabel.trim();
    }

    const source = row.dir === "in" ? node : focusUri;
    const target = row.dir === "in" ? focusUri : node;
    const key = `${source}|${pred}|${target}`;
    if (!edgeKeys.has(key)) {
      edgeKeys.add(key);
      edges.push({ source, target, label: shortenPredicate(pred), predicate: pred });
    }
  }

  return { nodes: Array.from(nodes.values()), edges };
}

/** Remove literal (attribute) nodes and their edges — used when the
 * "show attributes" toggle is off. */
export function stripLiterals(graph: GraphData): GraphData {
  const litIds = new Set(graph.nodes.filter((n) => n.kind === "literal").map((n) => n.id));
  if (litIds.size === 0) return graph;
  return {
    nodes: graph.nodes.filter((n) => n.kind !== "literal"),
    edges: graph.edges.filter((e) => !litIds.has(e.source) && !litIds.has(e.target)),
  };
}

export interface EntityHit {
  uri: string;
  label: string;
  type: string;
}

/** Escape a user string for safe inclusion inside a SPARQL string literal. */
function escapeSparqlLiteral(value: string): string {
  return value.replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/\n/g, " ");
}

/** Search named resources by a substring of their rdfs:label. */
export async function searchEntitiesByLabel(term: string, limit = 15): Promise<EntityHit[]> {
  const safe = escapeSparqlLiteral(term.trim());
  if (!safe) return [];
  const query = `${PREFIXES}
SELECT DISTINCT ?s ?label WHERE {
  ?s rdfs:label ?label .
  FILTER(isIRI(?s))
  FILTER(CONTAINS(LCASE(STR(?label)), LCASE("${safe}")))
}
ORDER BY STRLEN(STR(?label))
LIMIT ${limit}`;
  const res = await executeSparql(query);
  const rows: Array<{ s?: string; label?: string }> = Array.isArray(res?.data) ? res.data : [];
  return rows
    .filter((r) => r.s)
    .map((r) => ({ uri: r.s!, label: r.label?.trim() || labelFromUri(r.s!), type: typeFromUri(r.s!) }));
}

/** Merge newly fetched ego-network data into an existing graph (for expansion). */
export function mergeGraph(base: GraphData, addition: GraphData, expandedId: string): GraphData {
  const nodes = new Map<string, GraphNode>(base.nodes.map((n) => [n.id, n] as [string, GraphNode]));
  for (const n of addition.nodes) {
    const existing = nodes.get(n.id);
    if (!existing) {
      nodes.set(n.id, n);
    } else if (n.label && existing.label === labelFromUri(existing.id)) {
      existing.label = n.label;
    }
  }
  const marked = nodes.get(expandedId);
  if (marked) marked.expanded = true;

  const edgeKeys = new Set(base.edges.map((e) => `${e.source}|${e.predicate}|${e.target}`));
  const edges = [...base.edges];
  for (const e of addition.edges) {
    const key = `${e.source}|${e.predicate}|${e.target}`;
    if (!edgeKeys.has(key)) {
      edgeKeys.add(key);
      edges.push(e);
    }
  }
  return { nodes: Array.from(nodes.values()), edges };
}
