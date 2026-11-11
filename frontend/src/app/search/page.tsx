"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import type { ElementType } from "react";
import {
  ArrowRight,
  Building2,
  Calendar,
  Database,
  FileText,
  Image as ImageIcon,
  Loader2,
  Search,
  Sparkles,
  Users,
} from "lucide-react";

import { semanticSearch, SemanticSearchResult } from "@/lib/api";
import { buildDetailHref, parseEntityUri } from "@/lib/entity-routing";
import { cleanLabel } from "@/lib/utils";

const SEARCH_SCOPES = [
  { value: "", label: "All", icon: Database },
  { value: "exhibition", label: "Exhibitions", icon: Calendar },
  { value: "artwork", label: "Artworks", icon: ImageIcon },
  { value: "institution", label: "Institutions", icon: Building2 },
  { value: "actant", label: "People & Groups", icon: Users },
  { value: "catalog", label: "Catalogs", icon: FileText },
];

const TYPE_STYLE: Record<string, { label: string; icon: ElementType; color: string }> = {
  exhibition: { label: "Exhibition", icon: Calendar, color: "text-blue-700 bg-blue-50 border-blue-200" },
  artwork: { label: "Artwork", icon: ImageIcon, color: "text-fuchsia-700 bg-fuchsia-50 border-fuchsia-200" },
  institution: { label: "Institution", icon: Building2, color: "text-emerald-700 bg-emerald-50 border-emerald-200" },
  actant: { label: "Actor", icon: Users, color: "text-orange-700 bg-orange-50 border-orange-200" },
  catalog: { label: "Catalog", icon: FileText, color: "text-amber-700 bg-amber-50 border-amber-200" },
  company: { label: "Company", icon: Building2, color: "text-teal-700 bg-teal-50 border-teal-200" },
};

function resultHref(result: SemanticSearchResult) {
  const parsed = parseEntityUri(result.uri);
  if (parsed) return buildDetailHref(parsed.type || result.type, parsed.id);

  const id = result.uri.split("/").pop() || result.uri.split("#").pop() || "";
  return buildDetailHref(result.type, id);
}

function readableMatch(value?: string): string {
  if (!value) return "semantic context";
  if (value === "Name or title") return "title or name";
  if (value.startsWith("Related ")) return `related ${readableMatch(value.replace(/^Related\s+/, ""))}`;
  if (value.startsWith("Linked by ")) return `linked by ${readableMatch(value.replace(/^Linked by\s+/, ""))}`;

  return value
    .replace(/_/g, " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .trim();
}

function matchBadge(result: SemanticSearchResult) {
  const score = Number(result.score || 0);
  const property = result.matched_property || "";
  const matchLabel = cleanLabel(result.matched_label || result.label || "");

  if (property === "Name or title") {
    return {
      label: score >= 120 ? "Title match" : "Name match",
      title: `Matched the title or name: ${matchLabel}. Ranking: title/name match starts at 100 points, with +20 when the full query phrase appears in the matched text.`,
    };
  }

  if (property.startsWith("Related ")) {
    return {
      label: "Related match",
      title: `Matched a connected entity through ${readableMatch(property)}: ${matchLabel}. Ranking: related entity matches start at 70 points, with +20 for a full query phrase match.`,
    };
  }

  if (property.startsWith("Linked by ")) {
    return {
      label: "Inbound match",
      title: `Matched an entity that links to this result through ${readableMatch(property)}: ${matchLabel}. Ranking: inbound relation matches start at 45 points, with +20 for a full query phrase match.`,
    };
  }

  return {
    label: "Data match",
    title: `Matched the ${readableMatch(property)} value: ${matchLabel}. Ranking: data-field matches start at 55 points, with +20 for a full query phrase match.`,
  };
}

function SearchResultCard({ result }: { result: SemanticSearchResult }) {
  const style = TYPE_STYLE[result.type] || TYPE_STYLE.exhibition;
  const Icon = style.icon;
  const badge = matchBadge(result);

  return (
    <Link
      href={resultHref(result)}
      className="group flex min-h-48 flex-col rounded-lg border border-gray-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-indigo-300 hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-3">
        <span className={`inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 text-xs font-semibold ${style.color}`}>
          <Icon className="h-3.5 w-3.5" />
          {style.label}
        </span>
        {result.score && (
          <span
            className="rounded-md bg-gray-100 px-2 py-1 text-xs font-medium text-gray-700"
            title={badge.title}
            aria-label={badge.title}
          >
            {badge.label}
          </span>
        )}
      </div>

      <h2 className="mt-4 line-clamp-2 text-lg font-semibold leading-6 text-gray-950 group-hover:text-indigo-700">
        {cleanLabel(result.label || "Untitled")}
      </h2>

      <div className="mt-4 space-y-2 text-sm text-gray-600">
        <p className="line-clamp-1">
          <span className="font-medium text-gray-800">Matched {readableMatch(result.matched_property)}:</span>{" "}
          {cleanLabel(result.matched_label || result.label || "")}
        </p>
        <p className="line-clamp-1 font-mono text-xs text-gray-400">{result.uri}</p>
      </div>

      <div className="mt-auto flex items-center pt-5 text-sm font-semibold text-indigo-700">
        Open detail
        <ArrowRight className="ml-2 h-4 w-4 transition group-hover:translate-x-0.5" />
      </div>
    </Link>
  );
}

export default function SearchPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q") || "";
  const initialScope = searchParams.get("entity_type") || "";

  const [query, setQuery] = useState(initialQuery);
  const [scope, setScope] = useState(initialScope);
  const [results, setResults] = useState<SemanticSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasSearched, setHasSearched] = useState(false);

  const selectedScope = useMemo(
    () => SEARCH_SCOPES.find((item) => item.value === scope) || SEARCH_SCOPES[0],
    [scope]
  );

  const runSearch = useCallback(
    async (nextQuery: string, nextScope: string, updateUrl = true) => {
      const trimmed = nextQuery.trim();
      setQuery(nextQuery);
      setScope(nextScope);

      if (!trimmed) {
        setResults([]);
        setHasSearched(false);
        setError("");
        if (updateUrl) router.replace("/search");
        return;
      }

      setIsLoading(true);
      setError("");
      setHasSearched(true);

      try {
        const response = await semanticSearch(trimmed, {
          entity_type: nextScope || undefined,
          limit: "48",
        });
        setResults(Array.isArray(response.data) ? response.data : []);

        if (updateUrl) {
          const params = new URLSearchParams({ q: trimmed });
          if (nextScope) params.set("entity_type", nextScope);
          router.replace(`/search?${params.toString()}`);
        }
      } catch (err) {
        setResults([]);
        setError(err instanceof Error ? err.message : "Search failed");
      } finally {
        setIsLoading(false);
      }
    },
    [router]
  );

  useEffect(() => {
    if (initialQuery) {
      runSearch(initialQuery, initialScope, false);
    }
  }, [initialQuery, initialScope, runSearch]);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    runSearch(query, scope);
  };

  return (
    <main className="bg-gray-50">
      <section className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="max-w-3xl">
            <div className="mb-4 inline-flex items-center gap-2 rounded-md border border-indigo-200 bg-indigo-50 px-3 py-1 text-sm font-medium text-indigo-700">
              <Sparkles className="h-4 w-4" />
              Semantic search
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-gray-950 sm:text-4xl">
              Search the collection
            </h1>
          </div>

          <form onSubmit={handleSubmit} className="mt-8">
            <div className="flex flex-col gap-3 lg:flex-row">
              <div className="relative flex-1">
                <label htmlFor="semantic-search" className="sr-only">
                  Search terms
                </label>
                <Search className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input
                  id="semantic-search"
                  type="search"
                  className="block h-12 w-full rounded-lg border border-gray-300 bg-white pl-12 pr-4 text-base text-gray-950 shadow-sm outline-none transition placeholder:text-gray-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200"
                  placeholder="Search names, places, themes, dates, roles..."
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                />
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-indigo-600 px-6 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                Search
              </button>
            </div>

            <div className="mt-4 flex flex-wrap gap-2" aria-label="Search scope">
              {SEARCH_SCOPES.map((item) => {
                const Icon = item.icon;
                const isActive = selectedScope.value === item.value;

                return (
                  <button
                    key={item.value || "all"}
                    type="button"
                    onClick={() => runSearch(query, item.value)}
                    className={`inline-flex h-9 items-center gap-2 rounded-md border px-3 text-sm font-medium transition ${
                      isActive
                        ? "border-indigo-600 bg-indigo-600 text-white"
                        : "border-gray-300 bg-white text-gray-700 hover:border-indigo-300 hover:text-indigo-700"
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </button>
                );
              })}
            </div>
          </form>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-950">
              {hasSearched ? `${results.length} results` : "Ready to search"}
            </h2>
            {hasSearched && (
              <p className="text-sm text-gray-500">
                Scope: {selectedScope.label}
              </p>
            )}
          </div>
          {error && (
            <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </p>
          )}
        </div>

        {isLoading ? (
          <div className="flex h-48 items-center justify-center rounded-lg border border-dashed border-gray-300 bg-white text-indigo-700">
            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            Searching
          </div>
        ) : hasSearched && results.length === 0 && !error ? (
          <div className="rounded-lg border border-dashed border-gray-300 bg-white p-10 text-center text-gray-500">
            No results found.
          </div>
        ) : results.length > 0 ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {results.map((result) => (
              <SearchResultCard key={`${result.uri}-${result.type}-${result.matched_property}`} result={result} />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {SEARCH_SCOPES.slice(1, 4).map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.value}
                  type="button"
                  onClick={() => setScope(item.value)}
                  className="flex items-center gap-3 rounded-lg border border-gray-200 bg-white p-5 text-left shadow-sm transition hover:border-indigo-300 hover:text-indigo-700"
                >
                  <span className="flex h-10 w-10 items-center justify-center rounded-md bg-gray-100 text-gray-600">
                    <Icon className="h-5 w-5" />
                  </span>
                  <span className="font-semibold text-gray-900">{item.label}</span>
                </button>
              );
            })}
          </div>
        )}
      </section>
    </main>
  );
}
