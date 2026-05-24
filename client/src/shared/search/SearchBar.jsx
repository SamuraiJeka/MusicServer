import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./SearchBar.module.scss";
import { http } from "../api/http";
import { useAudioPlayer } from "../player/AudioPlayerContext";
import PlaylistAddButton from "../../widgets/PlaylistAddButton/PlaylistAddButton";

const LIMIT = 8;
const FALLBACK_COVER = "src/static/picture.png";

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
  const [artists, setArtists] = useState([]);
  const [tracks, setTracks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);
  const navigate = useNavigate();
  const player = useAudioPlayer();

  const trimmed = useMemo(() => query.trim(), [query]);
  const hasResults = artists.length > 0 || tracks.length > 0;
  const canPrev = offset > 0;
  const canNext = artists.length === LIMIT || tracks.length === LIMIT;

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
      setArtists([]);
      setTracks([]);
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
        setArtists(resp.data?.artists || []);
        setTracks(resp.data?.tracks || []);
      } catch (e) {
        setArtists([]);
        setTracks([]);
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

  const openArtist = (userId) => {
    setOpen(false);
    setQuery("");
    navigate(`/artist/${userId}`);
  };

  const playTrack = (tr) => {
    setOpen(false);
    setQuery("");
    player.playTrack({
      id: tr.id,
      title: tr.title,
      artist: tr.artist_name,
    });
  };

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

          {!loading && !error && !hasResults ? (
            <div className={styles.rowMuted}>Ничего не найдено</div>
          ) : null}

          {!error
            ? artists.map((u) => (
                <button
                  type="button"
                  className={styles.item}
                  key={`artist-${u.id}`}
                  onClick={() => openArtist(u.id)}
                >
                  <img
                    className={styles.itemAvatar}
                    src={u.avatar_url || FALLBACK_COVER}
                    alt=""
                  />
                  <div className={styles.itemMain}>
                    <div className={styles.itemTitle}>{u.username}</div>
                    <div className={styles.itemSub}>Артист</div>
                  </div>
                </button>
              ))
            : null}

          {!error
            ? tracks.map((tr) => (
                <div className={styles.trackItem} key={`track-${tr.id}`}>
                  <button
                    type="button"
                    className={styles.trackPlay}
                    onClick={() => playTrack(tr)}
                  >
                    <img
                      className={styles.itemCover}
                      src={tr.cover_url || FALLBACK_COVER}
                      alt=""
                    />
                    <div className={styles.itemMain}>
                      <div className={styles.trackTitleRow}>
                        <span className={styles.itemTitle}>{tr.title}</span>
                        <span className={styles.trackArtist}>{tr.artist_name}</span>
                      </div>
                      <div className={styles.itemSub}>Трек</div>
                    </div>
                  </button>
                  <PlaylistAddButton trackId={tr.id} />
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
