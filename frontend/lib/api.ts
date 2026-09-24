const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export { API_BASE_URL };

// Route handlers, request helpers, and typed API calls are added phase by
// phase as the backend endpoints they wrap come online (see root README).
