/**
 * Catalog-specific detail components.
 */

import { cleanLabel } from "@/lib/utils";
import { 
  SidebarCard, 
  SectionHeader, 
  SectionWrapper, 
  DefinitionList, 
  EntityList,
  PropertyRow,
} from "./DetailUtils";
import EntityLink from "@/components/EntityLink";
import type { LinkedEntity } from "@/lib/types";

interface CatalogData {
  label?: string;
  publication_date?: string;
  publication_place_label?: string;
  publication_place_uri?: string;
  producers?: string;
}

interface CatalogDetailsProps {
  data: CatalogData | CatalogData[];
}

export function CatalogDetails({ data }: CatalogDetailsProps) {
  const item = Array.isArray(data) && data.length > 0 ? data[0] : data as CatalogData;
  
  if (!item || !item.label) return null;
  
  // Don't render section if no publication info
  if (!item.publication_date && !item.publication_place_label) return null;
  
  return (
    <section>
      <SectionHeader title="Publication Details" colorClass="bg-amber-500" />
      <SectionWrapper>
        <div className="grid gap-4">
          <div className="space-y-4">
            {/* Publication Date */}
            {item.publication_date && (
              <PropertyRow label="Publication Date" value={item.publication_date} />
            )}
            
            {/* Publication Place */}
            {item.publication_place_label && (
              <div className="flex flex-col">
                <span className="text-xs font-semibold text-gray-500 uppercase">Publication Place</span>
                <span className="text-gray-900">
                  {item.publication_place_uri ? (
                    <EntityLink 
                      label={cleanLabel(item.publication_place_label)} 
                      uri={item.publication_place_uri} 
                      className="text-teal-600 hover:text-teal-800 hover:underline" 
                    />
                  ) : (
                    cleanLabel(item.publication_place_label)
                  )}
                </span>
              </div>
            )}
          </div>
        </div>
      </SectionWrapper>
    </section>
  );
}

interface CatalogSidebarProps {
  producers: LinkedEntity[];
  exhibitions: LinkedEntity[];
}

export function CatalogSidebar({ producers, exhibitions }: CatalogSidebarProps) {
  const hasData = producers.length > 0 || exhibitions.length > 0;
  if (!hasData) return null;
  
  return (
    <>
      {producers.length > 0 && (
        <SidebarCard title="Producers & Authors">
          <DefinitionList>
            <EntityList 
              label="Producers" 
              entities={producers} 
              colorClass="text-amber-600 hover:text-amber-800" 
            />
          </DefinitionList>
        </SidebarCard>
      )}
      
      {exhibitions.length > 0 && (
        <SidebarCard title="Related Exhibitions">
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

interface ExhibitionCatalogsProps {
  catalogs: LinkedEntity[];
}

export function ExhibitionCatalogs({ catalogs }: ExhibitionCatalogsProps) {
  if (catalogs.length === 0) return null;
  
  return (
    <SidebarCard title="Associated Catalogs">
      <DefinitionList>
        <EntityList 
          label="Catalogs" 
          entities={catalogs} 
          colorClass="text-amber-600 hover:text-amber-800" 
        />
      </DefinitionList>
    </SidebarCard>
  );
}

interface ProducedCatalogsProps {
  catalogs: LinkedEntity[];
  title?: string;
}

export function ProducedCatalogs({ catalogs, title = "Produced Catalogs" }: ProducedCatalogsProps) {
  if (catalogs.length === 0) return null;
  
  return (
    <SidebarCard title={title}>
      <DefinitionList>
        <EntityList 
          label="Catalogs" 
          entities={catalogs} 
          colorClass="text-amber-600 hover:text-amber-800" 
        />
      </DefinitionList>
    </SidebarCard>
  );
}
