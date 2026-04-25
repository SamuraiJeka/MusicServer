import { useMemo, useState } from "react";
import styles from "./ChatsPage.module.scss";

const MOCK_CHATS = [
  { id: 1, title: "Оксимирон", last: "Привет" },
  { id: 2, title: "Noize MC", last: "Ок" },
  { id: 3, title: "ATL", last: "Скинь трек" },
  { id: 4, title: "MiyaGi", last: "Позже" },
];

const MOCK_MESSAGES = [
  { id: 11, mine: false, text: "Привет! Как дела?" },
  { id: 12, mine: true, text: "Нормально. Ты как?" },
  { id: 13, mine: false, text: "Есть новый трек?" },
  { id: 14, mine: true, text: "Да, сейчас пришлю." },
];

export default function ChatsPage() {
  const [chatQuery, setChatQuery] = useState("");
  const [selectedChatId, setSelectedChatId] = useState(MOCK_CHATS[0]?.id ?? null);
  const [message, setMessage] = useState("");

  const chats = useMemo(() => {
    const q = chatQuery.trim().toLowerCase();
    if (!q) return MOCK_CHATS;
    return MOCK_CHATS.filter((c) => c.title.toLowerCase().includes(q));
  }, [chatQuery]);

  const selectedChat = useMemo(
    () => MOCK_CHATS.find((c) => c.id === selectedChatId) || null,
    [selectedChatId]
  );

  const onSend = (e) => {
    e.preventDefault();
    setMessage("");
  };

  return (
    <div className={styles.wrapper}>
      <div className={styles.left}>
        <div className={styles.chatHeader}>
          <h1 className={styles.chatTitle}>{selectedChat?.title || "Чат"}</h1>
        </div>

        <div className={styles.messages}>
          {MOCK_MESSAGES.map((m) => (
            <div
              key={m.id}
              className={`${styles.messageRow} ${m.mine ? styles.mine : styles.theirs}`}
            >
              <div className={styles.bubble}>{m.text}</div>
            </div>
          ))}
        </div>

        <form className={styles.composer} onSubmit={onSend}>
          <input
            className={styles.input}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Сообщение…"
          />
          <button type="button" className={styles.attachBtn} title="Прикрепить аудио">
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
          <button type="submit" className={styles.sendBtn} disabled={!message.trim()}>
            Отправить
          </button>
        </form>
      </div>

      <div className={styles.right}>
        <div className={styles.chatSearch}>
          <input
            className={styles.chatSearchInput}
            value={chatQuery}
            onChange={(e) => setChatQuery(e.target.value)}
            placeholder="Поиск чатов…"
          />
        </div>
        <div className={styles.chatList}>
          {chats.map((c) => (
            <button
              key={c.id}
              type="button"
              className={`${styles.chatItem} ${c.id === selectedChatId ? styles.chatItemActive : ""}`}
              onClick={() => setSelectedChatId(c.id)}
            >
              <div className={styles.chatItemTitle}>{c.title}</div>
              <div className={styles.chatItemSub}>{c.last}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

