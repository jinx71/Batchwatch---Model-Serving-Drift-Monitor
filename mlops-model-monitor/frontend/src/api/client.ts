import axios from 'axios';

// Vite inlines VITE_* at build time, so changing the API URL requires a
// rebuild of the frontend (not just a restart).
const baseURL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export const client = axios.create({
  baseURL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});
