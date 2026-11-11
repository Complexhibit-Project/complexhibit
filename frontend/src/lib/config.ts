/**
 * Centralized runtime configuration.
 *
 * `API_URL` is resolved once here and imported everywhere else, so the backend
 * endpoint never drifts between modules. On the server we prefer `API_URL`
 * (internal Docker network name), on the client we use the public variable.
 */
export const API_URL: string =
  (typeof window === "undefined" && process.env.API_URL)
    ? process.env.API_URL
    : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1");

/** Base IRI of the OntoExhibit ontology. */
export const ONTOLOGY_BASE = "https://w3id.org/OntoExhibit#";
