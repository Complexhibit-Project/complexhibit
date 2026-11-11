"use client";

import Link from "next/link";
import { cleanLabel } from "@/lib/utils";
import { buildDetailHref, parseEntityUri } from "@/lib/entity-routing";


// Helper to extract entity ID from URI for frontend links
export function getEntityLink(uri: string): { type: string; id: string } | null {
  return parseEntityUri(uri);
}

interface EntityLinkProps {
  label: string;
  uri: string | null;
  className?: string;
  children?: React.ReactNode;
}

export default function EntityLink({ 
  label, 
  uri, 
  className = "hover:text-indigo-600 hover:underline",
  children
}: EntityLinkProps) {
  if (!uri) {
    return <span>{children || cleanLabel(label)}</span>;
  }
  
  const link = getEntityLink(uri);
  
  if (!link) {
    return <span>{children || cleanLabel(label)}</span>;
  }

  // If we wanted to "support" direct w3id navigation, we would need the server to redirect.
  // Since we are client-side, we intercept and link internally.
  return (
    <Link 
      href={buildDetailHref(link.type, link.id)}
      className={className}
    >
      {children || cleanLabel(label)}
    </Link>
  );
}
