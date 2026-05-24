import styles from "./TrackRow.module.scss";
import { useMemo } from "react";
import PlaylistAddButton from "../PlaylistAddButton/PlaylistAddButton";

function formatDuration(value) {
  if (!value) return "";
  if (typeof value === "string") {
    if (value.startsWith("PT")) {
      const m = value.match(/^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?$/);
      if (m) {
        const h = Number(m[1] || 0);
        const mm = Number(m[2] || 0);
        const ss = Number(m[3] || 0);
        const totalMin = h * 60 + mm;
        return `${String(totalMin).padStart(2, "0")}:${String(Math.floor(ss)).padStart(2, "0")}`;
      }
    }

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

  return (
    <div className={styles.row}>
      <button type="button" className={styles.rowMain} onClick={onClick}>
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
      </button>

      <div className={styles.right}>
        {rightSlot ? <div className={styles.slot}>{rightSlot}</div> : null}
        <div className={styles.durationRight}>{durationText}</div>
        <PlaylistAddButton trackId={trackId} />
      </div>
    </div>
  );
}

