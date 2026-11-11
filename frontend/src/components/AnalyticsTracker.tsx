"use client";

import { useEffect } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import { trackEvent } from "@/lib/metrics";

export function AnalyticsTracker() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    // Track page view
    const url = pathname + (searchParams?.toString() ? `?${searchParams.toString()}` : "");
    trackEvent("page_view", { url, pathname });
  }, [pathname, searchParams]);

  return null;
}
