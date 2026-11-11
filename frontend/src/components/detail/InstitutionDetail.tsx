/**
 * Institution-specific detail components.
 */

import { cleanLabel } from "@/lib/utils";
import { SidebarCard, DefinitionList, SectionWrapper, SectionHeader, PropertyRow, EntityList } from "./DetailUtils";
import EntityLink from "@/components/EntityLink";
import type { LinkedEntity } from "@/lib/types";

interface ExhibitionItem {
  uri: string;
  label?: string;
  start_date?: string;
  type?: string;
}

interface InstitutionData {
  label?: string;
  apelation?: string;
  label_place?: string;
  place_uri?: string;
  ownershipType?: string;
  email?: string;
  telephone?: string;
  uriHtml?: string;
  headquarters_address?: string;
  headquarters_lat?: string;
  headquarters_long?: string;
}

interface InstitutionDetailsProps {
  data: InstitutionData | InstitutionData[];
  executives?: LinkedEntity[];
  parentOrganization?: LinkedEntity | null;
}

export function InstitutionDetails({ 
  data, 
  executives = [], 
  parentOrganization 
}: InstitutionDetailsProps) {
  const institution = Array.isArray(data) ? data[0] : data;
  
  const hasData = institution && (
    institution.apelation || institution.label_place || 
    institution.ownershipType || institution.email || 
    institution.telephone || institution.uriHtml
  );
  const hasExecutives = executives.length > 0;
  const hasParent = parentOrganization && parentOrganization.uri;
  
  if (!hasData && !hasExecutives && !hasParent) {
    return null;
  }
  
  return (
    <section>
      <SectionHeader title="Institution Details" colorClass="bg-green-600" />
      <SectionWrapper>
        <div className="space-y-4">
          <PropertyRow label="Alternative Name" value={institution?.apelation} />
          <PropertyRow label="Ownership Type" value={institution?.ownershipType} />
          
          {institution?.label_place && (
            <div className="flex flex-col">
              <span className="text-xs font-semibold text-gray-500 uppercase">Location</span>
              <span className="text-gray-900">
                {institution.place_uri ? (
                  <EntityLink 
                    label={cleanLabel(institution.label_place)} 
                    uri={institution.place_uri} 
                    className="text-teal-600 hover:text-teal-800 hover:underline" 
                  />
                ) : (
                  cleanLabel(institution.label_place)
                )}
              </span>
            </div>
          )}
          
          {/* Contact Information */}
          {(institution?.email || institution?.telephone || institution?.uriHtml) && (
            <>
              <hr className="border-gray-100" />
              <div className="grid sm:grid-cols-2 gap-4">
                {institution.email && (
                  <div className="flex flex-col">
                    <span className="text-xs font-semibold text-gray-500 uppercase">Email</span>
                    <a href={`mailto:${institution.email}`} className="text-indigo-600 hover:text-indigo-800 hover:underline">
                      {institution.email}
                    </a>
                  </div>
                )}
                {institution.telephone && (
                  <div className="flex flex-col">
                    <span className="text-xs font-semibold text-gray-500 uppercase">Telephone</span>
                    <a href={`tel:${institution.telephone}`} className="text-indigo-600 hover:text-indigo-800 hover:underline">
                      {institution.telephone}
                    </a>
                  </div>
                )}
                {institution.uriHtml && (
                  <div className="flex flex-col sm:col-span-2">
                    <span className="text-xs font-semibold text-gray-500 uppercase">Website</span>
                    <a href={institution.uriHtml} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-800 hover:underline truncate">
                      {institution.uriHtml}
                    </a>
                  </div>
                )}
              </div>
            </>
          )}
          
          {/* Executive Leadership */}
          {hasExecutives && (
            <>
              <hr className="border-gray-100" />
              <div className="flex flex-col">
                <span className="text-xs font-semibold text-gray-500 uppercase mb-2">Executive Leadership</span>
                <div className="flex flex-wrap gap-2">
                  {executives.map((exec, idx) => (
                    <EntityLink 
                      key={idx}
                      label={cleanLabel(exec.label || "Executive")} 
                      uri={exec.uri!} 
                      className="text-amber-600 hover:text-amber-800 hover:underline"
                    />
                  ))}
                </div>
              </div>
            </>
          )}
          
          {/* Parent Organization */}
          {hasParent && parentOrganization && (
            <>
              <hr className="border-gray-100" />
              <div className="flex flex-col">
                <span className="text-xs font-semibold text-gray-500 uppercase mb-1">Parent Organization</span>
                <EntityLink 
                  label={cleanLabel(parentOrganization.label || "Parent")} 
                  uri={parentOrganization.uri!} 
                  className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
                />
              </div>
            </>
          )}
        </div>
      </SectionWrapper>
    </section>
  );
}

interface InstitutionSidebarProps {
  exhibitions?: {
    venue?: ExhibitionItem[];
    organizer?: ExhibitionItem[];
    funder?: ExhibitionItem[];
  };
  lenderExhibitions?: ExhibitionItem[];
  ownedArtworks?: ExhibitionItem[];
}

export function InstitutionSidebar({ exhibitions = {}, lenderExhibitions = [], ownedArtworks = [] }: InstitutionSidebarProps) {
  const venueExhibitions = exhibitions?.venue || [];
  const organizerExhibitions = exhibitions?.organizer || [];
  const funderExhibitions = exhibitions?.funder || [];
  
  const hasLender = lenderExhibitions.length > 0;
  const hasArtworks = ownedArtworks.length > 0;
  const hasVenue = venueExhibitions.length > 0;
  const hasOrganizer = organizerExhibitions.length > 0;
  const hasFunder = funderExhibitions.length > 0;
  
  if (!hasVenue && !hasOrganizer && !hasFunder && !hasLender && !hasArtworks) return null;
  
  // Transform exhibitions to LinkedEntity format
  const toEntities = (items: ExhibitionItem[]) => items.map(exh => ({
    label: `${exh.label || "Untitled Exhibition"}${exh.start_date ? ` - ${exh.start_date}` : ""}`,
    uri: exh.uri
  }));
  
  const lenderEntities: LinkedEntity[] = toEntities(lenderExhibitions);
  const artworkEntities: LinkedEntity[] = ownedArtworks.map(art => ({
    label: `${art.label || "Untitled Artwork"}${art.type ? ` (${art.type})` : ""}`,
    uri: art.uri
  }));
  
  return (
    <>
      {/* Venue - Exhibitions hosted at this institution */}
      {venueExhibitions.length > 0 && (
        <SidebarCard title="Venue For">
          <DefinitionList>
            <EntityList 
              label="Exhibitions" 
              entities={toEntities(venueExhibitions)} 
              colorClass="text-indigo-600 hover:text-indigo-800"
            />
          </DefinitionList>
        </SidebarCard>
      )}
      
      {/* Organizer - Exhibitions organized by this institution */}
      {organizerExhibitions.length > 0 && (
        <SidebarCard title="Organized">
          <DefinitionList>
            <EntityList 
              label="Exhibitions" 
              entities={toEntities(organizerExhibitions)} 
              colorClass="text-blue-600 hover:text-blue-800"
            />
          </DefinitionList>
        </SidebarCard>
      )}
      
      {/* Funder - Exhibitions funded by this institution */}
      {funderExhibitions.length > 0 && (
        <SidebarCard title="Funded">
          <DefinitionList>
            <EntityList 
              label="Exhibitions" 
              entities={toEntities(funderExhibitions)} 
              colorClass="text-green-600 hover:text-green-800"
            />
          </DefinitionList>
        </SidebarCard>
      )}
      
      {/* Lender Role */}
      {hasLender && (
        <SidebarCard title="Lender For">
          <DefinitionList>
            <EntityList 
              label="Exhibitions" 
              entities={lenderEntities} 
              colorClass="text-purple-600 hover:text-purple-800"
            />
          </DefinitionList>
        </SidebarCard>
      )}
      
      {/* Owned Assets */}
      {hasArtworks && (
        <SidebarCard title="Owned Assets">
          <DefinitionList>
            <EntityList 
              label="Artworks" 
              entities={artworkEntities} 
              colorClass="text-pink-600 hover:text-pink-800"
            />
          </DefinitionList>
        </SidebarCard>
      )}
    </>
  );
}

interface InstitutionCollaboratorsProps {
  collaborators: LinkedEntity[];
}

export function InstitutionCollaborators({ collaborators }: InstitutionCollaboratorsProps) {
  if (!collaborators || collaborators.length === 0) return null;
  
  return (
    <SidebarCard title="Affiliated Persons">
      <DefinitionList>
        <EntityList 
          label="Persons" 
          entities={collaborators} 
          colorClass="text-indigo-600 hover:text-indigo-800"
        />
      </DefinitionList>
    </SidebarCard>
  );
}

interface InstitutionHeadquartersProps {
  data: InstitutionData | InstitutionData[];
}

export function InstitutionHeadquarters({ data }: InstitutionHeadquartersProps) {
  const institution = Array.isArray(data) ? data[0] : data;
  
  if (!institution?.headquarters_address) return null;
  
  return (
    <section>
      <SectionHeader title="Headquarters" colorClass="bg-teal-600" />
      <SectionWrapper>
        <div className="flex flex-col">
          <span className="text-xs font-semibold text-gray-500 uppercase">Address</span>
          <span className="text-gray-900">{institution.headquarters_address}</span>
        </div>
      </SectionWrapper>
    </section>
  );
}

interface InstitutionExecutivesProps {
  executives: LinkedEntity[];
}

export function InstitutionExecutives({ executives }: InstitutionExecutivesProps) {
  if (!executives || executives.length === 0) return null;
  
  return (
    <SidebarCard title="Executive Leadership">
      <DefinitionList>
        <EntityList 
          label="Executives" 
          entities={executives} 
          colorClass="text-amber-600 hover:text-amber-800"
        />
      </DefinitionList>
    </SidebarCard>
  );
}

interface InstitutionSubsidiariesProps {
  childOrganizations?: LinkedEntity[];
}

export function InstitutionSubsidiaries({ childOrganizations = [] }: InstitutionSubsidiariesProps) {
  if (!childOrganizations || childOrganizations.length === 0) return null;
  
  return (
    <SidebarCard title="Subsidiary Organizations">
      <DefinitionList>
        <EntityList 
          label="Institutions" 
          entities={childOrganizations} 
          colorClass="text-emerald-600 hover:text-emerald-800"
        />
      </DefinitionList>
    </SidebarCard>
  );
}
