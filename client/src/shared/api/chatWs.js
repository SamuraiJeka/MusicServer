import { getAccessToken } from "../auth/tokenStorage";

const apiBase = import.meta.env.VITE_API_URL || "http://localhost:8000";

/** Одно WS-подключение на пользователя (все чаты). */
export function messengerWsUrl() {
  const token = getAccessToken();
  const wsBase = apiBase.replace(/^http/i, "ws");
  const q = token ? `?token=${encodeURIComponent(token)}` : "";
  return `${wsBase}/ws/messenger${q}`;
}
