const BASE = import.meta.env.VITE_API_BASE_URL || '/api';

const authHeader = () => {
  const t = localStorage.getItem('accessToken');
  return t ? { Authorization: `Bearer ${t}` } : {};
};

async function refresh() {
  const r = localStorage.getItem('refreshToken');
  if (!r) return null;
  const res = await fetch(`${BASE}/auth/token/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: r }),
  });
  if (!res.ok) return null;
  const data = await res.json();
  localStorage.setItem('accessToken', data.access);
  return data.access;
}

export async function apiFetch(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}), ...authHeader() },
  });
  if (res.status !== 401) return res;
  const newTok = await refresh();
  if (!newTok) return res;
  return fetch(`${BASE}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}), Authorization: `Bearer ${newTok}` },
  });
}
