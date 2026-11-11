/**
 * Company-specific detail components.
 */

import { cleanLabel } from "@/lib/utils";
import { SidebarCard, DefinitionList, SectionWrapper, SectionHeader, PropertyRow, EntityList } from "./DetailUtils";
import EntityLink from "@/components/EntityLink";
import type { LinkedEntity } from "@/lib/types";

interface CompanyData {
  label?: string;
  isic4_category?: string;
  size?: string;
  location_label?: string;
  location_uri?: string;
}

interface CompanyDetailsProps {
  data: CompanyData | CompanyData[];
}

export function CompanyDetails({ data }: CompanyDetailsProps) {
  const company = Array.isArray(data) ? data[0] : data;
  
  const hasData = company && (
    company.isic4_category || company.size || company.location_label
  );
  
  if (!hasData) {
    return null;
  }
  
  return (
    <section>
      <SectionHeader title="Company Details" colorClass="bg-teal-600" />
      <SectionWrapper>
        <div className="space-y-4">
          <PropertyRow label="Industry (ISIC4)" value={company?.isic4_category} />
          <PropertyRow label="Company Size" value={company?.size} />
          
          {company?.location_label && (
            <div className="flex flex-col">
              <span className="text-xs font-semibold text-gray-500 uppercase">Location</span>
              <span className="text-gray-900">
                {company.location_uri ? (
                  <EntityLink 
                    label={cleanLabel(company.location_label)} 
                    uri={company.location_uri} 
                    className="text-teal-600 hover:text-teal-800 hover:underline" 
                  />
                ) : (
                  cleanLabel(company.location_label)
                )}
              </span>
            </div>
          )}
        </div>
      </SectionWrapper>
    </section>
  );
}

interface CompanySidebarProps {
  museographerExhibitions?: LinkedEntity[];
}

export function CompanySidebar({ museographerExhibitions = [] }: CompanySidebarProps) {
  const hasMuseographerExhibitions = museographerExhibitions.length > 0;
  
  if (!hasMuseographerExhibitions) return null;
  
  return (
    <>
      {hasMuseographerExhibitions && (
        <SidebarCard title="Museography For">
          <DefinitionList>
            <EntityList 
              label="Exhibitions" 
              entities={museographerExhibitions} 
              colorClass="text-indigo-600 hover:text-indigo-800"
            />
          </DefinitionList>
        </SidebarCard>
      )}
    </>
  );
}
