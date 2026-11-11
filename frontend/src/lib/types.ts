/**
 * TypeScript interfaces for API responses and domain entities.
 * 
 * These types provide type safety and better IDE support throughout the frontend.
 */

// ====================
// Base Types
// ====================

/** Base entity with URI and label */
export interface Entity {
  uri: string;
  label: string;
  description?: string;
  abstract?: string;
  image?: string;
  img?: string;
  title?: string;
  entity_type?: string;
}

/** Linked entity from GROUP_CONCAT fields */
export interface LinkedEntity {
  label: string;
  uri: string | null;
}

/** Paginated API response */
export interface PaginatedResponse<T> {
  data: T[];
  next_cursor: string | null;
}

/** Detail API response with optional SPARQL query */
export interface DetailResponse<T> {
  data: T[];
  sparql?: string;
}

// ====================
// Exhibition Types
// ====================

export interface Exhibition extends Entity {
  label_starting_date?: string;
  label_ending_date?: string;
  label_place?: string;
  place_uri?: string;
  venue_label?: string;
  venue_uri?: string;
  theme_label?: string;
  type_label?: string;
  curator_name?: string;
  access?: string;
  lat?: string;
  long?: string;
  // Linked entities (GROUP_CONCAT format: "label:::uri|label:::uri")
  curators?: string;
  organizers?: string;
  funders?: string;
  lenders?: string;
  exhibitors?: string;
  artworks?: string;
}

export interface ExhibitionListItem extends Entity {
  label_starting_date?: string;
  label_ending_date?: string;
  label_place?: string;
  curator_name?: string;
  theme_label?: string;
  type_label?: string;
}

// ====================
// Actor/Person Types
// ====================

export interface Actor extends Entity {
  gender?: string;
  birth_date?: string;
  death_date?: string;
  birth_place_label?: string;
  place_uri?: string;
  activity?: string;
  label_date?: string | string[];
  label_place?: string | string[];
}

export interface ActorListItem extends Entity {
  birth_place_label?: string;
  birth_date_label?: string;
  death_date_label?: string;
  gender?: string;
  activity?: string;
}

// ====================
// Artwork Types
// ====================

export interface Artwork extends Entity {
  label_starting_date?: string;
  type?: string;
  topic?: string;
  author?: string;
  author_uri?: string;
  owner?: string;
  owner_uri?: string;
  exhibition?: string;
  exhibition_uri?: string;
  // GROUP_CONCAT fields
  authors?: string;
  owners?: string;
  exhibitions?: string;
}

export interface ArtworkListItem extends Entity {
  author?: string;
  label_starting_date?: string;
  type?: string;
  owner?: string;
  topic?: string;
}

// ====================
// Institution Types
// ====================

export interface Institution extends Entity {
  apelation?: string;
  label_place?: string;
  place_uri?: string;
}

export interface InstitutionListItem extends Entity {
  label_place?: string;
}

// ====================
// Filter Types
// ====================

export interface FilterConfig {
  key: string;
  type: 'text' | 'number' | 'select' | 'async_select' | 'date' | 'exclusive_radio' | 'date_segments';
  placeholder: string;
  optionsKey?: string;
  width?: string;
  entityType?: string;
}

export interface FilterOptions {
  [key: string]: string[];
}

// ====================
// Role Types
// ====================

export interface RoleItem {
  uri: string;
  label: string;
  type: string;
}

export interface RolesByType {
  [roleType: string]: RoleItem[];
}

// ====================
// API Response Types
// ====================

export interface CountResponse {
  data: { count: number };
  message: string;
}

export interface ErrorResponse {
  error_code: string;
  error_message: string;
  error_details?: Record<string, unknown>;
}

export interface SparqlResult {
  results: {
    bindings: Array<Record<string, { type: string; value: string }>>;
  };
}
