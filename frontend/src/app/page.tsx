import Link from "next/link";
import { ArrowRight, BookOpen, Building2, Calendar, Users, Image as ImageIcon, FileText, Network } from "lucide-react";
import HashRedirect from "@/components/HashRedirect";
import { 
  getExhibitionsCount, 
  getArtworksCount, 
  getPersonsCount, 
  getInstitutionsCount,
  getCatalogsCount
} from "@/lib/api";

export const dynamic = 'force-dynamic';

interface Category {
  name: string;
  description: string;
  href: string;
  icon: React.ElementType;
  color: string;
  countKey: string;
  /** Card without a destination page yet: rendered as a non-link, with no count or CTA. */
  inactive?: boolean;
}

const initialCategories: Category[] = [
  {
    name: "Exhibitions",
    description: "Explore curated exhibitions from various institutions.",
    href: "/all/exhibition",
    icon: Calendar,
    color: "bg-blue-500",
    countKey: "exhibitions",
  },
  {
    name: "Artworks",
    description: "Discover individual artworks and their details.",
    href: "/all/artwork",
    icon: ImageIcon,
    color: "bg-purple-500",
    countKey: "artworks",
  },
  {
    name: "People & Groups",
    description: "Learn about the people and organizations involved.",
    href: "/all/person",
    icon: Users,
    color: "bg-orange-500",
    countKey: "persons",
  },
  {
    name: "Institutions",
    description: "Find museums, galleries, and other cultural institutions.",
    href: "/all/institution",
    icon: Building2,
    color: "bg-green-500",
    countKey: "institutions",
  },
  {
    name: "Catalogs",
    description: "Browse exhibition catalogs and documentation resources.",
    href: "/all/catalog",
    icon: BookOpen,
    color: "bg-amber-500",
    countKey: "catalogs",
  },
  {
    name: "Texts",
    description: "Texts and written sources related to exhibitions.",
    href: "#",
    icon: FileText,
    color: "bg-teal-500",
    countKey: "texts",
    inactive: true,
  },
];

export default async function Home() {
  // Server-side data fetching
  const [
    exhibitions, 
    artworks, 
    persons, 
    institutions, 
    catalogs
  ] = await Promise.allSettled([
    getExhibitionsCount(),
    getArtworksCount(),
    getPersonsCount(),
    getInstitutionsCount(),
    getCatalogsCount()
  ]);

  const counts: Record<string, number | null> = {
    exhibitions: exhibitions.status === 'fulfilled' ? exhibitions.value.data.count : null,
    artworks: artworks.status === 'fulfilled' ? artworks.value.data.count : null,
    persons: persons.status === 'fulfilled' ? persons.value.data.count : null,
    institutions: institutions.status === 'fulfilled' ? institutions.value.data.count : null,
    catalogs: catalogs.status === 'fulfilled' ? catalogs.value.data.count : null,
  };

  return (
    <div className="bg-gradient-to-br from-white via-indigo-50/30 to-purple-50/30 min-h-screen">
      <HashRedirect />
      {/* Hero section */}
      <div className="relative isolate px-6 pt-14 lg:px-8 overflow-hidden">
        {/* Animated background gradient blobs */}
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-gradient-to-br from-indigo-300/30 to-purple-300/30 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-gradient-to-br from-pink-300/30 to-orange-300/30 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
        
        <div className="mx-auto max-w-3xl py-32 sm:py-48 lg:py-56 relative z-10">
          <div className="text-center">
            {/* Floating badge */}
            <div className="inline-flex items-center gap-2 glass rounded-full px-4 py-2 mb-8 shadow-lg border border-white/40 animate-float">
              <span className="h-2 w-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 animate-pulse" />
              <span className="text-sm font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                Semantic Web Cultural Heritage Platform
              </span>
            </div>
            
            <h1 className="text-5xl font-extrabold tracking-tight text-gray-900 sm:text-7xl mb-6 leading-tight">
              Explore the World of{" "}
              <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent animate-gradient">
                Exhibitions
              </span>
            </h1>
            <p className="mt-6 text-xl leading-8 text-gray-700 max-w-2xl mx-auto font-light">
              Complexhibit is your gateway to a semantic web of cultural heritage. 
              Discover connections between <span className="font-semibold text-indigo-600">exhibitions</span>, <span className="font-semibold text-purple-600">artworks</span>, <span className="font-semibold text-pink-600">institutions</span>, and <span className="font-semibold text-orange-600">people</span>.
            </p>
            <div className="mt-12 flex flex-wrap items-center justify-center gap-4">
              <Link
                href="/search"
                className="group relative rounded-2xl bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4 text-base font-semibold text-white shadow-xl hover:shadow-2xl focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 transition-all duration-300 hover:scale-105 hover:-translate-y-1 overflow-hidden"
              >
                <span className="relative z-10">Start Searching</span>
                <div className="absolute inset-0 bg-gradient-to-r from-indigo-700 to-purple-700 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              </Link>
              <Link
                href="/graph"
                className="group flex items-center gap-2 rounded-2xl border-2 border-indigo-200 bg-white/70 px-6 py-4 text-base font-semibold text-indigo-700 shadow-sm backdrop-blur transition-all duration-300 hover:scale-105 hover:-translate-y-1 hover:border-indigo-400 hover:bg-white"
              >
                <Network className="h-5 w-5 transition-transform group-hover:rotate-12" />
                Explore the Graph
              </Link>
              <Link
                href="/about"
                className="group text-base font-semibold leading-6 text-gray-900 hover:text-indigo-600 transition-colors flex items-center gap-2"
              >
                Learn more
                <span aria-hidden="true" className="group-hover:translate-x-1 transition-transform inline-block">→</span>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Categories section */}
      <div className="mx-auto max-w-7xl px-6 lg:px-8 pb-24 relative">
        <div className="mx-auto max-w-2xl lg:max-w-none">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl mb-4">
              Browse by Category
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Explore our diverse collection organized by type
            </p>
          </div>
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {initialCategories.map((category, index) => {
              const Card: React.ElementType = category.inactive ? "div" : Link;
              const cardProps = category.inactive
                ? { "aria-disabled": true }
                : { href: category.href };
              return (
              <Card
                key={category.name}
                {...cardProps}
                className={`group relative flex flex-col overflow-hidden rounded-3xl bg-white shadow-lg ring-1 ring-gray-200/50 transition-all duration-500 ${
                  category.inactive
                    ? "cursor-default"
                    : "hover:ring-indigo-500/50 hover:-translate-y-2 hover:shadow-2xl"
                }`}
                style={{ animationDelay: `${index * 100}ms` }}
              >
                {/* Gradient overlay on hover */}
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 via-purple-500/5 to-pink-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                
                <div className={`relative flex h-40 items-center justify-center ${category.color} bg-opacity-10 overflow-hidden transition-all duration-500 group-hover:bg-opacity-20`}>
                  {/* Decorative background blob */}
                  <div className={`absolute w-32 h-32 ${category.color} rounded-full opacity-10 blur-2xl group-hover:scale-150 transition-transform duration-700`} />
                  <category.icon className={`relative z-10 h-16 w-16 text-black transition-all duration-500 group-hover:scale-110 group-hover:rotate-6`} />
                  
                  {/* Count Display */}
                  {!category.inactive && (
                    <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-bold shadow-sm flex items-center gap-1">
                      <span>{counts[category.countKey] !== null ? counts[category.countKey] : '-'}</span>
                    </div>
                  )}
                </div>
                <div className="relative flex flex-1 flex-col justify-between p-6">
                  <div className="flex-1">
                    <h3 className="text-2xl font-bold text-gray-900 group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-indigo-600 group-hover:to-purple-600 group-hover:bg-clip-text transition-all duration-300 mb-3">
                      {!category.inactive && <span className="absolute inset-0" />}
                      {category.name}
                    </h3>
                    <p className="text-base text-gray-600 leading-relaxed">{category.description}</p>
                  </div>
                  {!category.inactive && (
                    <div className="mt-6 flex items-center font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent group-hover:translate-x-1 transition-transform">
                      Browse {category.name} <ArrowRight className="ml-2 h-5 w-5 text-indigo-600 group-hover:text-purple-600 transition-colors" />
                    </div>
                  )}
                </div>
              </Card>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
