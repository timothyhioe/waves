// API Config
// For Kubernetes with Ingress: use relative URL (empty string)
// For local dev: use http://localhost:5000
// React env vars are embedded at BUILD TIME
export const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

export const apiEndpoint = (path) => {
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  // If API_URL is empty/relative, just return the path (works with Ingress)
  // This allows the same origin policy - frontend and backend on same domain
  if (!API_URL || API_URL === "") {
    return cleanPath;
  }
  return `${API_URL}${cleanPath}`;
};
