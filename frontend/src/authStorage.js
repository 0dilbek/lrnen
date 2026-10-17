const ACCESS_KEY = 'access_token';
const REFRESH_KEY = 'refresh_token';

function migrateLegacyTokens() {
  if (!sessionStorage.getItem(ACCESS_KEY)) {
    const legacyAccess = localStorage.getItem(ACCESS_KEY);
    const legacyRefresh = localStorage.getItem(REFRESH_KEY);
    if (legacyAccess) sessionStorage.setItem(ACCESS_KEY, legacyAccess);
    if (legacyRefresh) sessionStorage.setItem(REFRESH_KEY, legacyRefresh);
  }
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export function getAccessToken() {
  migrateLegacyTokens();
  return sessionStorage.getItem(ACCESS_KEY);
}

export function getRefreshToken() {
  migrateLegacyTokens();
  return sessionStorage.getItem(REFRESH_KEY);
}

export function setTokens(tokens) {
  sessionStorage.setItem(ACCESS_KEY, tokens.access);
  sessionStorage.setItem(REFRESH_KEY, tokens.refresh);
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export function setAccessToken(token) {
  sessionStorage.setItem(ACCESS_KEY, token);
}

export function clearTokens() {
  sessionStorage.removeItem(ACCESS_KEY);
  sessionStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}
