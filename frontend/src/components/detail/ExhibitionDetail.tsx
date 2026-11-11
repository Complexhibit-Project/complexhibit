/**
 * Exhibition-specific detail components.
 */

import Link from "next/link";
import { cleanLabel, unCamel } from "@/lib/utils";
import { buildDetailHref } from "@/lib/entity-routing";
import { 
  SidebarCard, 
  SectionHeader, 
  SectionWrapper,
  EntityList,
  DefinitionList,
  PropertyRow,
} from "./DetailUtils";
import EntityLink from "@/components/EntityLink";
import type { LinkedEntity } from "@/lib/types";

interface ExhibitionData {
  label_starting_date?: string;
  label_ending_date?: string;
  label_place?: string;
  place_uri?: string;
  venue_label?: string;
  venue_uri?: string;
  theme_label?: string;
  type_label?: string;
}

interface ExhibitionSidebarProps {
  curators: LinkedEntity[];
  organizers: LinkedEntity[];
  funders: LinkedEntity[];
  lenders: LinkedEntity[];
  exhibitors: LinkedEntity[];
}

export function ExhibitionSidebar({ 
  curators, organizers, funders, lenders, exhibitors 
}: ExhibitionSidebarProps) {
  const hasExhibitors = exhibitors.length > 0;
  const hasCurators = curators.length > 0;
  const hasOrganizers = organizers.length > 0;
  const hasFunders = funders.length > 0;
  const hasLenders = lenders.length > 0;
  
  if (!hasExhibitors && !hasCurators && !hasOrganizers && !hasFunders && !hasLenders) return null;
  
  return (
    <>
      {/* Exhibiting Artists */}
      {hasExhibitors && (
        <SidebarCard title="Exhibiting Artists">
          <DefinitionList>
            <EntityList 
              label="Artists" 
              entities={exhibitors} 
              colorClass="text-pink-600 hover:text-pink-800"
            />
          </DefinitionList>
        </SidebarCard>
      )}
      
      {/* Curators */}
      {hasCurators && (
        <SidebarCard title="Curators">
          <DefinitionList>
            <EntityList 
              label="Curators" 
              entities={curators} 
              colorClass="text-indigo-600 hover:text-indigo-800"
            />
          </DefinitionList>
        </SidebarCard>
      )}
      
      {/* Organizers */}
      {hasOrganizers && (
        <SidebarCard title="Organizers">
          <DefinitionList>
            <EntityList 
              label="Organizers" 
              entities={organizers} 
              colorClass="text-blue-600 hover:text-blue-800"
            />
          </DefinitionList>
        </SidebarCard>
      )}
      
      {/* Funders */}
      {hasFunders && (
        <SidebarCard title="Funders">
          <DefinitionList>
            <EntityList 
              label="Funders" 
              entities={funders} 
              colorClass="text-green-600 hover:text-green-800"
            />
          </DefinitionList>
        </SidebarCard>
      )}
      
      {/* Lenders */}
      {hasLenders && (
        <SidebarCard title="Lenders">
          <DefinitionList>
            <EntityList 
              label="Lenders" 
              entities={lenders} 
              colorClass="text-purple-600 hover:text-purple-800"
            />
          </DefinitionList>
        </SidebarCard>
      )}
    </>
  );
}

interface ExhibitionDetailsProps {
  data: ExhibitionData[];
}

export function ExhibitionDetails({ data }: ExhibitionDetailsProps) {
  if (!data || data.length === 0) return null;
  
  const item = data[0];
  const themes = item?.theme_label?.split('|').filter(Boolean) || [];
  const types = item?.type_label?.split('|').filter(Boolean) || [];
  
  return (
    <section>
      <SectionHeader title="Exhibition Details" colorClass="bg-green-500" />
      <SectionWrapper>
        <div className="grid gap-4">
          <div className="space-y-4">
            {/* Dates */}
            <div className="grid sm:grid-cols-2 gap-4">
              <PropertyRow label="Opening Date" value={item.label_starting_date} />
              <PropertyRow label="Closing Date" value={item.label_ending_date} />
            </div>
            
            {(item.label_starting_date || item.label_ending_date) && <hr className="border-gray-100" />}
            
            {/* Location */}
            {item.label_place && (
              <div className="flex flex-col">
                <span className="text-xs font-semibold text-gray-500 uppercase">Location</span>
                <span className="text-gray-900">
                  {item.place_uri ? (
                    <EntityLink label={cleanLabel(item.label_place)} uri={item.place_uri} className="text-teal-600 hover:text-teal-800 hover:underline" />
                  ) : (
                    cleanLabel(item.label_place)
                  )}
                </span>
              </div>
            )}
            
            {/* Venue */}
            {item.venue_label && (
              <div className="flex flex-col">
                <span className="text-xs font-semibold text-gray-500 uppercase">Venue</span>
                <span className="text-gray-900">
                  {item.venue_uri ? (
                    <EntityLink label={cleanLabel(item.venue_label)} uri={item.venue_uri} className="text-teal-600 hover:text-teal-800 hover:underline" />
                  ) : (
                    cleanLabel(item.venue_label)
                  )}
                </span>
              </div>
            )}
            
            {/* Themes & Types */}
            {(themes.length > 0 || types.length > 0) && <hr className="border-gray-100" />}
            
            <div className="grid sm:grid-cols-2 gap-4">
              {themes.length > 0 && (
                <div className="flex flex-col">
                  <span className="text-xs font-semibold text-gray-500 uppercase">Themes</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {themes.map((t: string, i: number) => (
                      <span key={i} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                        {cleanLabel(t)}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              {types.length > 0 && (
                <div className="flex flex-col">
                  <span className="text-xs font-semibold text-gray-500 uppercase">Exhibition Type</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {types.map((t: string, i: number) => (
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

interface ParticipantsSectionProps {
  data: Record<string, LinkedEntity[]>;
  title: string;
  colorClass: string;
  linkColorClass: string;
}

export function ParticipantsSection({ data, title, colorClass, linkColorClass }: ParticipantsSectionProps) {
  if (!data || Object.keys(data).length === 0) return null;
  
  return (
    <section>
      <SectionHeader title={title} colorClass={colorClass} />
      <div className="grid gap-6 sm:grid-cols-2">
        {Object.entries(data).map(([role, items]: [string, LinkedEntity[]]) => (
          <div key={role} className="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow p-5">
            <h4 className={`font-semibold ${linkColorClass.replace('hover:', '')} mb-3 text-lg border-b border-gray-100 pb-2`}>
              {unCamel(role)}
            </h4>
            <ul className="space-y-2">
              {Array.isArray(items) && items.map((item: LinkedEntity, idx: number) => (
                <li key={idx}>
                  <Link 
                    href={buildDetailHref("actant", item.uri?.split('/').pop() || "")}
                    className={`text-sm text-gray-700 ${linkColorClass} hover:underline flex items-start gap-2`}
                  >
                    <span className={linkColorClass.replace('hover:text-', 'text-').replace('600', '400')} style={{marginTop: '0.25rem'}}>•</span>
                    <span>{cleanLabel(item.label || item.uri)}</span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
}
