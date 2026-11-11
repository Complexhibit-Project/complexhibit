import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import {
  getDataProperties, 
  getRolesPlayed, 
  getParticipants,
  getArtworks,
  getExhibitionMaking,
  getDatesAndPlace,
  getActorDetails,
  getArtworkDetails,
  getInstitutionExhibitions,
  getInstitutionDetails,
  getInstitutionLenderExhibitions,
  getInstitutionOwnedArtworks,
  getPersonCollaborators,
  getInstitutionCollaborators,
  getPersonExecutivePositions,
  getInstitutionExecutives,
  getInstitutionParent,
  getInstitutionChildren,
  getCatalogDetails,
  getExhibitionCatalogs,
  getProducerCatalogs,
  getCatalogExhibitions,
  getCompanyDetails,
  getCompanyMuseographerExhibitions,
  getExhibitionMuseographers
} from "@/lib/api";
import { cleanLabel, unCamel } from "@/lib/utils";
import { getListTypeFromDetailType, buildStoreUri } from "@/lib/entity-routing";
import MapSection from '@/components/MapSection';
import QueryLogger from "@/components/QueryLogger";
import EntityLink from "@/components/EntityLink";
import { DetailClient } from "@/components/detail/DetailClient"; 

// Import entity-specific components
import {
  parseLinkedEntities,
  SectionHeader,
  ExhibitionSidebar,
  ExhibitionDetails,
  ParticipantsSection,
  ActorRolesSidebar,
  ActorBiography,
  ActorResidence,
  ActorCollaborators,
  ActorExecutivePositions,
  ArtworkRelationsSidebar,
  ArtworkDetails,
  InstitutionSidebar,
  InstitutionDetails,
  InstitutionCollaborators,
  InstitutionHeadquarters,
  InstitutionSubsidiaries,
  CatalogDetails,
  CatalogSidebar,
  ExhibitionCatalogs,
  ProducedCatalogs,
  CompanyDetails,
  CompanySidebar,
  SidebarCard,
  DefinitionList,
  EntityList,
} from "@/components/detail";

interface PageProps {
  params: Promise<{ type: string; id: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

// Helper type guards
const isActorType = (type: string) => 
  ['actor', 'human_actant', 'person', 'actant'].includes(type);

const isArtworkType = (type: string) => 
  ['artwork', 'obra'].includes(type);

export default async function DetailPage({ params, searchParams }: PageProps) {
  const { type, id } = await params;
  const rawType = decodeURIComponent(type);
  const decodedType = rawType.toLowerCase();
  const decodedId = decodeURIComponent(id);
  const isCanonicalEntityId = !decodedId.includes("/");
  const listType = getListTypeFromDetailType(decodedType);
  const queryParams = await searchParams;
  const from = typeof queryParams.from === "string" ? queryParams.from : undefined;
  const safeFrom = from?.startsWith("/") ? from : undefined;
  const hasListTarget = Boolean(safeFrom || listType);
  const backHref = safeFrom || (listType ? `/all/${listType}` : "/search");
  const backLabel = hasListTarget ? "Back to list" : "Back to search";
  
  // ====================
  // Data Fetching
  // ====================
  
  // Base fetches (always needed)
  const dataPropertiesPromise = getDataProperties(rawType, decodedId).catch(() => null);
  
  // Actor-specific
  const rolesPromise = isActorType(decodedType) && isCanonicalEntityId
    ? getRolesPlayed(decodedType, decodedId).catch(() => null) 
    : Promise.resolve(null);
  const actorDetailsPromise = isActorType(decodedType) && isCanonicalEntityId
    ? getActorDetails(decodedId).catch(() => null) 
    : Promise.resolve(null);
  const personCollaboratorsPromise = isActorType(decodedType) && isCanonicalEntityId
    ? getPersonCollaborators(decodedId).catch(() => null)
    : Promise.resolve(null);
  const personExecutivePositionsPromise = isActorType(decodedType) && isCanonicalEntityId
    ? getPersonExecutivePositions(decodedId).catch(() => null)
    : Promise.resolve(null);
  
  // Artwork-specific
  const artworkDetailsPromise = isArtworkType(decodedType) && isCanonicalEntityId
    ? getArtworkDetails(decodedId).catch(() => null) 
    : Promise.resolve(null);
  
  // Exhibition-specific
  const participantsPromise = decodedType === 'exhibition' 
    ? getParticipants().catch(() => null) 
    : Promise.resolve(null);
  const artworksPromise = decodedType === 'exhibition' 
    ? getArtworks().catch(() => null) 
    : Promise.resolve(null);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const _unusedArtworks = artworksPromise;
  const makingPromise = decodedType === 'exhibition' 
    ? getExhibitionMaking().catch(() => null) 
    : Promise.resolve(null);
  const datesAndPlacePromise = decodedType === 'exhibition' && isCanonicalEntityId
    ? getDatesAndPlace(decodedId).catch(() => null) 
    : Promise.resolve(null);

  // Institution-specific
  const institutionExhibitionsPromise = decodedType === 'institution' && isCanonicalEntityId
    ? getInstitutionExhibitions(decodedId).catch(() => null)
    : Promise.resolve(null);
  const institutionDetailsPromise = decodedType === 'institution' && isCanonicalEntityId
    ? getInstitutionDetails(decodedId).catch(() => null)
    : Promise.resolve(null);
  const institutionLenderExhibitionsPromise = decodedType === 'institution' && isCanonicalEntityId
    ? getInstitutionLenderExhibitions(decodedId).catch(() => null)
    : Promise.resolve(null);
  const institutionOwnedArtworksPromise = decodedType === 'institution' && isCanonicalEntityId
    ? getInstitutionOwnedArtworks(decodedId).catch(() => null)
    : Promise.resolve(null);
  const institutionCollaboratorsPromise = decodedType === 'institution' && isCanonicalEntityId
    ? getInstitutionCollaborators(decodedId).catch(() => null)
    : Promise.resolve(null);
  const institutionExecutivesPromise = decodedType === 'institution' && isCanonicalEntityId
    ? getInstitutionExecutives(decodedId).catch(() => null)
    : Promise.resolve(null);
  const institutionParentPromise = decodedType === 'institution' && isCanonicalEntityId
    ? getInstitutionParent(decodedId).catch(() => null)
    : Promise.resolve(null);
  const institutionChildrenPromise = decodedType === 'institution' && isCanonicalEntityId
    ? getInstitutionChildren(decodedId).catch(() => null)
    : Promise.resolve(null);

  // Catalog-specific
  const catalogDetailsPromise = decodedType === 'catalog' && isCanonicalEntityId
    ? getCatalogDetails(decodedId).catch(() => null)
    : Promise.resolve(null);
  
  // Catalogs for exhibitions
  const exhibitionCatalogsPromise = decodedType === 'exhibition' && isCanonicalEntityId
    ? getExhibitionCatalogs(decodedId).catch(() => null)
    : Promise.resolve(null);
  
  // Produced catalogs for actants and institutions
  const producedCatalogsPromise = (isActorType(decodedType) || decodedType === 'institution') && isCanonicalEntityId
    ? getProducerCatalogs(decodedId).catch(() => null)
    : Promise.resolve(null);
  
  // Exhibitions for a catalog
  const catalogExhibitionsPromise = decodedType === 'catalog' && isCanonicalEntityId
    ? getCatalogExhibitions(decodedId).catch(() => null)
    : Promise.resolve(null);

  // Company-specific
  const companyDetailsPromise = decodedType === 'company' && isCanonicalEntityId
    ? getCompanyDetails(decodedId).catch(() => null)
    : Promise.resolve(null);
  const companyMuseographerExhibitionsPromise = decodedType === 'company' && isCanonicalEntityId
    ? getCompanyMuseographerExhibitions(decodedId).catch(() => null)
    : Promise.resolve(null);
  
  // Museographers for exhibitions
  const exhibitionMuseographersPromise = decodedType === 'exhibition' && isCanonicalEntityId
    ? getExhibitionMuseographers(decodedId).catch(() => null)
    : Promise.resolve(null);

  // Await all promises
  const [
    dataProperties, roles, actorDetails, artworkDetails,
    participants, making, datesAndPlace, institutionExhibitions, 
    institutionDetails, institutionLenderExhibitions, institutionOwnedArtworks,
    personCollaborators, institutionCollaboratorsData, personExecutivePositions,
    institutionExecutivesData, institutionParentData, institutionChildrenData,
    catalogDetails, exhibitionCatalogs, producedCatalogs, catalogExhibitions,
    companyDetails, companyMuseographerExhibitions, exhibitionMuseographers
  ] = await Promise.all([
    dataPropertiesPromise,
    rolesPromise,
    actorDetailsPromise,
    artworkDetailsPromise,
    participantsPromise,
    makingPromise,
    datesAndPlacePromise,
    institutionExhibitionsPromise,
    institutionDetailsPromise,
    institutionLenderExhibitionsPromise,
    institutionOwnedArtworksPromise,
    personCollaboratorsPromise,
    institutionCollaboratorsPromise,
    personExecutivePositionsPromise,
    institutionExecutivesPromise,
    institutionParentPromise,
    institutionChildrenPromise,
    catalogDetailsPromise,
    exhibitionCatalogsPromise,
    producedCatalogsPromise,
    catalogExhibitionsPromise,
    companyDetailsPromise,
    companyMuseographerExhibitionsPromise,
    exhibitionMuseographersPromise
  ]);

  // ====================
  // Data Processing
  // ====================
  
  const rawProperties = dataProperties?.data || {};
  const roleData = roles?.data || {};
  const participantData = participants?.data || {};
  const makingData = making?.data || {};
  const datesAndPlaceData = datesAndPlace?.data || [];
  const actorData = actorDetails?.data || [];
  const artworkDetailData = artworkDetails?.data || [];
  const institutionExhibitionsData = institutionExhibitions?.data || [];
  const institutionData = institutionDetails?.data || [];
  const institutionItem = Array.isArray(institutionData) && institutionData.length > 0 ? institutionData[0] : institutionData;
  const institutionLenderExhibitionsData = institutionLenderExhibitions?.data || [];
  const institutionOwnedArtworksData = institutionOwnedArtworks?.data || [];
  const personCollaboratorsData = personCollaborators?.data || { persons: [], institutions: [] };
  const institutionCollaboratorsList = institutionCollaboratorsData?.data || [];
  const personExecutivePositionsData = personExecutivePositions?.data || [];
  const institutionExecutivesList = institutionExecutivesData?.data || [];
  const parentOrganization = institutionParentData?.data || null;
  const childOrganizations = institutionChildrenData?.data || [];
  const catalogData = catalogDetails?.data || [];
  const exhibitionCatalogsData = exhibitionCatalogs?.data || [];
  const producedCatalogsData = producedCatalogs?.data || [];
  
  // Parse catalogs to LinkedEntity format
  const catalogEntities = exhibitionCatalogsData.map((c: { catalog_uri: string; catalog_label?: string }) => ({
    uri: c.catalog_uri,
    label: c.catalog_label
  }));
  
  const producedCatalogEntities = producedCatalogsData.map((c: { catalog_uri: string; catalog_label?: string }) => ({
    uri: c.catalog_uri,
    label: c.catalog_label
  }));
  
  // Parse catalog producers
  const catalogProducers = catalogData[0]?.producers 
    ? catalogData[0].producers.split('|').map((p: string) => {
        const [uri, label] = p.split('::');
        return { uri, label };
      })
    : [];
  
  // Parse catalog exhibitions
  const catalogExhibitionsData = catalogExhibitions?.data || [];
  const catalogExhibitionEntities = catalogExhibitionsData.map((e: { exhibition_uri: string; exhibition_label?: string }) => ({
    uri: e.exhibition_uri,
    label: e.exhibition_label
  }));

  // Company data processing
  const companyData = companyDetails?.data || [];
  const companyItem = Array.isArray(companyData) && companyData.length > 0 ? companyData[0] : companyData;
  const companyMuseographerExhibitionsData = companyMuseographerExhibitions?.data || [];
  const museographerExhibitionEntities = companyMuseographerExhibitionsData.map((e: { uri: string; label?: string }) => ({
    uri: e.uri,
    label: e.label
  }));
  
  // Museographers for exhibitions
  const exhibitionMuseographersData = exhibitionMuseographers?.data || [];
  const museographerEntities = exhibitionMuseographersData.map((m: { uri: string; label?: string }) => ({
    uri: m.uri,
    label: m.label
  }));

  // Debug query for QueryLogger
  const debugQuery = decodedType === 'exhibition' 
    ? datesAndPlace?.sparql 
    : (isArtworkType(decodedType) 
      ? (artworkDetails?.sparql || dataProperties?.sparql)
      : (isActorType(decodedType) 
        ? (actorDetails?.sparql || dataProperties?.sparql)
        : (decodedType === 'institution' 
            ? (institutionExhibitions?.sparql || dataProperties?.sparql)
            : dataProperties?.sparql)));

  // For exhibitions, find matching data
  const exhibitionData = decodedType === 'exhibition' && datesAndPlaceData.length > 0 
    ? (datesAndPlaceData.find((item: { uri?: string; [key: string]: unknown }) => item.uri?.includes(decodedId)) || datesAndPlaceData[0])
    : null;
  
  // Properties with fallback
  const properties = exhibitionData
    ? { label: exhibitionData.label, ...exhibitionData }
    : (Array.isArray(rawProperties) && rawProperties.length > 0 ? rawProperties[0] : rawProperties);

  // Extract entity_type for Person/Group distinction
  const entityType = properties?.entity_type || (isActorType(decodedType) && actorData[0]?.entity_type);
  const displayEntityType = entityType === 'group' ? 'Group' : (entityType ? 'Person' : undefined);

  // Parse linked entities for exhibitions
  const curators = parseLinkedEntities(exhibitionData?.curators);
  const organizers = parseLinkedEntities(exhibitionData?.organizers);
  const funders = parseLinkedEntities(exhibitionData?.funders);
  const lenders = parseLinkedEntities(exhibitionData?.lenders);
  const exhibitors = parseLinkedEntities(exhibitionData?.exhibitors);
  const displayedArtworks = parseLinkedEntities(exhibitionData?.artworks);

  // ====================
  // Label Extraction
  // ====================
  
  const getLabel = (): string => {
    if (exhibitionData?.label) return cleanLabel(exhibitionData.label);
    if (isActorType(decodedType) && actorData[0]?.label) return cleanLabel(actorData[0].label);
    if (isArtworkType(decodedType) && artworkDetailData[0]?.label) return cleanLabel(artworkDetailData[0].label);
    if (decodedType === 'catalog' && catalogData[0]?.label) return cleanLabel(catalogData[0].label);
    if (decodedType === 'institution' && institutionItem?.label) return cleanLabel(institutionItem.label);
    if (decodedType === 'company' && companyItem?.label) return cleanLabel(companyItem.label);
    
    for (const key in properties) {
      if (key.toLowerCase().includes('label') || key.toLowerCase().includes('title') || key.toLowerCase().includes('name')) {
        const val = properties[key];
        return cleanLabel(typeof val === 'object' && val !== null ? val.label || val.value : val);
      }
    }
    return `${unCamel(decodedType)} Details`;
  };

  const label = getLabel();
  // Use the real store IRI (e.g. #human_actant/… for actants, #work_manifestation/… for artworks)
  // so the relationship graph and "Explore in graph" resolve the resource correctly.
  const fullUri = properties.uri || buildStoreUri(rawType, decodedId);

  // Collect all SPARQL queries used
  const allSparqlQueries = [
    dataProperties?.sparql,
    roles?.sparql,
    actorDetails?.sparql,
    artworkDetails?.sparql,
    datesAndPlace?.sparql,
    institutionDetails?.sparql,
    institutionExhibitions?.sparql,
    institutionLenderExhibitions?.sparql,
    institutionOwnedArtworks?.sparql,
    personCollaborators?.sparql,
    institutionCollaboratorsData?.sparql,
    personExecutivePositions?.sparql,
    institutionExecutivesData?.sparql,
    institutionParentData?.sparql,
    institutionChildrenData?.sparql,
    catalogDetails?.sparql,
    exhibitionCatalogs?.sparql,
    producedCatalogs?.sparql,
    catalogExhibitions?.sparql,
    companyDetails?.sparql,
    companyMuseographerExhibitions?.sparql,
    exhibitionMuseographers?.sparql
  ].filter(Boolean) as string[];

  // ====================
  // Render
  // ====================
  
  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
      <QueryLogger query={debugQuery} type={decodedType} />
      
      <div className="mb-8">
        <Link href={backHref} className="text-indigo-600 hover:text-indigo-800 flex items-center gap-1 mb-4 transition-colors">
          <ArrowLeft className="h-4 w-4" /> {backLabel}
        </Link>

        <DetailClient
          label={label}
          type={decodedType}
          fullUri={fullUri}
          properties={properties}
          sparqlQueries={allSparqlQueries}
          entityType={displayEntityType}
        >
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
              
              {/* Left Column: Sidebar */}
              <div className="lg:col-span-1 space-y-8">
                {isArtworkType(decodedType) && (
                  <ArtworkRelationsSidebar artworkData={artworkDetailData} />
                )}
                
                {isActorType(decodedType) && (
                  <>
                    <ActorRolesSidebar roleData={roleData} />
                    <ActorCollaborators collaborators={personCollaboratorsData} />
                    <ActorExecutivePositions positions={personExecutivePositionsData} />
                    <ProducedCatalogs catalogs={producedCatalogEntities} title="Produced Catalogs" />
                  </>
                )}
                
                {decodedType === 'institution' && (
                  <>
                    <InstitutionSidebar 
                      exhibitions={institutionExhibitionsData} 
                      lenderExhibitions={institutionLenderExhibitionsData}
                      ownedArtworks={institutionOwnedArtworksData}
                    />
                    <InstitutionCollaborators collaborators={institutionCollaboratorsList} />
                    <InstitutionSubsidiaries childOrganizations={childOrganizations} />
                    <ProducedCatalogs catalogs={producedCatalogEntities} title="Published Catalogs" />
                  </>
                )}
                
                {decodedType === 'exhibition' && (
                  <>
                    <ExhibitionSidebar 
                      curators={curators}
                      organizers={organizers}
                      funders={funders}
                      lenders={lenders}
                      exhibitors={exhibitors}
                    />
                    {museographerEntities.length > 0 && (
                      <SidebarCard title="Museography">
                        <DefinitionList>
                          <EntityList 
                            label="Museographer" 
                            entities={museographerEntities} 
                            colorClass="text-teal-600 hover:text-teal-800"
                          />
                        </DefinitionList>
                      </SidebarCard>
                    )}
                    <ExhibitionCatalogs catalogs={catalogEntities} />
                  </>
                )}
                
                {decodedType === 'catalog' && (
                  <CatalogSidebar producers={catalogProducers} exhibitions={catalogExhibitionEntities} />
                )}

                {decodedType === 'company' && (
                  <CompanySidebar museographerExhibitions={museographerExhibitionEntities} />
                )}
              </div>

              {/* Right Column: Main Content */}
              <div className="lg:col-span-2 space-y-10">
                {/* Actor Biography */}
                {isActorType(decodedType) && (
                  <>
                    <ActorBiography actorData={actorData} />
                    <ActorResidence actorData={actorData} />
                    
                    {/* Residence Map */}
                    {actorData[0]?.residence_lat && actorData[0]?.residence_long && (
                      <section>
                        <SectionHeader title="Residence Location" colorClass="bg-teal-500" />
                        <MapSection 
                          lat={parseFloat(actorData[0].residence_lat)} 
                          long={parseFloat(actorData[0].residence_long)} 
                          label={actorData[0]?.residence_address || label}
                        />
                      </section>
                    )}
                  </>
                )}
                
                {/* Artwork Details */}
                {isArtworkType(decodedType) && (
                  <ArtworkDetails artworkData={artworkDetailData} />
                )}

                {decodedType === 'institution' && (
                  <>
                    <InstitutionDetails 
                      data={institutionItem} 
                      executives={institutionExecutivesList} 
                      parentOrganization={parentOrganization}
                    />
                    <InstitutionHeadquarters data={institutionItem} />
                    
                    {/* Headquarters Map */}
                    {institutionItem?.headquarters_lat && institutionItem?.headquarters_long && (
                      <section>
                        <SectionHeader title="Headquarters Location" colorClass="bg-teal-600" />
                        <MapSection 
                          lat={parseFloat(institutionItem.headquarters_lat)} 
                          long={parseFloat(institutionItem.headquarters_long)} 
                          label={institutionItem?.headquarters_address || institutionItem?.label || "Headquarters"}
                        />
                      </section>
                    )}
                  </>
                )}
                
                {/* Catalog Details */}
                {decodedType === 'catalog' && (
                  <CatalogDetails data={catalogData} />
                )}

                {/* Company Details */}
                {decodedType === 'company' && (
                  <CompanyDetails data={companyItem} />
                )}
                
                {/* Exhibition Sections */}
                {decodedType === 'exhibition' && (
                  <>
                    <ParticipantsSection 
                      data={participantData} 
                      title="Participants" 
                      colorClass="bg-purple-500" 
                      linkColorClass="hover:text-purple-600" 
                    />
                    
                    <ParticipantsSection 
                      data={makingData} 
                      title="Exhibition Making" 
                      colorClass="bg-orange-500" 
                      linkColorClass="hover:text-orange-600" 
                    />
                    
                    <ExhibitionDetails data={datesAndPlaceData} />
                    
                    {/* Map */}
                    {exhibitionData?.lat && exhibitionData?.long && (
                      <section>
                        <SectionHeader title="Location" colorClass="bg-teal-500" />
                        <MapSection 
                          lat={parseFloat(exhibitionData.lat)} 
                          long={parseFloat(exhibitionData.long)} 
                          label={exhibitionData.venue_label || exhibitionData.label_place || label}
                        />
                      </section>
                    )}
                    
                    {/* Artworks Displayed */}
                    {displayedArtworks.length > 0 && (
                      <section>
                        <SectionHeader title="Artworks Displayed" colorClass="bg-pink-500" />
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                          {displayedArtworks.map((artwork, idx) => (
                            <div key={idx} className="group block bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-lg transition-all p-4 hover:border-pink-300">
                              <div className="font-medium text-gray-900 group-hover:text-pink-600 transition-colors">
                                <EntityLink 
                                  label={artwork.label} 
                                  uri={artwork.uri} 
                                  className="text-gray-900 hover:text-pink-600 hover:underline"
                                />
                              </div>
                            </div>
                          ))}
                        </div>
                      </section>
                    )}
                  </>
                )}
              </div>
            </div>
        </DetailClient>
      </div>
    </div>
  );
}
