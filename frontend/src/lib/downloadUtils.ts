/**
 * Utility functions for downloading data in multiple formats.
 * Supports: CSV, JSON, HTML, RDF/XML, N-Triples
 */

/**
 * Convert array of objects to CSV string.
 * Handles proper escaping of values containing commas, quotes, and newlines.
 */
function convertToCSV(data: Record<string, unknown>[]): string {
  if (!data || data.length === 0) return '';

  // Get all unique headers from the data
  const headers = new Set<string>();
  data.forEach(row => {
    Object.keys(row).forEach(key => headers.add(key));
  });
  const headerArray = Array.from(headers);

  // Create CSV content
  const csvRows: string[] = [];

  // Header row
  csvRows.push(headerArray.map(header => escapeCSVValue(header)).join(','));

  // Data rows
  data.forEach(row => {
    const values = headerArray.map(header => {
      const value = row[header];
      // Handle nested objects with 'value' property (SPARQL results format)
      if (value && typeof value === 'object' && 'value' in (value as object)) {
        return escapeCSVValue(String((value as { value: unknown }).value));
      }
      return escapeCSVValue(value === null || value === undefined ? '' : String(value));
    });
    csvRows.push(values.join(','));
  });

  return csvRows.join('\n');
}

/**
 * Escape a value for CSV format.
 * Wraps in quotes if contains comma, quote, or newline.
 */
function escapeCSVValue(value: string): string {
  if (value.includes(',') || value.includes('"') || value.includes('\n') || value.includes('\r')) {
    // Double up any quotes and wrap in quotes
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

/**
 * Trigger a file download in the browser.
 */
function triggerDownload(content: string, filename: string, mimeType: string): void {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Clean SPARQL results data (extract 'value' from nested objects).
 */
function cleanData(data: Record<string, unknown>[]): Record<string, unknown>[] {
  return data.map(row => {
    const cleaned: Record<string, unknown> = {};
    Object.entries(row).forEach(([key, value]) => {
      if (value && typeof value === 'object' && 'value' in (value as object)) {
        cleaned[key] = (value as { value: unknown }).value;
      } else {
        cleaned[key] = value;
      }
    });
    return cleaned;
  });
}

/**
 * Escape HTML special characters.
 */
function escapeHTML(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Download data as a CSV file.
 */
export function downloadAsCSV(
  data: Record<string, unknown>[], 
  filename: string, 
  sparqlQuery?: string
): void {
  let csv = convertToCSV(data);
  
  // Add query as comment at the top if provided
  if (sparqlQuery) {
    const queryComment = `# SPARQL Query:\n# ${sparqlQuery.replace(/\n/g, '\n# ')}\n#\n`;
    csv = queryComment + csv;
  }
  
  triggerDownload(csv, `${filename}.csv`, 'text/csv;charset=utf-8;');
}

/**
 * Download data as a JSON file.
 */
export function downloadAsJSON(
  data: Record<string, unknown>[], 
  filename: string,
  sparqlQuery?: string
): void {
  const cleanedData = cleanData(data);
  
  const output = sparqlQuery 
    ? { query: sparqlQuery, results: cleanedData }
    : cleanedData;
  
  const json = JSON.stringify(output, null, 2);
  triggerDownload(json, `${filename}.json`, 'application/json');
}

/**
 * Download data as an HTML file with styling.
 */
export function downloadAsHTML(
  data: Record<string, unknown>[], 
  filename: string,
  sparqlQuery?: string
): void {
  const cleanedData = cleanData(data);
  const headers = data.length > 0 ? Object.keys(data[0]) : [];
  
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SPARQL Results - ${escapeHTML(filename)}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f3f4f6; padding: 2rem; }
    .container { max-width: 1200px; margin: 0 auto; }
    h1 { color: #1f2937; margin-bottom: 1rem; font-size: 1.5rem; }
    .meta { color: #6b7280; margin-bottom: 1.5rem; font-size: 0.875rem; }
    .query-section { background: #1e1e1e; color: #d4d4d4; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1.5rem; overflow-x: auto; }
    .query-section h3 { color: #818cf8; margin-bottom: 0.5rem; font-size: 0.875rem; }
    .query-section pre { font-family: 'Fira Code', monospace; font-size: 0.75rem; white-space: pre-wrap; word-break: break-word; }
    table { width: 100%; border-collapse: collapse; background: white; border-radius: 0.5rem; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    th { background: #f9fafb; color: #374151; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #e5e7eb; }
    td { padding: 0.75rem 1rem; border-bottom: 1px solid #e5e7eb; font-size: 0.875rem; color: #4b5563; word-break: break-word; max-width: 300px; }
    tr:nth-child(even) { background: #f9fafb; }
    tr:hover { background: #f3f4f6; }
    .footer { margin-top: 1.5rem; text-align: center; color: #9ca3af; font-size: 0.75rem; }
  </style>
</head>
<body>
  <div class="container">
    <h1>SPARQL Query Results</h1>
    <p class="meta">Exported on ${new Date().toLocaleString()} • ${data.length} results</p>
    ${sparqlQuery ? `
    <div class="query-section">
      <h3>SPARQL Query</h3>
      <pre>${escapeHTML(sparqlQuery)}</pre>
    </div>
    ` : ''}
    <table>
      <thead>
        <tr>
          ${headers.map(h => `<th>${escapeHTML(h)}</th>`).join('')}
        </tr>
      </thead>
      <tbody>
        ${cleanedData.map(row => `
        <tr>
          ${headers.map(h => `<td>${escapeHTML(String(row[h] ?? ''))}</td>`).join('')}
        </tr>
        `).join('')}
      </tbody>
    </table>
    <div class="footer">Generated by Complexhibit SPARQL Endpoint</div>
  </div>
</body>
</html>`;
  
  triggerDownload(html, `${filename}.html`, 'text/html;charset=utf-8');
}

/**
 * Download data as RDF/XML.
 * Creates a simple RDF representation with each row as a resource.
 */
export function downloadAsRDF(
  data: Record<string, unknown>[], 
  filename: string,
  sparqlQuery?: string
): void {
  const cleanedData = cleanData(data);
  
  let rdf = `<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
         xmlns:result="http://www.w3.org/2005/sparql-results#">
`;
  
  if (sparqlQuery) {
    rdf += `  <!-- SPARQL Query:\n${sparqlQuery.split('\n').map(l => '       ' + l).join('\n')}\n  -->\n`;
  }
  
  cleanedData.forEach((row, index) => {
    rdf += `  <result:binding rdf:about="result:row${index + 1}">\n`;
    Object.entries(row).forEach(([key, value]) => {
      const escapedValue = escapeHTML(String(value ?? ''));
      rdf += `    <result:${key}>${escapedValue}</result:${key}>\n`;
    });
    rdf += `  </result:binding>\n`;
  });
  
  rdf += `</rdf:RDF>`;
  
  triggerDownload(rdf, `${filename}.rdf`, 'application/rdf+xml');
}

/**
 * Download data as N-Triples.
 */
export function downloadAsNTriples(
  data: Record<string, unknown>[], 
  filename: string,
  sparqlQuery?: string
): void {
  const cleanedData = cleanData(data);
  let ntriples = '';
  
  if (sparqlQuery) {
    ntriples += `# SPARQL Query:\n# ${sparqlQuery.replace(/\n/g, '\n# ')}\n#\n`;
  }
  
  cleanedData.forEach((row, index) => {
    const subject = `<http://complexhibit.uma.es/results/row${index + 1}>`;
    Object.entries(row).forEach(([key, value]) => {
      const predicate = `<http://www.w3.org/2005/sparql-results#${key}>`;
      // Escape special chars in literal
      const escapedValue = String(value ?? '')
        .replace(/\\/g, '\\\\')
        .replace(/"/g, '\\"')
        .replace(/\n/g, '\\n')
        .replace(/\r/g, '\\r');
      const object = `"${escapedValue}"`;
      ntriples += `${subject} ${predicate} ${object} .\n`;
    });
  });
  
  triggerDownload(ntriples, `${filename}.nt`, 'application/n-triples');
}

/**
 * Get a timestamp-based filename prefix.
 */
export function getTimestampFilename(prefix: string): string {
  const now = new Date();
  const timestamp = now.toISOString().replace(/[:.]/g, '-').slice(0, 19);
  return `${prefix}_${timestamp}`;
}
