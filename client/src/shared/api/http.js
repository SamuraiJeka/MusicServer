import axios from "axios";
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from "../auth/tokenStorage";

const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const http = axios.create({
  baseURL,
});

let isRefreshing = false;
let refreshWaiters = [];

function notifyWaiters(token) {
  refreshWaiters.forEach((cb) => cb(token));
  refreshWaiters = [];
}

http.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

http.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    const status = error?.response?.status;

    if (status !== 401 || original?._retry) {
      throw error;
    }

    const refresh = getRefreshToken();
    if (!refresh) {
      clearTokens();
      throw error;
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        refreshWaiters.push((token) => {
          if (!token) return reject(error);
          original.headers = original.headers || {};
          original.headers.Authorization = `Bearer ${token}`;
          resolve(http(original));
        });
      });
    }

    original._retry = true;
    isRefreshing = true;
    try {
      const resp = await axios.post(
        `${baseURL}/auth/refresh`,
        { refresh_token: refresh },
        { headers: { "Content-Type": "application/json" } }
      );
      setTokens(resp.data);
      const newToken = resp.data.access_token;
      notifyWaiters(newToken);
      original.headers = original.headers || {};
      original.headers.Authorization = `Bearer ${newToken}`;
      return http(original);
    } catch (e) {
      notifyWaiters(null);
      clearTokens();
      throw e;
    } finally {
      isRefreshing = false;
    }
  }
);

