import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import styles from "./ChatsPage.module.scss";
import { http } from "../../shared/api/http";
import { messengerWsUrl } from "../../shared/api/chatWs";
import ChatAudioMessage from "./ChatAudioMessage";

function safeDetail(err) {
  const detail = err?.response?.data?.detail;
  if (!detail) return "Ошибка";
  return typeof detail === "string" ? detail : "Ошибка";
}

function messageLabel(msg) {
  if (msg.type === "audio") return "Аудио";
  return (msg.text || "").trim();
}

export default function ChatsPage() {
  const [meId, setMeId] = useState(null);
  const [sidebarQuery, setSidebarQuery] = useState("");
  const [sidebarItems, setSidebarItems] = useState([]);
  const [sidebarLoading, setSidebarLoading] = useState(false);
  const [sidebarError, setSidebarError] = useState(null);

  const [selected, setSelected] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const [messagesError, setMessagesError] = useState(null);

  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [wsStatus, setWsStatus] = useState("idle");

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const messageInputRef = useRef(null);
  const sidebarQueryRef = useRef(sidebarQuery);
  const selectedRef = useRef(null);
  const wsRef = useRef(null);
  const reconnectTimerRef = useRef(null);
  const didAutoSelectRef = useRef(false);

  const trimmedSidebar = sidebarQuery.trim();

  useEffect(() => {
    sidebarQueryRef.current = sidebarQuery;
  }, [sidebarQuery]);

  useEffect(() => {
    selectedRef.current = selected;
  }, [selected]);

  const appendMessage = useCallback((msg) => {
    if (!msg?.id) return;
    if (Number(selectedRef.current?.chatId) !== Number(msg.chat_id)) return;
    const id = Number(msg.id);
    setMessages((prev) => {
      if (prev.some((m) => Number(m.id) === id)) return prev;
      return [...prev, msg];
    });
  }, []);

  const loadSidebar = useCallback(async (q) => {
    setSidebarLoading(true);
    setSidebarError(null);
    try {
      const resp = await http.get("/search/messenger/users", {
        params: { q, limit: 50 },
      });
      setSidebarItems(resp.data || []);
    } catch (err) {
      setSidebarError(safeDetail(err));
      setSidebarItems([]);
    } finally {
      setSidebarLoading(false);
    }
  }, []);

  const sendText = useCallback(
    async (text) => {
      if (!selected?.chatId) return;
      const chatId = selected.chatId;
      const resp = await http.post(`/messages/${chatId}/text`, { text });
      appendMessage(resp.data);
      loadSidebar(sidebarQueryRef.current.trim());
    },
    [selected?.chatId, appendMessage, loadSidebar]
  );

  const sendAudio = useCallback(
    async (audioKey) => {
      if (!selected?.chatId) return;
      const chatId = selected.chatId;
      const resp = await http.post(`/messages/${chatId}/audio`, { audio_key: audioKey });
      appendMessage(resp.data);
      loadSidebar(sidebarQueryRef.current.trim());
    },
    [selected?.chatId, appendMessage, loadSidebar]
  );

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const me = await http.get("/user/me");
        if (!alive) return;
        setMeId(me.data?.id ?? null);
      } catch {
        if (!alive) return;
        setMeId(null);
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  useEffect(() => {
    const t = setTimeout(() => loadSidebar(trimmedSidebar), trimmedSidebar ? 280 : 0);
    return () => clearTimeout(t);
  }, [trimmedSidebar, loadSidebar]);

  const openChat = useCallback(
    async (item) => {
      setMessagesError(null);
      let chatId = item.chat_id ?? item.chatId ?? null;
      if (!chatId) {
        try {
          const resp = await http.post(`/chats/${item.id}`);
          chatId = resp.data?.id ?? null;
          await loadSidebar(trimmedSidebar);
        } catch (err) {
          setMessagesError(safeDetail(err));
          return;
        }
      }
      if (!chatId) {
        setMessagesError("Не удалось открыть чат");
        return;
      }
      setSelected({
        userId: item.id,
        username: item.username,
        chatId: Number(chatId),
      });
      requestAnimationFrame(() => messageInputRef.current?.focus());
    },
    [loadSidebar, trimmedSidebar]
  );

  useEffect(() => {
    if (didAutoSelectRef.current || selected || sidebarLoading || sidebarItems.length === 0) {
      return;
    }
    didAutoSelectRef.current = true;
    openChat(sidebarItems[0]);
  }, [selected, sidebarLoading, sidebarItems, openChat]);

  useEffect(() => {
    if (!selected?.chatId) {
      setMessages([]);
      return;
    }

    let alive = true;
    (async () => {
      setMessagesLoading(true);
      setMessagesError(null);
      try {
        const resp = await http.get(`/messages/${selected.chatId}`, {
          params: { limit: 100, offset: 0 },
        });
        if (!alive) return;
        const items = resp.data?.items || [];
        setMessages([...items].reverse());
      } catch (err) {
        if (!alive) return;
        setMessagesError(safeDetail(err));
        setMessages([]);
      } finally {
        if (alive) setMessagesLoading(false);
      }
    })();

    return () => {
      alive = false;
    };
  }, [selected?.chatId]);

  // Одно WS на пользователя: push всех новых сообщений из чатов, где он участник
  useEffect(() => {
    let cancelled = false;

    const connect = () => {
      if (cancelled) return;
      const ws = new WebSocket(messengerWsUrl());
      wsRef.current = ws;
      setWsStatus("connecting");

      ws.onopen = () => {
        if (!cancelled) setWsStatus("open");
      };
      ws.onerror = () => {
        if (!cancelled) setWsStatus("error");
      };
      ws.onclose = () => {
        if (cancelled) return;
        setWsStatus("closed");
        reconnectTimerRef.current = setTimeout(connect, 3000);
      };
      ws.onmessage = (ev) => {
        try {
          const data = JSON.parse(ev.data);
          if (data.event !== "message" || !data.message) return;
          const msg = data.message;
          const chatId = Number(msg.chat_id);
          if (Number(selectedRef.current?.chatId) === chatId) {
            appendMessage(msg);
          }
          setSidebarItems((prev) => {
            const preview =
              msg.type === "audio" ? "Аудио" : (msg.text || "").trim() || "Сообщение";
            const idx = prev.findIndex(
              (u) => Number(u.chat_id) === chatId || Number(u.chatId) === chatId
            );
            if (idx === -1) {
              loadSidebar(sidebarQueryRef.current.trim());
              return prev;
            }
            const next = [...prev];
            const item = { ...next[idx], last_message: preview, has_chat: true };
            next.splice(idx, 1);
            next.unshift(item);
            return next;
          });
        } catch {
          /* ignore */
        }
      };
    };

    connect();

    return () => {
      cancelled = true;
      clearTimeout(reconnectTimerRef.current);
      wsRef.current?.close();
      wsRef.current = null;
      setWsStatus("idle");
    };
  }, [appendMessage, loadSidebar]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const hasActiveChat = !!selected?.chatId;
  const canSend = hasActiveChat && !sending && !uploading;

  const onSend = async (e) => {
    e.preventDefault();
    const text = draft.trim();
    if (!text) return;
    if (!hasActiveChat) {
      setMessagesError("Сначала выберите пользователя справа");
      return;
    }
    if (!canSend) return;

    setSending(true);
    setMessagesError(null);
    try {
      await sendText(text);
      setDraft("");
    } catch (err) {
      setMessagesError(safeDetail(err));
    } finally {
      setSending(false);
    }
  };

  const onPickFile = () => fileInputRef.current?.click();

  const onFileChange = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    if (!hasActiveChat) {
      setMessagesError("Сначала выберите пользователя справа");
      return;
    }
    if (!canSend) return;

    setUploading(true);
    setMessagesError(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const upload = await http.post("/upload/audio", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      const audioKey = upload.data?.audio_key;
      if (!audioKey) throw new Error("Не удалось загрузить файл");
      await sendAudio(audioKey);
    } catch (err) {
      setMessagesError(safeDetail(err));
    } finally {
      setUploading(false);
    }
  };

  const activeKey = selected ? `${selected.userId}` : null;

  const emptyMain = !selected;

  const wsHint = useMemo(() => {
    if (!selected) return null;
    if (wsStatus === "connecting") return "Подключение…";
    if (wsStatus === "closed" || wsStatus === "error") return "Соединение потеряно";
    return null;
  }, [selected, wsStatus]);

  return (
    <div className={styles.wrapper}>
      <div className={styles.left}>
        <div className={styles.chatHeader}>
          <h1 className={styles.chatTitle}>
            {selected?.username || "Выберите чат"}
          </h1>
          {wsHint ? <div className={styles.wsHint}>{wsHint}</div> : null}
        </div>

        <div className={styles.messages}>
          {emptyMain ? (
            <div className={styles.placeholder}>Выберите пользователя справа</div>
          ) : null}
          {messagesLoading ? (
            <div className={styles.placeholder}>Загрузка…</div>
          ) : null}
          {messagesError ? (
            <div className={styles.error}>{messagesError}</div>
          ) : null}
          {!emptyMain &&
            messages.map((m) => {
              const mine = meId != null && m.user_id === meId;
              return (
                <div
                  key={m.id}
                  className={`${styles.messageRow} ${mine ? styles.mine : styles.theirs}`}
                >
                  <div
                    className={`${styles.bubble} ${
                      m.type === "audio" ? styles.bubbleAudio : ""
                    }`}
                  >
                    {m.type === "audio" ? (
                      <ChatAudioMessage
                        messageId={m.id}
                        src={m.audio_url}
                        mine={mine}
                        peerName={selected?.username}
                      />
                    ) : (
                      messageLabel(m)
                    )}
                  </div>
                </div>
              );
            })}
          <div ref={messagesEndRef} />
        </div>

        <form className={styles.composer} onSubmit={onSend}>
          <input
            ref={messageInputRef}
            id="chat-message"
            name="message"
            type="text"
            autoComplete="off"
            className={`${styles.input} ${!hasActiveChat ? styles.inputReadonly : ""}`}
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder={
              hasActiveChat ? "Сообщение…" : "Выберите чат справа, чтобы написать…"
            }
            aria-label="Текст сообщения"
          />
          <input
            ref={fileInputRef}
            id="chat-audio-file"
            name="audio"
            type="file"
            accept=".mp3,audio/mpeg"
            className={styles.hiddenFile}
            onChange={onFileChange}
          />
          <button
            type="button"
            className={styles.attachBtn}
            title="Прикрепить MP3"
            onClick={onPickFile}
            disabled={!hasActiveChat || sending || uploading}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path
                d="M21 12.5l-9.2 9.2a6 6 0 01-8.5-8.5l9.9-9.9a4.5 4.5 0 016.4 6.4l-10 10a3 3 0 01-4.2-4.2l9.4-9.4"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
          <button
            type="submit"
            className={styles.sendBtn}
            disabled={!draft.trim() || !canSend}
          >
            {uploading ? "…" : "Отправить"}
          </button>
        </form>
      </div>

      <div className={styles.right}>
        <div className={styles.chatSearch}>
          <input
            id="chat-user-search"
            name="chat-user-search"
            type="search"
            autoComplete="off"
            className={styles.chatSearchInput}
            value={sidebarQuery}
            onChange={(e) => setSidebarQuery(e.target.value)}
            placeholder="Поиск пользователей…"
            aria-label="Поиск пользователей"
          />
        </div>
        <div className={styles.chatList}>
          {sidebarLoading ? (
            <div className={styles.listHint}>Поиск…</div>
          ) : null}
          {sidebarError ? (
            <div className={styles.listError}>{sidebarError}</div>
          ) : null}
          {!sidebarLoading && !sidebarError && sidebarItems.length === 0 ? (
            <div className={styles.listHint}>
              {trimmedSidebar ? "Никого не найдено" : "Нет переписок"}
            </div>
          ) : null}
          {sidebarItems.map((u) => (
            <button
              key={u.id}
              type="button"
              className={`${styles.chatItem} ${
                activeKey === `${u.id}` ? styles.chatItemActive : ""
              }`}
              onClick={() => openChat(u)}
            >
              <div className={styles.chatItemTitle}>{u.username}</div>
              <div className={styles.chatItemSub}>
                {u.last_message || (u.has_chat ? "Нет сообщений" : "Новый чат")}
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
