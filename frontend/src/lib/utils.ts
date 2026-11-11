import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function unCamel(str: string): string {
  if (!str) return "";
  // Insert space before capital letters (for camelCase)
  const result = str.replace(/([A-Z])/g, " $1").trim();
  // Capitalize first letter of each word
  return result
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

export function obtainTranslatedType(str: string): string | null {
  if (str.includes("ex")) {
    return "exhibition";
  } else if (str.includes("obra")) {
    return "artwork";
  } else if (str.includes("dispositivo")) {
    return "inscription device";
  } else if (str.includes("inst")) {
    return "institution";
  } else if (str.includes("person") || str.includes("actant")) {
    return "actor";
  }
  return null;
}

export function cleanLabel(label: unknown): string {
  // Handle null, undefined, or empty values
  if (!label) return "";
  
  // Handle arrays - join non-empty values or return empty string
  if (Array.isArray(label)) {
    const nonEmpty = label.filter(Boolean);
    if (nonEmpty.length === 0) return "";
    return cleanLabel(nonEmpty[0]); // Clean the first item
  }
  
  // Ensure we have a string
  if (typeof label !== 'string') {
    return String(label);
  }
  
  // If label contains " (http", it might be "Name (URI) ..."
  // We want to extract "Name"
  const uriMatch = label.match(/^(.*?)\s*\(https?:\/\//);
  if (uriMatch && uriMatch[1]) {
    return uriMatch[1].trim();
  }
  
  // If label contains " was ", take the part before it
  const wasMatch = label.match(/^(.*?)\s+was\s+/);
  if (wasMatch && wasMatch[1]) {
      // Check if it also has a URI pattern we missed or if this is cleaner
      return wasMatch[1].trim();
  }

  return label;
}
