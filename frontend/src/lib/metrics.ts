import { API_URL } from "./config";
/**
 * Metrics utility for tracking user events.
 */

export async function trackEvent(eventType: string, payload: Record<string, unknown> = {}) {
  try {
    const apiUrl = API_URL;
    const token = localStorage.getItem("access_token");
    
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    await fetch(`${apiUrl}/metrics/`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        event_type: eventType,
        payload,
      }),
    });
  } catch (error) {
    console.warn("Failed to track event:", error);
  }
}
