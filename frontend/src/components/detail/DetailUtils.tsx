/**
 * Shared utilities and components for detail pages.
 */

import { cleanLabel } from "@/lib/utils";
import EntityLink from "@/components/EntityLink";
import type { LinkedEntity } from "@/lib/types";

// Parse "label:::uri" format into objects with label and uri
export function parseLinkedEntities(value: string | undefined): LinkedEntity[] {
  if (!value) return [];
  
  return value.split('|').filter(Boolean).map(item => {
    if (item.includes(':::')) {
      const [label, uri] = item.split(':::');
      return { label: label.trim(), uri: uri?.trim() || null };
    }
    return { label: item.trim(), uri: null };
  }).filter(entity => entity.label && entity.label.length > 0);
}

// Section header component
interface SectionHeaderProps {
  title: string;
  colorClass?: string;
}

export function SectionHeader({ title, colorClass = "bg-indigo-500" }: SectionHeaderProps) {
  return (
    <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
      <span className={`w-2 h-8 ${colorClass} rounded-full`}></span>
      {title}
    </h3>
  );
}

// Section wrapper component
interface SectionWrapperProps {
  children: React.ReactNode;
  className?: string;
}

export function SectionWrapper({ children, className = "" }: SectionWrapperProps) {
  return (
    <div className={`bg-white rounded-xl border border-gray-200 shadow-sm p-6 ${className}`}>
      {children}
    </div>
  );
}

// Sidebar card component
interface SidebarCardProps {
  title: string;
  children: React.ReactNode;
}

export function SidebarCard({ title, children }: SidebarCardProps) {
  return (
    <div className="bg-gray-50 rounded-xl p-6 border border-gray-100">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 border-b pb-2">{title}</h3>
      {children}
    </div>
  );
}

// Property display component
interface PropertyRowProps {
  label: string;
  value: string | undefined;
  className?: string;
}

export function PropertyRow({ label, value, className = "" }: PropertyRowProps) {
  if (!value) return null;
  
  return (
    <div className="flex flex-col">
      <span className="text-xs font-semibold text-gray-500 uppercase">{label}</span>
      <span className={`text-gray-900 ${className}`}>{cleanLabel(value)}</span>
    </div>
  );
}

// Linked entity list component
interface EntityListProps {
  label: string;
  entities: LinkedEntity[];
  colorClass?: string;
}

export function EntityList({ label, entities, colorClass = "text-indigo-600 hover:text-indigo-800" }: EntityListProps) {
  if (entities.length === 0) return null;
  
  return (
    <div>
      <dt className="text-xs font-medium text-gray-500 uppercase tracking-wide">{label}</dt>
      <dd className="mt-1 space-y-1">
        {entities.map((entity, i) => (
          <div key={i} className="text-sm text-gray-900 font-medium">
            <EntityLink 
              label={entity.label} 
              uri={entity.uri} 
              className={`${colorClass} hover:underline`} 
            />
          </div>
        ))}
      </dd>
    </div>
  );
}

// Definition list wrapper
interface DefinitionListProps {
  children: React.ReactNode;
  className?: string;
}

export function DefinitionList({ children, className = "space-y-4" }: DefinitionListProps) {
  return <dl className={className}>{children}</dl>;
}
