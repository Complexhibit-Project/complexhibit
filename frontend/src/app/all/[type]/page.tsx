import { getFromType } from "@/lib/api";
import InfiniteList from "@/components/InfiniteList";
import { unCamel } from "@/lib/utils";
import { Entity } from "@/lib/types";
import { normalizeListType } from "@/lib/entity-routing";
import { notFound, redirect } from "next/navigation";

interface PageProps {
  params: Promise<{ type: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export default async function ListPage({ params, searchParams }: PageProps) {
  const { type } = await params;
  const rawType = decodeURIComponent(type).toLowerCase();
  const normalizedType = normalizeListType(rawType);

  if (!normalizedType) {
    notFound();
  }

  const allSearchParams = await searchParams;

  if (normalizedType !== rawType) {
    const qs = new URLSearchParams();
    for (const [key, value] of Object.entries(allSearchParams)) {
      if (typeof value === "string") {
        qs.set(key, value);
      } else if (Array.isArray(value)) {
        value.forEach((v) => qs.append(key, v));
      }
    }
    const suffix = qs.toString() ? `?${qs.toString()}` : "";
    redirect(`/all/${normalizedType}${suffix}`);
  }
  
  let initialData: Entity[] = [];
  let initialCursor: string | null = null;

  try {
    const apiParams: Record<string, string> = {};
    for (const [key, value] of Object.entries(allSearchParams)) {
      if (typeof value === "string" && value.trim()) {
        apiParams[key] = value;
      } else if (Array.isArray(value) && value.length > 0 && value[0]) {
        apiParams[key] = value[0];
      }
    }

    const response = await getFromType(normalizedType, apiParams);
    
    if (response) {
        if (response.data) {
             // Handle if data is array or object wrapped
            if (Array.isArray(response.data)) {
                initialData = response.data;
            } else {
                 // Try to convert object values to array if needed, though backend seems to return list now
                initialData = (Object.values(response.data).flat() as Entity[]); 
            }
        }
        initialCursor = response.next_cursor || null;
    }
  } catch (error) {
    console.error("Failed to fetch initial data:", error);
  }

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
      <div className="md:flex md:items-center md:justify-between mb-8">
        <div className="min-w-0 flex-1">
          <h2 className="text-3xl font-bold leading-7 text-gray-900 sm:truncate sm:tracking-tight mb-2">
            All {unCamel(normalizedType)}s
          </h2>
          <p className="text-gray-500">Browse and search the complete catalog.</p>
        </div>
      </div>

      <InfiniteList 
        initialData={initialData} 
        initialCursor={initialCursor} 
        type={normalizedType} 
      />
    </div>
  );
}
