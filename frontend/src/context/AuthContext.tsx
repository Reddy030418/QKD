import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';
import { apiGet, apiPost } from '../utils/api';

interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'user';
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const persistAuth = (nextToken: string, nextRefreshToken: string, nextUser: User) => {
    setToken(nextToken);
    setRefreshToken(nextRefreshToken);
    setUser(nextUser);
    localStorage.setItem('token', nextToken);
    localStorage.setItem('refresh_token', nextRefreshToken);
    localStorage.setItem('user', JSON.stringify(nextUser));
  };

  const clearAuth = () => {
    setUser(null);
    setToken(null);
    setRefreshToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  };

  const refreshAccessToken = async (storedRefreshToken: string): Promise<string | null> => {
    try {
      const data = await apiPost<{ access_token: string }>('/auth/refresh', {
        refresh_token: storedRefreshToken,
      });
      if (!data.access_token) {
        return null;
      }

      setToken(data.access_token);
      localStorage.setItem('token', data.access_token);
      return data.access_token;
    } catch (error) {
      console.error('Token refresh error:', error);
      return null;
    }
  };

  const verifyAccessToken = async (candidateToken: string): Promise<boolean> => {
    try {
      await apiGet('/auth/me', {
        headers: { Authorization: `Bearer ${candidateToken}` },
      });
      return true;
    } catch {
      return false;
    }
  };

  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem('token');
      const storedRefreshToken = localStorage.getItem('refresh_token');
      const storedUser = localStorage.getItem('user');

      if (!storedRefreshToken || !storedUser) {
        setIsLoading(false);
        return;
      }

      try {
        const parsedUser = JSON.parse(storedUser) as User;
        let usableToken = storedToken || null;

        if (usableToken) {
          const isValid = await verifyAccessToken(usableToken);
          if (!isValid) {
            usableToken = null;
          }
        }

        if (!usableToken) {
          usableToken = await refreshAccessToken(storedRefreshToken);
        }

        if (!usableToken) {
          clearAuth();
          setIsLoading(false);
          return;
        }

        setToken(usableToken);
        setRefreshToken(storedRefreshToken);
        setUser(parsedUser);
      } catch (error) {
        console.error('Error initializing auth:', error);
        clearAuth();
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const login = async (username: string, password: string) => {
    try {
      const data = await apiPost<any>('/auth/login', { username, password });

      persistAuth(data.access_token, data.refresh_token, {
        id: data.user.id,
        username: data.user.username,
        email: data.user.email,
        role: data.user.role,
      });
    } catch (error) {
      throw new Error(extractApiErrorMessage(error, 'Login failed'));
    }
  };

  const register = async (username: string, email: string, password: string) => {
    try {
      await apiPost('/auth/register', { username, email, password });
    } catch (error) {
      throw new Error(extractApiErrorMessage(error, 'Registration failed'));
    }
  };

  const logout = async () => {
    try {
      if (token) {
        await apiPost('/auth/logout');
      }
    } catch (error) {
      console.error('Logout API error:', error);
    } finally {
      clearAuth();
    }
  };

  const value: AuthContextType = {
    user,
    token,
    refreshToken,
    login,
    register,
    logout,
    isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
  const extractApiErrorMessage = (error: unknown, fallback: string): string => {
    if (!axios.isAxiosError(error)) {
      return fallback;
    }

    const data = error.response?.data as
      | { detail?: string; errors?: Array<{ msg?: string }> }
      | undefined;

    if (typeof data?.detail === 'string' && data.detail.trim().length > 0) {
      if (data.detail === 'Invalid request payload' && Array.isArray(data.errors) && data.errors.length > 0) {
        const first = data.errors[0]?.msg;
        if (first) {
          return first;
        }
      }
      return data.detail;
    }

    const errors = data?.errors;
    if (Array.isArray(errors) && errors.length > 0) {
      const first = errors[0]?.msg;
      if (first) {
        return first;
      }
    }

    return fallback;
  };
