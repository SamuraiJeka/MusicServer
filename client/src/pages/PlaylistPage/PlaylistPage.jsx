import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import styles from "./PlaylistPage.module.scss";
import { http } from "../../shared/api/http";
import TrackRow from "../../widgets/TrackRow/TrackRow";
import { useAudioPlayer } from "../../shared/player/AudioPlayerContext";

function safeDetail(err) {
  return err?.response?.data?.detail || "Ошибка загрузки";
}

function formatDate(value) {
  if (!value) return "";
  try {
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return "";
    return d.toLocaleDateString("ru-RU", { year: "numeric", month: "2-digit", day: "2-digit" });
  } catch {
    return "";
  }
}

export default function PlaylistPage() {
  const { playlistId } = useParams();
  const idNum = useMemo(() => Number(playlistId), [playlistId]);
  const player = useAudioPlayer();

  const [me, setMe] = useState({ username: "" });
  const [playlist, setPlaylist] = useState(null);
  const [coverUrl, setCoverUrl] = useState(null);
  const [tracks, setTracks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    if (!Number.isFinite(idNum) || idNum <= 0) {
      setError("Некорректный id плейлиста");
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const [p, my] = await Promise.all([http.get(`/music/playlists/${idNum}`), http.get("/user/me")]);
      setPlaylist(p.data);
      setTracks(p.data?.tracks || []);
      setMe({ username: my.data?.username || "" });

      if (p.data?.image_filename) {
        try {
          const resp = await http.get(`/music/playlists/${idNum}/image-url`);
          setCoverUrl(resp.data?.url || null);
        } catch {
          setCoverUrl(null);
        }
      } else {
        setCoverUrl(null);
      }
    } catch (e) {
      setError(safeDetail(e));
    } finally {
      setLoading(false);
    }
  }, [idNum]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className={styles.page}>
      <div className={styles.content}>
        {loading ? <div className={styles.loading}>Загрузка…</div> : null}
        {error ? <div className={styles.error}>{String(error)}</div> : null}

        {playlist ? (
          <>
            <div className={styles.header}>
              <div className={styles.cover}>
                <img src={coverUrl || "src/static/picture.png"} alt="" />
              </div>
              <div className={styles.info}>
                <h1 className={styles.title}>{playlist.title}</h1>
                <div className={styles.author}>{me.username || "Автор"}</div>
                <div className={styles.date}>{formatDate(playlist.created_at)}</div>
              </div>
            </div>

            <div className={styles.tracks}>
              {tracks.map((tr, idx) => (
                <TrackRow
                  key={String(tr.id)}
                  index={idx + 1}
                  trackId={tr.id}
                  title={tr.title}
                  author={me.username || ""}
                  duration={tr.duration}
                  coverSrc={coverUrl}
                  onClick={() => player.playQueue(tracks, idx)}
                />
              ))}
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}

