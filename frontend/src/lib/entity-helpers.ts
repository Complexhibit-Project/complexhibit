import { Exhibition, Artwork, Actor } from "@/lib/types";

// Helper to parse "Name:::URI|Name2:::URI2" format
export const parseComplexField = (value: string | undefined): string[] | null => {
  if (!value) return null;
  const parts = value.split('|')
    .map(part => part.split(':::')[0])
    .filter(Boolean);
  return parts.length > 0 ? parts : null;
};

// Helper to parse simple piped strings
export const parseSimpleList = (value: string | undefined): string[] | null => {
  if (!value) return null;
  const parts = value.split('|').filter(Boolean);
  return parts.length > 0 ? parts : null;
};

// Build extra info for cards based on entity type
// Build extra info for cards based on entity type
export const getCardExtra = (item: unknown, type: string): Record<string, string | string[]> => {
  const extra: Record<string, string | string[]> = {};
  
  if (['person', 'actant', 'human_actant', 'actor'].includes(type.toLowerCase())) {
    const actor = item as Actor;
    // Use arrays for consistent tag styling with exhibitions/artworks
    if (actor.birth_place_label) extra["Born in"] = [actor.birth_place_label];
    const itemAny = item as { 
      birth_date_label?: string; 
      death_date_label?: string;
      foundation_date_label?: string;
      foundation_place_label?: string;
      dissolution_date_label?: string;
    };
    if (itemAny.birth_date_label) extra["Born"] = [itemAny.birth_date_label];
    if (itemAny.death_date_label) extra["Died"] = [itemAny.death_date_label];
    // Cast to any for properties not in Actor interface but possibly present
    if (itemAny.foundation_date_label) extra["Founded"] = [itemAny.foundation_date_label];
    if (itemAny.foundation_place_label) extra["Founded in"] = [itemAny.foundation_place_label];
    if (itemAny.dissolution_date_label) extra["Dissolved"] = [itemAny.dissolution_date_label];
    if (actor.gender) extra["Gender"] = [actor.gender];
    // Activity is pipe-separated, so parse it as a list
    const activities = parseSimpleList(actor.activity);
    if (activities) extra["Activity"] = activities;
  } else if (type === 'exhibition') {
    const exhibition = item as Exhibition;
    if (exhibition.label_starting_date) extra["Opening"] = exhibition.label_starting_date;
    if (exhibition.label_ending_date) extra["Closing"] = exhibition.label_ending_date;
    
    const curators = parseComplexField(exhibition.curators);
    if (curators) extra["Curator"] = curators;

    const organizers = parseComplexField(exhibition.organizers);
    if (organizers) extra["Organizer"] = organizers;

    const funders = parseComplexField(exhibition.funders);
    if (funders) extra["Sponsor"] = funders;

    const themes = parseSimpleList(exhibition.theme_label);
    if (themes) extra["Theme"] = themes;

    const types = parseSimpleList(exhibition.type_label);
    if (types) extra["Type"] = types;

    if (exhibition.label_place) extra["Place"] = exhibition.label_place;

    // New fields
    // Cast to specific type if these fields are missing from Exhibition interface
    const exAny = item as {
      participating_actants?: string;
      exhibited_artworks?: string;
    };
    const actants = parseComplexField(exAny.participating_actants);
    const artworks = parseComplexField(exAny.exhibited_artworks);
    
    if (actants) extra["Participants"] = actants;
    if (artworks) extra["Artworks"] = artworks;
  } else if (type === 'artwork') {
    const artwork = item as Artwork;
    // Backend returns plural fields with "Name:::URI" format
    const authors = parseComplexField(artwork.authors);
    const owners = parseComplexField(artwork.owners);
    const exhibitions = parseComplexField(artwork.exhibitions);

    if (authors) extra["Artist"] = authors;
    if (artwork.label_starting_date) extra["Date"] = artwork.label_starting_date;
    // Cast to specific type if production_place is missing from Artwork interface
    const artAny = item as { production_place?: string };
    if (artAny.production_place) extra["Place"] = artAny.production_place;

    const types = parseSimpleList(artwork.type);
    if (types) extra["Type"] = types;

    if (owners) extra["Owner"] = owners;

    const topics = parseSimpleList(artwork.topic);
    if (topics) extra["Topic"] = topics;

    if (exhibitions) extra["Shown in"] = exhibitions;
  } else if (type === 'institution') {
    const instAny = item as {
      label_place?: string;
      institution_type?: string;
      apelation?: string;
      ownershipType?: string;
      headquarters_address?: string;
    };
    if (instAny.institution_type) extra["Type"] = [instAny.institution_type];
    if (instAny.apelation) extra["Alternative Name"] = [instAny.apelation];
    if (instAny.ownershipType) extra["Ownership"] = [instAny.ownershipType];
    if (instAny.headquarters_address) extra["Address"] = [instAny.headquarters_address];
    if (instAny.label_place) extra["Location"] = [instAny.label_place];
  } else if (type === 'catalog') {
    const catAny = item as {
      publication_date?: string;
      publication_place?: string;
    };
    if (catAny.publication_date) extra["Published"] = [catAny.publication_date];
    if (catAny.publication_place) extra["Place"] = [catAny.publication_place];
  } else if (type === 'company') {
    const compAny = item as {
      isic4_category?: string;
      size?: string;
      location?: string;
    };
    if (compAny.isic4_category) extra["Category"] = [compAny.isic4_category];
    if (compAny.size) extra["Size"] = [compAny.size];
    if (compAny.location) extra["Location"] = [compAny.location];
  }

  return extra;
};
