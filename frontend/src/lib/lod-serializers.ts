import { buildCanonicalEntityUri } from "@/lib/entity-routing";

export type LodFormat = "jsonld" | "ttl" | "rdfxml";

const ONTO_BASE = "https://w3id.org/OntoExhibit#";

function escapeTurtleLiteral(value: string): string {
  return value
    .replace(/\\/g, "\\\\")
    .replace(/"/g, '\\"')
    .replace(/\n/g, "\\n")
    .replace(/\r/g, "\\r")
    .replace(/\t/g, "\\t");
}

function escapeXml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

function isUri(value: string): boolean {
  return /^https?:\/\//i.test(value) || /^urn:/i.test(value);
}

function normalizePredicate(key: string): string {
  if (/^https?:\/\//i.test(key)) return key;
  return `${ONTO_BASE}${key}`;
}

function objectToTriples(subject: string, properties: Record<string, unknown>) {
  const triples: Array<{ predicate: string; object: string; objectIsUri: boolean }> = [];

  for (const [key, rawValue] of Object.entries(properties)) {
    if (rawValue === null || rawValue === undefined) continue;
    const predicate = normalizePredicate(key);

    const values = Array.isArray(rawValue) ? rawValue : [rawValue];
    for (const value of values) {
      const object = String(value);
      triples.push({
        predicate,
        object,
        objectIsUri: isUri(object),
      });
    }
  }

  if (!triples.some((t) => t.predicate.endsWith("#uri"))) {
    triples.push({
      predicate: `${ONTO_BASE}uri`,
      object: subject,
      objectIsUri: true,
    });
  }

  return triples;
}

export function toTurtle(type: string, id: string, properties: Record<string, unknown>): string {
  const subject = buildCanonicalEntityUri(type, id);
  const triples = objectToTriples(subject, properties);
  const body = triples
    .map((t) => {
      const object = t.objectIsUri ? `<${t.object}>` : `"${escapeTurtleLiteral(t.object)}"`;
      return `<${subject}> <${t.predicate}> ${object} .`;
    })
    .join("\n");

  return `@prefix onto: <${ONTO_BASE}> .\n\n${body}\n`;
}

export function toJsonLd(type: string, id: string, properties: Record<string, unknown>): string {
  const subject = buildCanonicalEntityUri(type, id);
  const context: Record<string, string> = {
    onto: ONTO_BASE,
  };
  const graphNode: Record<string, unknown> = {
    "@id": subject,
  };

  for (const [key, value] of Object.entries(properties)) {
    if (value === null || value === undefined) continue;
    const fullKey = normalizePredicate(key);
    graphNode[fullKey] = value;
  }

  const data = {
    "@context": context,
    "@graph": [graphNode],
  };

  return JSON.stringify(data, null, 2);
}

export function toRdfXml(type: string, id: string, properties: Record<string, unknown>): string {
  const subject = buildCanonicalEntityUri(type, id);
  const triples = objectToTriples(subject, properties);

  const namespaces = new Map<string, string>();
  let nsIndex = 0;

  const splitPredicate = (uri: string): { ns: string; local: string } => {
    const hash = uri.lastIndexOf("#");
    const slash = uri.lastIndexOf("/");
    const idx = Math.max(hash, slash);
    const ns = idx >= 0 ? uri.slice(0, idx + 1) : `${ONTO_BASE}`;
    let local = idx >= 0 ? uri.slice(idx + 1) : uri;
    local = local.replace(/[^A-Za-z0-9_.-]/g, "_");
    if (!/^[A-Za-z_]/.test(local)) local = `p_${local}`;
    return { ns, local };
  };

  const predicateNodes = triples
    .map((t) => {
      const { ns, local } = splitPredicate(t.predicate);
      let prefix = namespaces.get(ns);
      if (!prefix) {
        prefix = `ns${nsIndex++}`;
        namespaces.set(ns, prefix);
      }

      if (t.objectIsUri) {
        return `<${prefix}:${local} rdf:resource="${escapeXml(t.object)}" />`;
      }
      return `<${prefix}:${local}>${escapeXml(t.object)}</${prefix}:${local}>`;
    })
    .join("\n    ");

  const nsAttrs = Array.from(namespaces.entries())
    .map(([ns, prefix]) => `xmlns:${prefix}="${escapeXml(ns)}"`)
    .join("\n  ");

  return `<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  ${nsAttrs}>
  <rdf:Description rdf:about="${escapeXml(subject)}">
    ${predicateNodes}
  </rdf:Description>
</rdf:RDF>
`;
}
