import { NextRequest, NextResponse } from "next/server";
import { buildCanonicalEntityUri, buildDetailHref } from "@/lib/entity-routing";
import { LodFormat, toJsonLd, toRdfXml, toTurtle } from "@/lib/lod-serializers";

const API_URL =
  process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

function parseResourcePath(rawPath: string[]): { type: string; id: string; formatFromExt?: LodFormat } | null {
  if (!rawPath || rawPath.length < 2) return null;

  const cloned = [...rawPath];
  const last = cloned[cloned.length - 1];

  let formatFromExt: LodFormat | undefined;
  if (last.endsWith(".jsonld")) {
    formatFromExt = "jsonld";
    cloned[cloned.length - 1] = last.slice(0, -7);
  } else if (last.endsWith(".ttl")) {
    formatFromExt = "ttl";
    cloned[cloned.length - 1] = last.slice(0, -4);
  } else if (last.endsWith(".rdf") || last.endsWith(".xml")) {
    formatFromExt = "rdfxml";
    cloned[cloned.length - 1] = last.replace(/\.(rdf|xml)$/i, "");
  }

  const cleaned = cloned.filter(Boolean).map((segment) => decodeURIComponent(segment));
  if (cleaned.length < 2) return null;

  return {
    type: cleaned[0],
    id: cleaned.slice(1).join("/"),
    formatFromExt,
  };
}

function negotiateFormat(request: NextRequest, ext?: LodFormat): LodFormat | "html" {
  if (ext) return ext;

  const qp = request.nextUrl.searchParams.get("format")?.toLowerCase();
  if (qp === "ttl" || qp === "turtle") return "ttl";
  if (qp === "rdf" || qp === "rdfxml" || qp === "xml") return "rdfxml";
  if (qp === "jsonld" || qp === "ld+json") return "jsonld";
  if (qp === "html") return "html";

  const accept = request.headers.get("accept")?.toLowerCase() || "";
  if (accept.includes("text/turtle")) return "ttl";
  if (accept.includes("application/rdf+xml")) return "rdfxml";
  if (accept.includes("application/ld+json")) return "jsonld";
  return "html";
}

async function fetchEntityProperties(type: string, id: string) {
  const encodedType = encodeURIComponent(type);
  const encodedId = encodeURIComponent(id);
  const url = `${API_URL}/get_object_any_type/${encodedType}/${encodedId}`;

  const response = await fetch(url, {
    headers: { Accept: "application/json" },
    cache: "no-store",
  });

  if (!response.ok) return null;
  const data = (await response.json()) as { data?: Array<Record<string, unknown>> };
  return Array.isArray(data.data) && data.data.length > 0 ? data.data[0] : null;
}

export async function GET(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const params = await context.params;
  const parsed = parseResourcePath(params.path || []);
  if (!parsed) {
    return new NextResponse("Invalid resource path", { status: 400 });
  }

  const format = negotiateFormat(request, parsed.formatFromExt);
  if (format === "html") {
    const detailHref = buildDetailHref(parsed.type, parsed.id);
    const resourcePath = `/resource/${params.path.map(encodeURIComponent).join("/")}`;
    const target = new URL(detailHref, request.url);
    target.searchParams.set("from", resourcePath);
    return NextResponse.redirect(target, 303);
  }

  const properties = await fetchEntityProperties(parsed.type, parsed.id);
  if (!properties) {
    return new NextResponse("Resource not found", { status: 404 });
  }

  if (format === "ttl") {
    return new NextResponse(toTurtle(parsed.type, parsed.id, properties), {
      headers: {
        "Content-Type": "text/turtle; charset=utf-8",
        "Content-Location": buildCanonicalEntityUri(parsed.type, parsed.id),
      },
    });
  }

  if (format === "rdfxml") {
    return new NextResponse(toRdfXml(parsed.type, parsed.id, properties), {
      headers: {
        "Content-Type": "application/rdf+xml; charset=utf-8",
        "Content-Location": buildCanonicalEntityUri(parsed.type, parsed.id),
      },
    });
  }

  return new NextResponse(toJsonLd(parsed.type, parsed.id, properties), {
    headers: {
      "Content-Type": "application/ld+json; charset=utf-8",
      "Content-Location": buildCanonicalEntityUri(parsed.type, parsed.id),
    },
  });
}
