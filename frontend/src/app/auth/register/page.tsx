"use client";

import { API_URL } from "@/lib/config";
import { useState, useEffect, ChangeEvent, FormEvent } from "react";
import Link from "next/link";
import { UserPlus, Mail, Lock, User, AlertCircle, CheckCircle, Loader2, Building, ChevronDown } from "lucide-react";

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: "",
    username: "",
    password: "",
    confirmPassword: "",
    fullName: "",
    userType: "individual",
    institutionType: "",
  });
  const [institutionTypes, setInstitutionTypes] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const FALLBACK_TYPES = ["Museum", "University", "Gallery", "Art Center", "Other"];

  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  useEffect(() => {
    const fetchInstitutionTypes = async () => {
      try {
        const apiUrl = API_URL;
        const response = await fetch(`${apiUrl}/filter_options/institution_type`);
        if (response.ok) {
          const data = await response.json();
          setInstitutionTypes(data.data && data.data.length > 0 ? data.data : FALLBACK_TYPES);
        } else {
          setInstitutionTypes(FALLBACK_TYPES);
        }
      } catch (error) {
        setInstitutionTypes(FALLBACK_TYPES);
      }
    };
    fetchInstitutionTypes();
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    setIsLoading(true);

    try {
      const apiUrl = API_URL;
      const response = await fetch(`${apiUrl}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: formData.email,
          username: formData.username,
          password: formData.password,
          full_name: formData.fullName || null,
          user_type: formData.userType,
          institution_type: formData.userType === 'institution' ? formData.institutionType : null,
        }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Registration failed");
      setSuccess(true);
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 via-white to-emerald-50 py-12 px-4 shadow-[inset_0_0_100px_rgba(0,0,0,0.02)]">
        <div className="max-w-md w-full space-y-8 p-10 bg-white rounded-3xl shadow-2xl border border-white text-center animate-in fade-in zoom-in duration-500">
          <div className="mx-auto h-20 w-20 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full flex items-center justify-center shadow-lg shadow-green-100">
            <CheckCircle className="h-10 w-10 text-white" />
          </div>
          <h2 className="text-3xl font-extrabold text-gray-900 tracking-tight">Registration Sent!</h2>
          <p className="text-gray-600 leading-relaxed">Your account has been created and is <b>pending administrator approval</b>. We will notify you by email once it is reviewed.</p>
          <Link href="/" className="inline-block px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-bold hover:shadow-xl hover:shadow-indigo-200 transition-all active:scale-95">
            Back to Home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50 py-12 px-4">
      <div className="max-w-md w-full space-y-8 bg-white/80 backdrop-blur-xl p-10 rounded-3xl shadow-2xl border border-white">
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-xl shadow-indigo-100">
            <UserPlus className="h-8 w-8 text-white" />
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900 tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-gray-900 to-gray-600">Create account</h2>
        </div>

        <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-100 text-red-600 px-4 py-3 rounded-xl flex items-center gap-3 text-sm animate-shake">
              <AlertCircle className="h-5 w-5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="space-y-4">
            <div className="relative group">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 group-focus-within:text-indigo-600 transition-colors" />
              <input name="email" type="email" required placeholder="Email address *" onChange={handleChange}
                className="block w-full pl-10 pr-4 py-3 bg-gray-50/50 border-gray-200 border rounded-xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all outline-none" />
            </div>

            <div className="relative group">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 group-focus-within:text-indigo-600 transition-colors" />
              <input name="username" type="text" required placeholder="Username *" onChange={handleChange}
                className="block w-full pl-10 pr-4 py-3 bg-gray-50/50 border-gray-200 border rounded-xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all outline-none" />
            </div>

            <div className="relative group">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 group-focus-within:text-indigo-600 transition-colors" />
              <input name="fullName" type="text" placeholder="Full name (optional)" value={formData.fullName} onChange={handleChange}
                className="block w-full pl-10 pr-4 py-3 bg-gray-50/50 border-gray-200 border rounded-xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all outline-none" />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button type="button" onClick={() => setFormData({...formData, userType: 'individual'})}
                className={`flex items-center justify-center gap-2 p-3 rounded-xl border-2 transition-all font-semibold ${formData.userType==='individual'?'border-indigo-600 bg-indigo-50 text-indigo-700 shadow-sm shadow-indigo-100':'border-gray-100 bg-gray-50/50 text-gray-500 hover:border-gray-200'}`}>
                <User className="h-4 w-4" /> Individual
              </button>
              <button type="button" onClick={() => setFormData({...formData, userType: 'institution'})}
                className={`flex items-center justify-center gap-2 p-3 rounded-xl border-2 transition-all font-semibold ${formData.userType==='institution'?'border-indigo-600 bg-indigo-50 text-indigo-700 shadow-sm shadow-indigo-100':'border-gray-100 bg-gray-50/50 text-gray-500 hover:border-gray-200'}`}>
                <Building className="h-4 w-4" /> Institution
              </button>
            </div>

            {formData.userType === 'institution' && (
              <div className="relative animate-in slide-in-from-top-2 duration-300">
                <Building className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <select name="institutionType" required onChange={handleChange}
                  className="block w-full pl-10 pr-10 py-3 bg-gray-50/50 border-gray-200 border rounded-xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all outline-none appearance-none cursor-pointer">
                  <option value="">Select Institution type *</option>
                  {institutionTypes.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none" />
              </div>
            )}

            <div className="relative group">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 group-focus-within:text-indigo-600 transition-colors" />
              <input name="password" type="password" required minLength={8} placeholder="Password * (min. 8 characters)" onChange={handleChange}
                className="block w-full pl-10 pr-4 py-3 bg-gray-50/50 border-gray-200 border rounded-xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all outline-none" />
            </div>

            <div className="relative group">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 group-focus-within:text-indigo-600 transition-colors" />
              <input name="confirmPassword" type="password" required placeholder="Confirm Password *" onChange={handleChange}
                className="block w-full pl-10 pr-4 py-3 bg-gray-50/50 border-gray-200 border rounded-xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all outline-none" />
            </div>
          </div>

          <button type="submit" disabled={isLoading}
            className="w-full flex justify-center items-center py-4 px-4 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white rounded-2xl font-bold shadow-xl shadow-indigo-100 transition-all disabled:opacity-50 active:scale-[0.98]">
            {isLoading ? <Loader2 className="h-6 w-6 animate-spin" /> : <><UserPlus className="h-5 w-5 mr-2" /> Create account</>}
          </button>
        </form>
      </div>
    </div>
  );
}
