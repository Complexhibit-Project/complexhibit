const DETAIL_TYPE_ALIASES: Record<string, string> = {
  actor: "person",
  actant: "person",
  group: "person",
  human_actant: "person",
  work_manifestation: "artwork",
  obra: "artwork",
  museum: "institution",
  cultural_institution: "institution",
  art_center: "institution",
  cultural_center: "institution",
  exhibitionspace: "institution",
  interpretation_center: "institution",
  library: "institution",
  educational_institution: "institution",
  university: "institution",
  "foundation_(institution)": "institution",
};

const LIST_TYPE_ALIASES: Record<string, string> = {
  ...DETAIL_TYPE_ALIASES,
  site: "institution",
  territorialentity: "institution",
  territorial_entity: "institution",
};

const LISTABLE_TYPES = new Set([
  "exhibition",
  "artwork",
  "institution",
  "person",
  "catalog",
  "company",
]);

const W3ID_BASE = "https://w3id.org/OntoExhibit";

export function normalizeDetailType(type: string): string {
  const key = type.toLowerCase();
  return DETAIL_TYPE_ALIASES[key] || type;
}

export function normalizeListType(type: string): string | null {
  const key = type.toLowerCase();
  const candidate = LIST_TYPE_ALIASES[key] || key;
  return LISTABLE_TYPES.has(candidate) ? candidate : null;
}

export function getListTypeFromDetailType(type: string): string | null {
  return normalizeListType(type);
}

export function parseEntityUri(uri: string): { type: string; id: string } | null {
  if (!uri) return null;

  const idPathPrefix = `${W3ID_BASE}/id/`;
  if (uri.startsWith(idPathPrefix)) {
    const relative = uri.slice(idPathPrefix.length).replace(/^\/+/, "");
    const segments = relative.split("/").filter(Boolean);
    if (segments.length >= 2) {
      return {
        type: normalizeDetailType(segments[0]),
        id: segments.slice(1).join("/"),
      };
    }
  }

  const hashIndex = uri.indexOf("#");
  if (hashIndex < 0) return null;

  const fragment = uri.slice(hashIndex + 1).replace(/^\/+/, "");
  const segments = fragment.split("/").filter(Boolean);
  if (segments.length < 2) return null;

  const type = normalizeDetailType(segments[0]);
  const id = segments.slice(1).join("/");
  if (!id) return null;

  return { type, id };
}

export function buildDetailHref(type: string, id: string): string {
  const normalizedType = normalizeDetailType(type);
  return `/detail/${encodeURIComponent(normalizedType)}/${encodeURIComponent(id)}`;
}

export function buildResourceHref(type: string, id: string): string {
  const encodedType = encodeURIComponent(type);
  const encodedId = id
    .split("/")
    .filter(Boolean)
    .map((segment) => encodeURIComponent(segment))
    .join("/");
  return `/resource/${encodedType}/${encodedId}`;
}

export function buildCanonicalEntityUri(type: string, id: string): string {
  return `${W3ID_BASE}${buildResourceHref(type, id).replace("/resource", "/id")}`;
}

// Display/route types differ from the RDF URI fragment for some entities:
// the store uses #human_actant/… and #work_manifestation/… even though the UI
// routes them as "actant" / "artwork".
const RDF_URI_FRAGMENTS: Record<string, string> = {
  actant: "human_actant",
  actor: "human_actant",
  person: "human_actant",
  human_actant: "human_actant",
  artwork: "work_manifestation",
  obra: "work_manifestation",
  work_manifestation: "work_manifestation",
};

/** Map a display/route type to the fragment used in the resource's RDF IRI. */
export function rdfUriFragment(type: string): string {
  const key = type.toLowerCase();
  return RDF_URI_FRAGMENTS[key] ?? key;
}

/** Build the hash IRI of a resource as stored in the triple store. */
export function buildStoreUri(type: string, id: string): string {
  return `${W3ID_BASE}#${rdfUriFragment(type)}/${id}`;
}
