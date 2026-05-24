import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./MyLibraryPage.module.scss";
import { http } from "../../shared/api/http";
import MediaGrid from "../../widgets/MediaGrid/MediaGrid";

function safeDetail(err) {
  return err?.response?.data?.detail || "Ошибка загрузки";
}

export default function MyLibraryPage() {
  const [albums, setAlbums] = useState([]);
  const [playlists, setPlaylists] = useState([]);
  const [me, setMe] = useState({ username: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    let alive = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const [a, p, my] = await Promise.all([
          http.get("/music/me/albums"),
          http.get("/music/me/playlists"),
          http.get("/user/me"),
        ]);
        if (!alive) return;
        setMe({ username: my.data?.username || "" });
        const albumsRaw = a.data || [];
        const playlistsRaw = p.data || [];

        const [albumsWithCovers, playlistsWithCovers] = await Promise.all([
          Promise.all(
            albumsRaw.map(async (al) => {
              if (!al?.image_filename) return al;
              try {
                const resp = await http.get(`/music/albums/${al.id}/image-url`);
                return { ...al, image_url: resp.data?.url || null };
              } catch {
                return { ...al, image_url: null };
              }
            })
          ),
          Promise.all(
            playlistsRaw.map(async (pl) => {
              if (!pl?.image_filename) return pl;
              try {
                const resp = await http.get(`/music/playlists/${pl.id}/image-url`);
                return { ...pl, image_url: resp.data?.url || null };
              } catch {
                return { ...pl, image_url: null };
              }
            })
          ),
        ]);

        if (!alive) return;
        setAlbums(albumsWithCovers);
        setPlaylists(playlistsWithCovers);
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
          <MediaGrid
            title={
              <h2 className={styles.sectionTitle}>
                Альбомы <span>мои</span>
              </h2>
            }
            items={albums.map((a) => ({ ...a, author: me.username }))}
            emptyText={loading ? "Загрузка…" : "У вас пока нет альбомов."}
            getTitle={(a) => a?.title ?? ""}
            getAuthor={(a) => a?.author ?? ""}
            getCoverSrc={(a) => a?.image_url || "src/static/picture.png"}
            getReleaseDate={(a) => a?.created_at}
            onItemClick={(a) => navigate(`/music/albums/${a.id}`)}
          />
        </section>

        <section className={styles.section}>
          <MediaGrid
            title={
              <h2 className={styles.sectionTitle}>
                Плейлисты <span>мои</span>
              </h2>
            }
            items={playlists.map((p) => ({ ...p, author: me.username }))}
            emptyText={loading ? "Загрузка…" : "У вас пока нет плейлистов."}
            getTitle={(p) => p?.title ?? ""}
            getAuthor={(p) => p?.author ?? ""}
            getCoverSrc={(p) => p?.image_url || "src/static/picture.png"}
            onItemClick={(p) => navigate(`/music/playlists/${p.id}`)}
          />
        </section>
      </div>
    </div>
  );
}

