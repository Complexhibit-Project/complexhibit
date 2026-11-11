"use client";

import { useState } from "react";
import { submitReport } from "@/lib/api";

export default function ReportsPage() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    type: "bug",
    description: ""
  });
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("submitting");
    try {
      await submitReport(formData);
      setStatus("success");
      setFormData({ name: "", email: "", type: "bug", description: "" });
    } catch (err) {
      console.error(err);
      setStatus("error");
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6 lg:px-8">
      <h1 className="text-3xl font-bold mb-6 text-gray-900">Report an Incident</h1>
      <p className="mb-8 text-gray-600">
        Found a bug, data error, or have a suggestion? Please let us know by filling out the form below.
      </p>

      {status === "success" ? (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-8 rounded-lg text-center shadow-sm">
            <h3 className="text-lg font-bold mb-2">Thank you!</h3>
            <p className="mb-4">Your report has been submitted successfully.</p>
            <button 
                onClick={() => setStatus("idle")}
                className="text-indigo-600 hover:text-indigo-800 font-medium hover:underline"
            >
                Submit another report
            </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6 bg-white p-8 rounded-lg shadow-sm border border-gray-100">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
                <label className="block text-sm font-medium text-gray-700">Name</label>
                <input
                type="text"
                required
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                />
            </div>
            <div>
                <label className="block text-sm font-medium text-gray-700">Email (optional)</label>
                <input
                type="email"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Type</label>
            <select
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border bg-white"
                value={formData.type}
                onChange={(e) => setFormData({...formData, type: e.target.value})}
            >
                <option value="bug">Bug Report</option>
                <option value="data_error">Data Error</option>
                <option value="feature_request">Feature Request</option>
                <option value="other">Other</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Description</label>
            <textarea
              required
              rows={5}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
              placeholder="Please describe the issue or suggestion..."
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
            />
          </div>
          
          {status === "error" && (
             <div className="text-red-600 text-sm bg-red-50 p-2 rounded">
                 Failed to submit report. Please try again.
             </div>
          )}

          <div className="flex justify-end">
            <button
                type="submit"
                disabled={status === "submitting"}
                className="inline-flex justify-center py-2 px-6 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 transition-colors"
            >
                {status === "submitting" ? "Submitting..." : "Submit Report"}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
