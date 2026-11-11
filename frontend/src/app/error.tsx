'use client';

import { useEffect } from 'react';
import { AlertTriangle, RefreshCcw } from 'lucide-react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error(error);
  }, [error]);

  return (
    <div className="flex h-[calc(100vh-4rem)] w-full items-center justify-center bg-gray-50 px-4">
      <div className="flex flex-col items-center gap-6 text-center max-w-md">
        <div className="bg-red-50 p-4 rounded-full">
            <AlertTriangle className="h-8 w-8 text-red-600" />
        </div>
        <div className="space-y-2">
            <h2 className="text-2xl font-bold text-gray-900">Something went wrong!</h2>
            <p className="text-gray-600">
            We apologize for the inconvenience. The application encountered an unexpected error.
            </p>
            {process.env.NODE_ENV === 'development' && (
                <div className="mt-2 p-3 bg-red-50 rounded-lg text-left text-xs font-mono text-red-800 overflow-auto max-h-32 w-full">
                    {error.message}
                </div>
            )}
        </div>
        <button
          onClick={
            // Attempt to recover by trying to re-render the segment
            () => reset()
          }
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 transition-all hover:scale-105"
        >
          <RefreshCcw className="h-4 w-4" />
          Try again
        </button>
      </div>
    </div>
  );
}
