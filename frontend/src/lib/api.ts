import { API_URL } from "./config";

export { API_URL };

export async function fetchFromApi(endpoint: string, params: Record<string, string> = {}) {
  const url = new URL(`${API_URL}${endpoint}`);
  Object.keys(params).forEach((key) => url.searchParams.append(key, params[key]));

  const response = await fetch(url.toString(), {
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }

  return response.json();
}

export interface SemanticSearchResult {
  uri: string;
  type: string;
  label: string;
  label_type?: string;
  matched_property?: string;
  matched_label?: string;
  score?: string;
}

export async function semanticSearch(
  q: string,
  params: { entity_type?: string; limit?: string } = {}
): Promise<{ data: SemanticSearchResult[]; sparql?: string }> {
  const searchParams: Record<string, string> = { q };
  if (params.entity_type) searchParams.entity_type = params.entity_type;
  if (params.limit) searchParams.limit = params.limit;

  return fetchFromApi("/semantic_search", searchParams);
}

export async function getFromType(type: string, params: Record<string, string> = {}) {
  // Map frontend types to API endpoints
  let endpoint = "";
  if (type === 'exhibition') endpoint = '/all_exhibitions';
  else if (type === 'artwork') endpoint = '/all_artworks';
  else if (type === 'institution') endpoint = '/all_institutions';
  else if (type === 'catalog') endpoint = '/all_catalogs';
  else if (type === 'company') endpoint = '/all_companies';
  else if (type === 'actant' || type === 'actor' || type === 'human_actant' || type === 'person') endpoint = '/all_persons';
  else endpoint = `/get_object_any_type/${encodeURIComponent((type === 'person' ? 'human actant' : type).replace(/_/g, ' '))}`;

  return fetchFromApi(endpoint, params);
}

export async function getDataProperties(type: string, id: string) {
    // Fallback to generic object fetch
    return fetchFromApi(`/get_object_any_type/${type}/${id}`);
}

export async function getTypesFromId(type: string, id: string) {
  // We haven't implemented this specifically, but maybe object properties include type?
  // Or we can add a simple endpoint. For now, try generic.
  return fetchFromApi(`/get_object_any_type/${type}/${id}`); 
}

export async function getRolesPlayed(type: string, id: string) {
  // Fetch roles/exhibitions where this actor participated
  if (type === 'actor' || type === 'human_actant' || type === 'person' || type === 'actant') {
    return fetchFromApi(`/get_actor_roles/${id}`);
  }
  return Promise.resolve({ data: {} });
}

export async function getParticipants() {
    // Not implemented in backend yet
  return Promise.resolve({ data: {} });
}

export async function getArtworks() {
    // Not implemented in backend yet
  return Promise.resolve({ data: {} });
}

export async function getExhibitionMaking() {
    // Not implemented in backend yet
  return Promise.resolve({ data: {} });
}

export async function getDatesAndPlace(id: string) {
  // Covered by get_exhibition
  return fetchFromApi(`/get_exhibition/${id}`);
}

// Add more specific fetchers as needed based on views.py logic
export async function getGenericDetail(type: string, id: string) {
    return fetchFromApi(`/get_object_any_type/${type}/${id}`);
}

export async function getActorDetails(id: string) {
  return fetchFromApi(`/get_person/${id}`);
}

export async function getArtworkDetails(id: string) {
  return fetchFromApi(`/get_artwork/${id}`);
}

export async function getInstitutionExhibitions(id: string) {
  return fetchFromApi(`/get_institution_exhibitions/${id}`);
}

export async function getInstitutionDetails(id: string) {
  return fetchFromApi(`/get_institution/${id}`);
}

export async function getInstitutionLenderExhibitions(id: string) {
  return fetchFromApi(`/get_institution_lender_exhibitions/${id}`);
}

export async function getInstitutionOwnedArtworks(id: string) {
  return fetchFromApi(`/get_institution_owned_artworks/${id}`);
}

export async function getPersonCollaborators(id: string) {
  return fetchFromApi(`/get_person_collaborators/${id}`);
}

export async function getInstitutionCollaborators(id: string) {
  return fetchFromApi(`/get_institution_collaborators/${id}`);
}

export async function getPersonExecutivePositions(id: string) {
  return fetchFromApi(`/get_person_executive_positions/${id}`);
}

export async function getInstitutionExecutives(id: string) {
  return fetchFromApi(`/get_institution_executives/${id}`);
}

export async function getInstitutionParent(id: string) {
  return fetchFromApi(`/get_institution_parent/${id}`);
}

export async function getInstitutionChildren(id: string) {
  return fetchFromApi(`/get_institution_children/${id}`);
}

export async function executeSparql(query: string) {
  const url = new URL(`${API_URL}/sparql`);
  // Attach the auth token when present so authenticated users can run
  // INSERT/DELETE/UPDATE queries (the backend gates modifying queries on it).
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const response = await fetch(url.toString(), {
    method: 'POST',
    headers,
    body: JSON.stringify({ query })
  });
  if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error((errorData as { detail?: string }).detail || `API Error: ${response.statusText}`);
  }
  return response.json();
}

export async function submitReport(report: Record<string, unknown>) {
  const url = new URL(`${API_URL}/report`);
  const response = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(report)
  });
  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }
  return response.json();
}

// Count API functions
export async function getExhibitionsCount() {
  return fetchFromApi("/count_exhibitions");
}

export async function getArtworksCount() {
  return fetchFromApi("/count_artworks");
}

export async function getPersonsCount() {
  return fetchFromApi("/count_persons");
}

export async function getInstitutionsCount() {
  return fetchFromApi("/count_institutions");
}

export async function getCatalogsCount() {
  return fetchFromApi("/count_catalogs");
}

export async function getCompaniesCount() {
  return fetchFromApi("/count_companies");
}

// Catalog API functions
export async function getCatalogDetails(id: string) {
  return fetchFromApi(`/get_catalog/${id}`);
}

export async function getExhibitionCatalogs(id: string) {
  return fetchFromApi(`/get_exhibition_catalogs/${id}`);
}

export async function getProducerCatalogs(id: string) {
  return fetchFromApi(`/get_producer_catalogs/${id}`);
}

export async function getCatalogExhibitions(id: string) {
  return fetchFromApi(`/get_catalog_exhibitions/${id}`);
}

// Company API functions
export async function getCompanyDetails(id: string) {
  return fetchFromApi(`/get_company/${id}`);
}

export async function getCompanyMuseographerExhibitions(id: string) {
  return fetchFromApi(`/get_company_museographer_exhibitions/${id}`);
}

export async function getExhibitionMuseographers(id: string) {
  return fetchFromApi(`/get_exhibition_museographers/${id}`);
}

// Map API functions
export async function getMapEntities(types?: string[]) {
  const params = new URLSearchParams();
  if (types && types.length > 0) {
    types.forEach(type => params.append('types', type));
    return fetchFromApi(`/map/all?${params.toString()}`);
  }
  return fetchFromApi(`/map/all`);
}

export async function getMapMeta() {
  return fetchFromApi(`/map/meta`);
}

// Example Query API functions
export interface ExampleQueryResponse {
  id: number;
  name: string;
  description: string | null;
  query: string;
  category: string;
  user_id: number;
  username: string;
  created_at: string;
}

export async function getExampleQueries(): Promise<{ data: ExampleQueryResponse[] }> {
  const response = await fetch(`${API_URL}/example-queries`);
  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }
  const data = await response.json();
  return { data };
}

export async function createExampleQuery(
  name: string,
  description: string | null,
  query: string,
  category: string = 'custom'
): Promise<ExampleQueryResponse> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }
  
  const response = await fetch(`${API_URL}/example-queries`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ name, description, query, category })
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error((errorData as { detail?: string }).detail || `API Error: ${response.statusText}`);
  }
  
  return response.json();
}

export async function deleteExampleQuery(id: number): Promise<void> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }
  
  const response = await fetch(`${API_URL}/example-queries/${id}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error((errorData as { detail?: string }).detail || `API Error: ${response.statusText}`);
  }
}
