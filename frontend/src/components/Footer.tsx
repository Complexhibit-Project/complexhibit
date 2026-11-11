import Link from 'next/link';
import { Twitter, Globe } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="mx-auto max-w-7xl px-6 py-8 lg:px-8">
        <div className="md:flex md:items-center md:justify-between">
          
          {/* Social Media & Links */}
          <div className="flex justify-center space-x-6 md:order-2">
            <Link 
              href="https://iarthis.iarthislab.eu/" 
              target="_blank" 
              rel="noopener noreferrer" 
              className="text-gray-400 hover:text-gray-500"
              title="iArtHIS_lab Website"
            >
              <span className="sr-only">Website</span>
              <Globe className="h-5 w-5" />
            </Link>
            
            <Link 
              href="https://x.com/iArtHislab" 
              target="_blank" 
              rel="noopener noreferrer" 
              className="text-gray-400 hover:text-gray-500"
              title="Twitter / X"
            >
              <span className="sr-only">Twitter</span>
              <Twitter className="h-5 w-5" />
            </Link>

             <Link href="/privacy" className="text-sm leading-6 text-gray-500 hover:text-gray-900 flex items-center">
              Privacy Policy
            </Link>
          </div>

          {/* Copyright text */}
          <div className="mt-8 md:order-1 md:mt-0">
            <p className="text-center text-xs leading-5 text-gray-500">
              &copy; {new Date().getFullYear()} Complexhibit. All rights reserved. <span className="mx-1">|</span> Developed by <a href="https://iarthis.iarthislab.eu/" target="_blank" rel="noopener noreferrer" className="hover:underline font-medium">iArtHIS_lab</a> - Universidad de Málaga.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
