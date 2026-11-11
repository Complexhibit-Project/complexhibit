"use client";

import { useState } from "react";
import { Save, CheckCircle } from "lucide-react";
import { executeSparql } from "@/lib/api";
import { DownloadButton } from "@/components/ui/DownloadButton";
import { ExampleQuerySelector } from "@/components/sparql/ExampleQuerySelector";
import { SaveQueryModal } from "@/components/sparql/SaveQueryModal";
import { useAuth } from "@/hooks/useAuth";

export default function SparqlPage() {
  const { isAuthenticated } = useAuth();
  const [query, setQuery] = useState("SELECT * WHERE { ?s ?p ?o } LIMIT 10");
  const [results, setResults] = useState<Record<string, unknown>[] | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);

  const handleExecute = async () => {
    setLoading(true);
    setError("");
    setResults(null);
    try {
      const resp = await executeSparql(query);
      setResults(resp.data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  const handleExampleSelect = (selectedQuery: string) => {
    setQuery(selectedQuery);
    // Clear previous results when selecting a new query
    setResults(null);
    setError("");
  };

  const handleQuerySaved = () => {
    // Could refresh example queries list here if needed
  };

  return (
    <div className="max-w-7xl mx-auto p-6 lg:px-8">
      <h1 className="text-3xl font-bold mb-6 text-gray-900">SPARQL Query Endpoint</h1>
      <p className="mb-4 text-sm text-gray-500">
        Execute SPARQL queries against the Complexhibit Knowledge Graph.
      </p>

      {/* Example Query Selector */}
      <div className="mb-4">
        <ExampleQuerySelector onSelect={handleExampleSelect} />
      </div>

      {/* Query Textarea */}
      <div className="mb-4">
        <textarea
          className="w-full h-64 p-4 border border-gray-300 rounded-md font-mono text-sm bg-gray-50 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          spellCheck={false}
        />
      </div>

      {/* Action Buttons */}
      <div className="mb-6 flex items-center gap-4 flex-wrap">
        <button
          onClick={handleExecute}
          disabled={loading}
          className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50 font-medium transition-colors cursor-pointer"
        >
          {loading ? "Executing..." : "Execute Query"}
        </button>

        {/* Results count - inline with actions */}
        {results && results.length > 0 && (
          <div className="flex items-center gap-2 px-3 py-2 bg-emerald-50 text-emerald-700 rounded-lg text-sm font-medium border border-emerald-200">
            <CheckCircle className="h-4 w-4" />
            {results.length} result{results.length !== 1 ? 's' : ''}
          </div>
        )}

        {/* Download Button - only show when results exist */}
        {results && results.length > 0 && (
          <DownloadButton 
            data={results} 
            filename="sparql_results"
            sparqlQuery={query}
            disabled={loading}
          />
        )}

        {/* Save Query Button - only show for authenticated users */}
        {isAuthenticated && (
          <button
            onClick={() => setShowSaveModal(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm bg-violet-50 border border-violet-200 text-violet-700 hover:bg-violet-100 hover:border-violet-300 transition-all cursor-pointer"
          >
            <Save className="h-4 w-4" />
            Save Query
          </button>
        )}
      </div>

      {/* Save Query Modal */}
      {showSaveModal && (
        <SaveQueryModal
          query={query}
          onClose={() => setShowSaveModal(false)}
          onSaved={handleQuerySaved}
        />
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {/* Results Table */}
      {results && results.length > 0 && (
        <div className="overflow-x-auto shadow ring-1 ring-black/5 rounded-lg">
          <table className="min-w-full divide-y divide-gray-300">
            <thead className="bg-gray-50">
              <tr>
                {Object.keys(results[0]).map((header) => (
                  <th key={header} className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {results.map((row: Record<string, unknown>, i: number) => (
                <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  {Object.values(row).map((val: unknown, j: number) => (
                      <td key={j} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {(val as { value: string })?.value || String(val)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
       {results && results.length === 0 && (
          <p className="text-gray-500 italic">No results found.</p>
       )}
    </div>
  );
}
