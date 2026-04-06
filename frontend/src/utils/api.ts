import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

const DEFAULT_API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const toAltUrl = (url: string) => {
  if (url.includes('localhost')) {
    return url.replace('localhost', '127.0.0.1');
  }
  if (url.includes('127.0.0.1')) {
    return url.replace('127.0.0.1', 'localhost');
  }
  return url;
};

const secondaryApiUrl = toAltUrl(DEFAULT_API_URL);
const apiBases = [DEFAULT_API_URL, secondaryApiUrl].filter((base, idx, arr) => arr.indexOf(base) === idx);

type RetriableConfig = AxiosRequestConfig & { _retry?: boolean };

const createClient = (baseURL: string): AxiosInstance => {
  const client = axios.create({
    baseURL,
    timeout: 15000,
  });

  client.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = (error.config || {}) as RetriableConfig;
      const status = error.response?.status;
      const url = originalRequest.url || '';

      if (
        status === 401 &&
        !originalRequest._retry &&
        !url.includes('/auth/login') &&
        !url.includes('/auth/register') &&
        !url.includes('/auth/refresh')
      ) {
        originalRequest._retry = true;
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          localStorage.removeItem('token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          return Promise.reject(error);
        }

        try {
          const refreshResponse = await axios.post(
            `${baseURL}/auth/refresh`,
            { refresh_token: refreshToken },
            { timeout: 15000 }
          );
          const nextToken = refreshResponse.data?.access_token;
          if (!nextToken) {
            throw new Error('Missing access token');
          }

          localStorage.setItem('token', nextToken);
          originalRequest.headers = originalRequest.headers || {};
          originalRequest.headers.Authorization = `Bearer ${nextToken}`;
          return client(originalRequest);
        } catch {
          localStorage.removeItem('token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          return Promise.reject(error);
        }
      }

      return Promise.reject(error);
    }
  );

  return client;
};

const clients = apiBases.map(createClient);

const isNetworkError = (error: unknown) => {
  if (!axios.isAxiosError(error)) {
    return false;
  }
  return !error.response;
};

const runWithFallback = async <T>(
  runner: (client: AxiosInstance) => Promise<AxiosResponse<T>>
): Promise<AxiosResponse<T>> => {
  let lastError: unknown;
  for (const client of clients) {
    try {
      return await runner(client);
    } catch (error) {
      lastError = error;
      if (!isNetworkError(error)) {
        throw error;
      }
    }
  }
  throw lastError;
};

export const apiGet = async <T>(path: string, config?: AxiosRequestConfig): Promise<T> => {
  const response = await runWithFallback<T>((client) => client.get(path, config));
  return response.data;
};

export const apiPost = async <T>(
  path: string,
  body?: unknown,
  config?: AxiosRequestConfig
): Promise<T> => {
  const response = await runWithFallback<T>((client) => client.post(path, body, config));
  return response.data;
};

export const getApiBaseUrl = () => DEFAULT_API_URL;

export const getWebSocketCandidates = (path: string): string[] => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return apiBases.map((base) =>
    `${base}${normalizedPath}`.replace(/^http:/, 'ws:').replace(/^https:/, 'wss:')
  );
};

export const fetchApi = async (path: string, init?: RequestInit): Promise<Response> => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  const primaryBase = DEFAULT_API_URL;
  const secondaryBase = toAltUrl(primaryBase);

  try {
    return await fetch(`${primaryBase}${normalizedPath}`, init);
  } catch (primaryError) {
    if (secondaryBase === primaryBase) {
      throw primaryError;
    }
    return fetch(`${secondaryBase}${normalizedPath}`, init);
  }
};
