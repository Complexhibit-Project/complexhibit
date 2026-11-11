"use client";

/**
 * Navigation bar with authentication state.
 */

import Link from "next/link";
import { useState, useEffect } from "react";
import { Menu, X, Home, Search, Code, FileText, Users, LogIn, LogOut, Shield, User, PlusCircle, Map as MapIcon, BarChart, Network } from "lucide-react";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";

const navigation = [
  { name: "Home", href: "/", icon: Home },
  { name: "Search", href: "/search", icon: Search },
  { name: "Graph", href: "/graph", icon: Network },
  { name: "Map", href: "/map", icon: MapIcon },
  { name: "SPARQL", href: "/sparql", icon: Code },
  { name: "Reports", href: "/reports", icon: FileText },
  { name: "About", href: "/about", icon: Users },
];

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const pathname = usePathname();
  const { user, isAuthenticated, isAdmin, isLoading, logout } = useAuth();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header 
      className={cn(
        "sticky top-0 z-50 transition-all duration-300",
        scrolled 
          ? "glass shadow-xl backdrop-blur-xl border-b border-indigo-200/50" 
          : "bg-white/80 backdrop-blur-sm shadow-sm border-b border-gray-100"
      )}
    >
      <nav className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8" aria-label="Global">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Link href="/" className="font-bold text-2xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent hover:from-indigo-700 hover:via-purple-700 hover:to-pink-700 transition-all">
              Complexhibit
            </Link>
          </div>

          {/* Desktop navigation - center */}
          <div className="hidden lg:flex lg:items-center lg:gap-x-6">
            {navigation.map((item) => (
              <Link 
                key={item.name} 
                href={item.href} 
                className="text-sm font-medium text-gray-700 hover:text-indigo-600 flex items-center gap-1.5 transition-colors"
              >
                <item.icon className="h-4 w-4" />
                {item.name}
              </Link>
            ))}
            {isAuthenticated && (
              <Link 
                href="/insert" 
                className="text-sm font-medium text-emerald-600 hover:text-emerald-700 flex items-center gap-1.5 transition-colors"
              >
                <PlusCircle className="h-4 w-4" />
                Insert
              </Link>
            )}
            {isAdmin && (
              <>
                <Link 
                  href="/admin/users" 
                  className="text-sm font-medium text-purple-600 hover:text-purple-700 flex items-center gap-1.5 transition-colors"
                >
                  <Shield className="h-4 w-4" />
                  Users
                </Link>
                <Link 
                  href="/admin/metrics" 
                  className="text-sm font-medium text-blue-600 hover:text-blue-700 flex items-center gap-1.5 transition-colors"
                >
                  <BarChart className="h-4 w-4" />
                  Metrics
                </Link>
              </>
            )}
          </div>

          {/* Desktop auth - right */}
          <div className="hidden lg:flex lg:items-center lg:gap-4">
            {isLoading ? (
              <div className="h-5 w-5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
            ) : isAuthenticated ? (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <div className="h-8 w-8 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 flex items-center justify-center text-white text-sm font-medium flex-shrink-0">
                    {user?.username?.[0]?.toUpperCase() || <User className="h-4 w-4" />}
                  </div>
                  <span className="text-sm font-medium text-gray-700 max-w-[120px] truncate">
                    {user?.full_name || user?.username}
                  </span>
                </div>
                <button
                  onClick={logout}
                  className="text-sm font-medium text-gray-500 hover:text-red-600 flex items-center gap-1 transition-colors"
                >
                  <LogOut className="h-4 w-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link 
                  href="/auth/register" 
                  className="text-sm font-medium text-gray-600 hover:text-indigo-600 transition-colors"
                >
                  Register
                </Link>
                <Link 
                  href={`/auth/login?callbackUrl=${encodeURIComponent(pathname)}`}
                  className="text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors"
                >
                  <LogIn className="h-4 w-4" />
                  Log in
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="flex lg:hidden">
            <button
              type="button"
              className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-gray-700"
              onClick={() => setMobileMenuOpen(true)}
            >
              <span className="sr-only">Open main menu</span>
              <Menu className="h-6 w-6" aria-hidden="true" />
            </button>
          </div>
        </div>
      </nav>
      
      {/* Mobile menu */}
      <div className={cn("lg:hidden", mobileMenuOpen ? "fixed inset-0 z-50" : "hidden")}>
        <div className="fixed inset-0 bg-black/20" onClick={() => setMobileMenuOpen(false)} />
        <div className="fixed inset-y-0 right-0 z-50 w-full overflow-y-auto bg-white px-6 py-6 sm:max-w-sm sm:ring-1 sm:ring-gray-900/10">
          <div className="flex items-center justify-between">
            <Link href="/" className="font-bold text-xl text-indigo-600" onClick={() => setMobileMenuOpen(false)}>
              Complexhibit
            </Link>
            <button
              type="button"
              className="-m-2.5 rounded-md p-2.5 text-gray-700"
              onClick={() => setMobileMenuOpen(false)}
            >
              <span className="sr-only">Close menu</span>
              <X className="h-6 w-6" aria-hidden="true" />
            </button>
          </div>
          
          <div className="mt-6 flow-root">
            <div className="-my-6 divide-y divide-gray-500/10">
              {/* User info for mobile */}
              {isAuthenticated && (
                <div className="py-4 flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 flex items-center justify-center text-white font-medium flex-shrink-0">
                    {user?.username?.[0]?.toUpperCase() || '?'}
                  </div>
                  <div className="min-w-0">
                    <div className="font-medium text-gray-900 truncate">{user?.full_name || user?.username}</div>
                    <div className="text-sm text-gray-500 truncate">{user?.email}</div>
                  </div>
                </div>
              )}

              {/* Navigation links */}
              <div className="space-y-1 py-6">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    className="-mx-3 flex items-center gap-3 rounded-lg px-3 py-2 text-base font-medium text-gray-900 hover:bg-gray-50"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <item.icon className="h-5 w-5 text-gray-400" />
                    {item.name}
                  </Link>
                ))}
                {isAuthenticated && (
                  <Link
                    href="/insert"
                    className="-mx-3 flex items-center gap-3 rounded-lg px-3 py-2 text-base font-medium text-emerald-600 hover:bg-emerald-50"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <PlusCircle className="h-5 w-5" />
                    Insert Data
                  </Link>
                )}
                {isAdmin && (
                  <Link
                    href="/admin/users"
                    className="-mx-3 flex items-center gap-3 rounded-lg px-3 py-2 text-base font-medium text-purple-600 hover:bg-purple-50"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <Shield className="h-5 w-5" />
                    Admin Panel
                  </Link>
                )}
              </div>

              {/* Auth buttons for mobile */}
              <div className="py-6">
                {isAuthenticated ? (
                  <button
                    onClick={() => { logout(); setMobileMenuOpen(false); }}
                    className="-mx-3 flex items-center gap-3 rounded-lg px-3 py-2.5 text-base font-medium text-red-600 hover:bg-red-50 w-full"
                  >
                    <LogOut className="h-5 w-5" />
                    Log out
                  </button>
                ) : (
                  <div className="space-y-2">
                    <Link
                      href={`/auth/login?callbackUrl=${encodeURIComponent(pathname)}`}
                      className="-mx-3 flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-3 py-2.5 text-base font-medium text-white hover:bg-indigo-700"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      <LogIn className="h-5 w-5" />
                      Log in
                    </Link>
                    <Link
                      href="/auth/register"
                      className="-mx-3 flex items-center justify-center gap-2 rounded-lg px-3 py-2.5 text-base font-medium text-gray-900 hover:bg-gray-50"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      Create account
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
