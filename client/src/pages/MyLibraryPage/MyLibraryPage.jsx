import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./MyLibraryPage.module.scss";
import { http } from "../../shared/api/http";

const MOCK_ALBUMS = [
  { id: 101, title: "Мой первый альбом" },
  { id: 102, title: "Избранное (сборник)" },
  { id: 103, title: "Дорога домой" },
];

const MOCK_PLAYLISTS = [
  { id: 201, title: "На повторе" },
  { id: 202, title: "Тренировка" },
  { id: 203, title: "Вечерний вайб" },
];

function safeDetail(err) {
  return err?.response?.data?.detail || "Ошибка загрузки";
}

export default function MyLibraryPage() {
  const [albums, setAlbums] = useState([]);
  const [playlists, setPlaylists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    let alive = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const [a, p] = await Promise.all([
          http.get("/music/me/albums"),
          http.get("/music/me/playlists"),
        ]);
        if (!alive) return;
        setAlbums(a.data || []);
        setPlaylists(p.data || []);
      } catch (e) {
        if (!alive) return;
        setError(safeDetail(e));
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  const albumItems = useMemo(() => {
    if (loading || error) return albums;
    return albums.length === 0 ? MOCK_ALBUMS : albums;
  }, [albums, loading, error]);

  const playlistItems = useMemo(() => {
    if (loading || error) return playlists;
    return playlists.length === 0 ? MOCK_PLAYLISTS : playlists;
  }, [playlists, loading, error]);

  return (
    <div className={styles.page}>
      <div className={styles.stickyHeader}>
        <div className={styles.headerInner}>
          <h1 className={styles.title}>
            Моя <span>медиатека</span>
          </h1>
          <button
            type="button"
            className={styles.primaryBtn}
            onClick={() => navigate("/create-playlist")}
          >
            Создать плейлист
          </button>
        </div>
      </div>

      <div className={styles.content}>
        {loading ? <div className={styles.info}>Загрузка…</div> : null}
        {error ? <div className={styles.error}>{String(error)}</div> : null}

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>
            Альбомы <span>мои</span>
          </h2>
          {albumItems.length === 0 && !loading ? (
            <div className={styles.info}>Пока нет альбомов.</div>
          ) : (
            <div className={styles.grid}>
              {albumItems.map((a) => (
                <div className={styles.card} key={`album-${a.id}`}>
                  <div className={styles.cardTitle}>{a.title}</div>
                  <div className={styles.cardSub}>ID: {a.id}</div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>
            Плейлисты <span>мои</span>
          </h2>
          {playlistItems.length === 0 && !loading ? (
            <div className={styles.info}>Пока нет плейлистов.</div>
          ) : (
            <div className={styles.grid}>
              {playlistItems.map((p) => (
                <div className={styles.card} key={`playlist-${p.id}`}>
                  <div className={styles.cardTitle}>{p.title}</div>
                  <div className={styles.cardSub}>ID: {p.id}</div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

