import { createContext, useContext, useState, useEffect } from 'react';
import api from '../api';
import { clearTokens, getAccessToken, setTokens } from '../authStorage';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getAccessToken();
    if (token) {
      api.get('/auth/me/')
        .then(({ data }) => setUser(data))
        .catch(() => {
          clearTokens();
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (username, password) => {
    const { data } = await api.post('/auth/login/', { username, password });
    setTokens(data.tokens);
    setUser(data.user);
    return data.user;
  };

  const logout = () => {
    clearTokens();
    setUser(null);
  };

  const updateProfile = async (changes) => {
    const { data } = await api.put('/auth/me/', changes);
    setUser(data);
    return data;
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, updateProfile }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
