import Link from 'next/link';
import { FileQuestion, Home } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="flex h-[calc(100vh-4rem)] w-full items-center justify-center bg-gray-50 px-4">
      <div className="flex flex-col items-center gap-6 text-center max-w-md">
        <div className="bg-indigo-50 p-4 rounded-full">
            <FileQuestion className="h-8 w-8 text-indigo-600" />
        </div>
        <div className="space-y-2">
            <h2 className="text-2xl font-bold text-gray-900">Page Not Found</h2>
            <p className="text-gray-600">
            Could not find the requested resource. The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.
            </p>
        </div>
        <Link
          href="/"
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 transition-all hover:scale-105"
        >
          <Home className="h-4 w-4" />
          Return Home
        </Link>
      </div>
    </div>
  );
}
