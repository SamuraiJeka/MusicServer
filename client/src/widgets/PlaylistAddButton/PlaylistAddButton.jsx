import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import styles from "./PlaylistAddButton.module.scss";
import { http } from "../../shared/api/http";

const MENU_WIDTH = 260;
const MENU_MAX_HEIGHT = 280;
const VIEWPORT_PAD = 8;

function clampMenuPosition(rect) {
  let left = rect.right - MENU_WIDTH;
  if (left < VIEWPORT_PAD) left = VIEWPORT_PAD;
  if (left + MENU_WIDTH > window.innerWidth - VIEWPORT_PAD) {
    left = window.innerWidth - MENU_WIDTH - VIEWPORT_PAD;
  }

  let top = rect.bottom + 8;
  if (top + MENU_MAX_HEIGHT > window.innerHeight - VIEWPORT_PAD) {
    top = Math.max(VIEWPORT_PAD, rect.top - MENU_MAX_HEIGHT - 8);
  }

  return { top, left };
}

export default function PlaylistAddButton({ trackId, className = "" }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [menuLoading, setMenuLoading] = useState(false);
  const [menuError, setMenuError] = useState(null);
  const [playlists, setPlaylists] = useState([]);
  const [menuPos, setMenuPos] = useState({ top: 0, left: 0 });

  const anchorRef = useRef(null);
  const menuPortalRef = useRef(null);

  const updateMenuPosition = useCallback(() => {
    if (!anchorRef.current) return;
    const rect = anchorRef.current.getBoundingClientRect();
    setMenuPos(clampMenuPosition(rect));
  }, []);

  useEffect(() => {
    if (!menuOpen) return undefined;

    updateMenuPosition();

    const onDown = (e) => {
      if (anchorRef.current?.contains(e.target)) return;
      if (menuPortalRef.current?.contains(e.target)) return;
      setMenuOpen(false);
    };

    const onReposition = () => updateMenuPosition();

    document.addEventListener("mousedown", onDown);
    window.addEventListener("resize", onReposition);
    window.addEventListener("scroll", onReposition, true);

    return () => {
      document.removeEventListener("mousedown", onDown);
      window.removeEventListener("resize", onReposition);
      window.removeEventListener("scroll", onReposition, true);
    };
  }, [menuOpen, updateMenuPosition]);

  const toggleMenu = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    const next = !menuOpen;
    setMenuOpen(next);
    if (!next) return;

    updateMenuPosition();

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
      await http.post(`/music/playlists/${playlistId}/tracks`, null, {
        params: { track_id: trackId },
      });
      setMenuOpen(false);
    } catch (err) {
      setMenuError(err?.response?.data?.detail || "Не удалось добавить трек");
    }
  };

  const menu = menuOpen ? (
    <div
      ref={menuPortalRef}
      className={styles.menuPortal}
      style={{ top: menuPos.top, left: menuPos.left }}
      role="dialog"
      aria-label="Добавить в плейлист"
      onClick={(e) => e.stopPropagation()}
      onMouseDown={(e) => e.stopPropagation()}
    >
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
  ) : null;

  return (
    <>
      <div ref={anchorRef} className={`${styles.wrap} ${className}`.trim()}>
        <button
          type="button"
          className={`${styles.plusBtn} ${menuOpen ? styles.plusBtnActive : ""}`}
          onClick={toggleMenu}
          aria-label="Добавить в плейлист"
          aria-expanded={menuOpen}
        >
          +
        </button>
      </div>
      {menuOpen && typeof document !== "undefined"
        ? createPortal(menu, document.body)
        : null}
    </>
  );
}
