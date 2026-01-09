export const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

export const apiEndpoint = (path) => {
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_URL}${cleanPath}`;
};
