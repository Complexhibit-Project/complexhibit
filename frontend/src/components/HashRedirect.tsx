"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getEntityLink } from "./EntityLink";
import { buildDetailHref } from "@/lib/entity-routing";

export default function HashRedirect() {
  const router = useRouter();

  useEffect(() => {
    // Check if there is a hash in the URL (e.g., #actor/123)
    if (typeof window !== "undefined" && window.location.hash) {
      const hash = window.location.hash; // e.g., "#actor/123"
      
      // Simulate a full URI to use the existing parser
      // The parser expects "something#type/id"
      const dummyUri = `https://mock${hash}`;
      
      const link = getEntityLink(dummyUri);
      
      if (link) {
        // Redirect to the internal detail page
        router.push(buildDetailHref(link.type, link.id));
      }
    }
  }, [router]);

  return null;
}
