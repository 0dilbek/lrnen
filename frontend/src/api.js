import axios from 'axios';
import {
  clearTokens, getAccessToken, getRefreshToken, setAccessToken,
} from './authStorage';

const api = axios.create({
  baseURL: '/api',
});

export function getApiErrorMessage(error, fallback = 'Amalni bajarishda xatolik yuz berdi') {
  const data = error?.response?.data;
  if (error?.response?.status === 403) {
    return 'Administrator huquqi tasdiqlanmadi. Qayta tizimga kirib ko‘ring.';
  }
  if (error?.response?.status >= 500) {
    return 'Server ma’lumotni saqlay olmadi. Administratorga murojaat qiling.';
  }
  if (typeof data === 'string' && data.trim()) return data;
  if (typeof data?.detail === 'string' && data.detail.trim()) return data.detail;
  if (data && typeof data === 'object') {
    const messages = Object.values(data)
      .flatMap((value) => Array.isArray(value) ? value : [value])
      .filter((value) => typeof value === 'string' && value.trim());
    if (messages.length) return messages.join(' ');
  }
  return fallback;
}

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = getRefreshToken();
      if (refresh) {
        try {
          const { data } = await axios.post('/api/auth/token/refresh/', { refresh });
          setAccessToken(data.access);
          original.headers.Authorization = `Bearer ${data.access}`;
          return api(original);
        } catch {
          clearTokens();
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
