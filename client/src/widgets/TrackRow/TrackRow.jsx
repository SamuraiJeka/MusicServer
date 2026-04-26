import styles from "./TrackRow.module.scss";
import { useEffect, useMemo, useRef, useState } from "react";
import { http } from "../../shared/api/http";

function formatDuration(value) {
  if (!value) return "";
  // Backend sends Postgres interval; it may serialize as "HH:MM:SS" or similar.
  if (typeof value === "string") {
    const parts = value.split(":").map((p) => Number(p));
    if (parts.length >= 2 && parts.every((n) => Number.isFinite(n))) {
      const h = parts.length === 3 ? parts[0] : 0;
      const m = parts.length === 3 ? parts[1] : parts[0];
      const s = parts.length === 3 ? parts[2] : parts[1];
      const mm = String(m + h * 60).padStart(2, "0");
      const ss = String(Math.floor(s)).padStart(2, "0");
      return `${mm}:${ss}`;
    }
    return value;
  }
  return String(value);
}

const FALLBACK_COVER = "src/static/picture.png";

export default function TrackRow({
  index,
  title,
  author,
  duration,
  coverSrc,
  trackId,
  onClick,
  rightSlot,
}) {
  const durationText = useMemo(() => formatDuration(duration), [duration]);

  const [menuOpen, setMenuOpen] = useState(false);
  const [menuLoading, setMenuLoading] = useState(false);
  const [menuError, setMenuError] = useState(null);
  const [playlists, setPlaylists] = useState([]);
  const menuRef = useRef(null);

  useEffect(() => {
    if (!menuOpen) return;
    const onDown = (e) => {
      if (!menuRef.current) return;
      if (menuRef.current.contains(e.target)) return;
      setMenuOpen(false);
    };
    document.addEventListener("mousedown", onDown);
    return () => document.removeEventListener("mousedown", onDown);
  }, [menuOpen]);

  const toggleMenu = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    const next = !menuOpen;
    setMenuOpen(next);
    if (!next) return;
    if (playlists.length > 0) return;
    setMenuLoading(true);
    setMenuError(null);
    try {
      const resp = await http.get("/music/me/playlists");
      setPlaylists(resp.data || []);
    } catch (err) {
      setMenuError(err?.response?.data?.detail || "Не удалось загрузить плейлисты");
    } finally {
      setMenuLoading(false);
    }
  };

  const addToPlaylist = async (e, playlistId) => {
    e.preventDefault();
    e.stopPropagation();
    if (!trackId) return;
    try {
      await http.post(`/music/playlists/${playlistId}/tracks`, null, { params: { track_id: trackId } });
      setMenuOpen(false);
    } catch (err) {
      setMenuError(err?.response?.data?.detail || "Не удалось добавить трек");
    }
  };

  return (
    <button type="button" className={styles.row} onClick={onClick}>
      <div className={styles.left}>
        <div className={styles.index}>{index}</div>
        <div className={styles.cover}>
          <img src={coverSrc || FALLBACK_COVER} alt="" />
        </div>
        <div className={styles.meta}>
          <div className={styles.title} title={title}>
            {title}
          </div>
          <div className={styles.author} title={author}>
            {author}
          </div>
        </div>
      </div>

      <div className={styles.right}>
        {rightSlot ? <div className={styles.slot}>{rightSlot}</div> : null}
        <div className={styles.durationRight}>{durationText}</div>
        <div className={styles.plusWrap} ref={menuRef}>
          <button type="button" className={styles.plusBtn} onClick={toggleMenu} aria-label="Добавить в плейлист">
            +
          </button>
          {menuOpen ? (
            <div className={styles.menu}>
              <div className={styles.menuTitle}>Добавить в плейлист</div>
              {menuLoading ? <div className={styles.menuInfo}>Загрузка…</div> : null}
              {menuError ? <div className={styles.menuError}>{String(menuError)}</div> : null}
              {!menuLoading && !menuError && playlists.length === 0 ? (
                <div className={styles.menuInfo}>Плейлистов нет.</div>
              ) : null}
              <div className={styles.menuList}>
                {playlists.map((p) => (
                  <button
                    key={String(p.id)}
                    type="button"
                    className={styles.menuItem}
                    onClick={(ev) => addToPlaylist(ev, p.id)}
                    disabled={!trackId}
                    title={p.title}
                  >
                    {p.title}
                  </button>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </button>
  );
}

