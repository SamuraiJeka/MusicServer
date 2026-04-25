import { useEffect, useMemo, useState } from "react";
import styles from "./SongList.module.scss";
import { http } from "../../shared/api/http";
import { useAudioPlayer } from "../../shared/player/AudioPlayerContext";

function formatTrackDuration(d) {
  if (d == null) return "";
  if (typeof d === "number" && Number.isFinite(d)) {
    const total = Math.round(d);
    const m = Math.floor(total / 60);
    const s = total % 60;
    return `${m}:${String(s).padStart(2, "0")}`;
  }
  if (typeof d === "string") {
    const m = d.match(/(\d+)M/);
    const s = d.match(/(\d+(?:\.\d+)?)S/);
    if (m || s) {
      const mm = m ? parseInt(m[1], 10) : 0;
      const ss = s ? Math.round(parseFloat(s[1])) : 0;
      return `${mm}:${String(ss).padStart(2, "0")}`;
    }
  }
  return "";
}

const SongList = () => {
  const [data, setData] = useState([]);
  const [loadError, setLoadError] = useState(null);
  const { playQueue } = useAudioPlayer();

  const queueItems = useMemo(
    () =>
      data.map((t) => ({
        id: t.id,
        title: t.title,
        artist: t.artist,
      })),
    [data]
  );

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const resp = await http.get("/music/tracks/popular", { params: { limit: 15, offset: 0 } });
        if (!alive) return;
        const rows = (resp.data || []).map((t) => ({
          id: t.id,
          img: "src/static/picture.png",
          title: t.title,
          artist: `Пользователь ${t.owner_id}`,
          timedelta: formatTrackDuration(t.duration),
        }));
        setData(rows);
        setLoadError(null);
      } catch (e) {
        if (!alive) return;
        setLoadError(e?.response?.data?.detail || "Не удалось загрузить треки");
        setData([]);
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  return (
    <div className={styles.wrapper}>
      <div className={styles.title_list}>
        <h1>
          Некий топ <span>песен</span>
        </h1>
      </div>
      {loadError ? <div className={styles.loadError}>{String(loadError)}</div> : null}
      <div className={styles.song_list}>
        {data.map((el, idx) => (
          <button
            type="button"
            className={styles.element}
            key={el.id}
            onClick={() => playQueue(queueItems, idx)}
          >
            <img src={el.img} alt="" />
            <div>
              <p>{el.title}</p>
              <span>{el.artist}</span>
            </div>
            <span className={styles.duration}>{el.timedelta}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default SongList;
