import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./MainPage.module.scss";
import { http } from "../../shared/api/http";
import { useAudioPlayer } from "../../shared/player/AudioPlayerContext";

import MediaGrid from "../../widgets/MediaGrid/MediaGrid";
import TrackRow from "../../widgets/TrackRow/TrackRow";

function safeDetail(err) {
  return err?.response?.data?.detail || "Ошибка загрузки";
}

const MainPage = () => {
  const [popularTracks, setPopularTracks] = useState([]);
  const [popularAlbums, setPopularAlbums] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const player = useAudioPlayer();
  const navigate = useNavigate();

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [t, a] = await Promise.all([
        http.get("/music/tracks/popular", { params: { limit: 20, offset: 0 } }),
        http.get("/music/albums/popular", { params: { limit: 15, offset: 0 } }),
      ]);
      const tracksRaw = t.data || [];
      const albumsRaw = a.data || [];

      const coverCache = new Map();
      const tracksWithCovers = await Promise.all(
        tracksRaw.map(async (tr) => {
          const albumId = tr?.created_album_id;
          if (!albumId) return { ...tr, cover_url: null };
          if (coverCache.has(albumId)) return { ...tr, cover_url: coverCache.get(albumId) };
          try {
            const resp = await http.get(`/music/albums/${albumId}/image-url`);
            const url = resp.data?.url || null;
            coverCache.set(albumId, url);
            return { ...tr, cover_url: url };
          } catch {
            coverCache.set(albumId, null);
            return { ...tr, cover_url: null };
          }
        })
      );

      const albumsWithCovers = await Promise.all(
        albumsRaw.map(async (al) => {
          if (!al?.image_filename) return al;
          try {
            const resp = await http.get(`/music/albums/${al.id}/image-url`);
            return { ...al, image_url: resp.data?.url || null };
          } catch {
            return { ...al, image_url: null };
          }
        })
      );

      setPopularTracks(tracksWithCovers);
      setPopularAlbums(albumsWithCovers);
    } catch (e) {
      setError(safeDetail(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className={styles.wrapper}>
      <div className={styles.main_container}>
        <h1 className={styles.pageTitle}>
          Главная <span>по прослушиваниям</span>
        </h1>

        {loading ? <div className={styles.info}>Загрузка…</div> : null}
        {error ? <div className={styles.error}>{String(error)}</div> : null}

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>
            Треки <span>по прослушиваниям</span>
          </h2>
          <div className={styles.tracks}>
            {!loading && popularTracks.length === 0 ? (
              <div className={styles.info}>Пока нет треков.</div>
            ) : null}
            {popularTracks.map((tr, idx) => (
              <TrackRow
                key={String(tr.id)}
                index={idx + 1}
                trackId={tr.id}
                title={tr.title}
                author={""}
                duration={tr.duration}
                coverSrc={tr.cover_url || "src/static/picture.png"}
                onClick={() =>
                  player.playQueue(
                    popularTracks.map((t) => ({
                      id: t.id,
                      title: t.title,
                      artist: "",
                    })),
                    idx
                  )
                }
              />
            ))}
          </div>
        </section>

        <section className={styles.section}>
          <MediaGrid
            title={
              <h2 className={styles.sectionTitle}>
                Альбомы <span>популярные</span>
              </h2>
            }
            items={popularAlbums.map((a) => ({ ...a, author: "" }))}
            emptyText={loading ? "Загрузка…" : "Альбомов нет."}
            getTitle={(a) => a?.title ?? ""}
            getAuthor={(a) => a?.author ?? ""}
            getCoverSrc={(a) => a?.image_url || "src/static/picture.png"}
            getReleaseDate={(a) => a?.created_at}
            onItemClick={(a) => navigate(`/music/albums/${a.id}`)}
          />
        </section>
      </div>
    </div>
  );
};

export default MainPage;
