import { useEffect, useMemo, useRef, useState } from "react";
import styles from "./SearchBar.module.scss";
import { http } from "../api/http";

const LIMIT = 8;

function normalizeDetail(err) {
  const detail = err?.response?.data?.detail;
  if (!detail) return "Ошибка поиска";
  if (typeof detail === "string") return detail;
  try {
    return JSON.stringify(detail);
  } catch {
    return "Ошибка поиска";
  }
}

export default function SearchBar() {
  const [query, setQuery] = useState("");
  const [offset, setOffset] = useState(0);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);

  const trimmed = useMemo(() => query.trim(), [query]);
  const canPrev = offset > 0;
  const canNext = items.length === LIMIT;

  useEffect(() => {
    const onDoc = (e) => {
      if (!rootRef.current) return;
      if (!rootRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  useEffect(() => {
    if (!trimmed) {
      setItems([]);
      setError(null);
      setLoading(false);
      return;
    }
    const t = setTimeout(async () => {
      setLoading(true);
      setError(null);
      try {
        const resp = await http.get("/search/global", {
          params: { q: trimmed, limit: LIMIT, offset },
        });
        setItems(resp.data?.artists || []);
      } catch (e) {
        setItems([]);
        setError(normalizeDetail(e));
      } finally {
        setLoading(false);
      }
    }, 300);
    return () => clearTimeout(t);
  }, [trimmed, offset]);

  useEffect(() => {
    setOffset(0);
  }, [trimmed]);

  return (
    <div className={styles.root} ref={rootRef}>
      <input
        className={styles.input}
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        placeholder="Поиск..."
      />

      {open && trimmed ? (
        <div className={styles.dropdown}>
          {loading ? <div className={styles.rowMuted}>Поиск…</div> : null}
          {error ? <div className={styles.rowError}>{error}</div> : null}

          {!loading && !error && items.length === 0 ? (
            <div className={styles.rowMuted}>Ничего не найдено</div>
          ) : null}

          {!error
            ? items.map((u) => (
                <div className={styles.item} key={u.id}>
                  <div className={styles.itemTitle}>{u.username}</div>
                  <div className={styles.itemSub}>ID: {u.id}</div>
                </div>
              ))
            : null}

          <div className={styles.pager}>
            <button
              type="button"
              className={styles.arrow}
              disabled={!canPrev}
              onClick={() => setOffset((o) => Math.max(0, o - LIMIT))}
              title="Предыдущая страница"
            >
              ↑
            </button>
            <button
              type="button"
              className={styles.arrow}
              disabled={!canNext}
              onClick={() => setOffset((o) => o + LIMIT)}
              title="Следующая страница"
            >
              ↓
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}

