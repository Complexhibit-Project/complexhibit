/**
 * Artwork-specific detail components.
 */

import { cleanLabel } from "@/lib/utils";
import { 
  SidebarCard, 
  SectionHeader, 
  SectionWrapper, 
  EntityList, 
  DefinitionList,
  parseLinkedEntities 
} from "./DetailUtils";

interface ArtworkData {
  label?: string;
  label_starting_date?: string;
  label_ending_date?: string;
  type?: string;
  topic?: string;
  apelation?: string;
  production_place?: string;
  author?: string;
  author_uri?: string;
  authors?: string;
  owner?: string;
  owner_uri?: string;
  owners?: string;
  exhibition?: string;
  exhibition_uri?: string;
  exhibitions?: string;
}

interface ArtworkRelationsSidebarProps {
  artworkData: ArtworkData[];
}

export function ArtworkRelationsSidebar({ artworkData }: ArtworkRelationsSidebarProps) {
  if (!artworkData || artworkData.length === 0) return null;
  
  const artwork = artworkData[0];
  
  // Handle both GROUP_CONCAT format (authors) and flat format (author, author_uri)
  let authors = parseLinkedEntities(artwork?.authors);
  if (authors.length === 0 && artwork?.author && artwork?.author_uri) {
    authors = [{ label: artwork.author, uri: artwork.author_uri }];
  }
  
  let owners = parseLinkedEntities(artwork?.owners);
  if (owners.length === 0 && artwork?.owner && artwork?.owner_uri) {
    owners = [{ label: artwork.owner, uri: artwork.owner_uri }];
  }
  
  let exhibitions = parseLinkedEntities(artwork?.exhibitions);
  if (exhibitions.length === 0 && artwork?.exhibition && artwork?.exhibition_uri) {
    exhibitions = [{ label: artwork.exhibition, uri: artwork.exhibition_uri }];
  }
  
  const hasAuthors = authors.length > 0;
  const hasOwners = owners.length > 0;
  const hasExhibitions = exhibitions.length > 0;
  
  // Only render if there are relationships
  if (!hasAuthors && !hasOwners && !hasExhibitions) return null;
  
  return (
    <>
      {/* Authors */}
      {hasAuthors && (
        <SidebarCard title="Author(s)">
          <DefinitionList>
            <EntityList 
              label="Artists" 
              entities={authors} 
              colorClass="text-amber-600 hover:text-amber-800"
            />
          </DefinitionList>
        </SidebarCard>
      )}
      
      {/* Owners */}
      {hasOwners && (
        <SidebarCard title="Owner(s)">
          <DefinitionList>
            <EntityList 
              label="Owners" 
              entities={owners} 
              colorClass="text-emerald-600 hover:text-emerald-800"
            />
          </DefinitionList>
        </SidebarCard>
      )}
      
      {/* Exhibitions */}
      {hasExhibitions && (
        <SidebarCard title="Displayed At">
          <DefinitionList>
            <EntityList 
              label="Exhibitions" 
              entities={exhibitions} 
              colorClass="text-indigo-600 hover:text-indigo-800"
            />
          </DefinitionList>
        </SidebarCard>
      )}
    </>
  );
}

interface ArtworkDetailsProps {
  artworkData: ArtworkData[];
}

export function ArtworkDetails({ artworkData }: ArtworkDetailsProps) {
  if (!artworkData || artworkData.length === 0) return null;
  
  const artwork = artworkData[0];
  const types = artwork?.type?.split('|').filter(Boolean) || [];
  const topics = artwork?.topic?.split('|').filter(Boolean) || [];
  
  return (
    <section>
      <SectionHeader title="Artwork Details" colorClass="bg-amber-500" />
      <SectionWrapper>
        <div className="grid gap-4">
          <div className="space-y-4">
            {/* Alternative Name */}
            {artwork?.apelation && (
              <div className="flex flex-col">
                <span className="text-xs font-semibold text-gray-500 uppercase">Alternative Name</span>
                <span className="text-gray-900">{artwork.apelation}</span>
              </div>
            )}
            
            {/* Creation Date */}
            {(artwork?.label_starting_date || artwork?.label_ending_date) && (
              <div className="flex flex-col">
                <span className="text-xs font-semibold text-gray-500 uppercase">Creation Date</span>
                <span className="text-gray-900">
                  {artwork.label_starting_date}
                  {artwork.label_starting_date && artwork.label_ending_date && " - "}
                  {artwork.label_ending_date}
                </span>
              </div>
            )}
            
            {/* Production Place */}
            {artwork?.production_place && (
              <div className="flex flex-col">
                <span className="text-xs font-semibold text-gray-500 uppercase">Place of Creation</span>
                <span className="text-gray-900">{artwork.production_place}</span>
              </div>
            )}
            
            {artwork?.label_starting_date && (types.length > 0 || topics.length > 0) && <hr className="border-gray-100" />}
            
            {/* Type & Topics */}
            <div className="grid sm:grid-cols-2 gap-4">
              {types.length > 0 && (
                <div className="flex flex-col">
                  <span className="text-xs font-semibold text-gray-500 uppercase">Type</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {types.map((t: string, i: number) => (
                      <span key={i} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800">
                        {cleanLabel(t)}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              {topics.length > 0 && (
                <div className="flex flex-col">
                  <span className="text-xs font-semibold text-gray-500 uppercase">Topics</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {topics.map((t: string, i: number) => (
                      <span key={i} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                        {cleanLabel(t)}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </SectionWrapper>
    </section>
  );
}
