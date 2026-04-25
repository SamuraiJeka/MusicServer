import styles from "./PlayerBar.module.scss";
import { useAudioPlayer } from "./AudioPlayerContext";

function formatTime(sec) {
  if (!Number.isFinite(sec) || sec < 0) return "0:00";
  const s = Math.floor(sec);
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${m}:${String(r).padStart(2, "0")}`;
}

export default function PlayerBar() {
  const {
    queue,
    index,
    currentTrack,
    isPlaying,
    loadingUrl,
    error,
    currentTime,
    duration,
    togglePlayPause,
    next,
    prev,
    seek,
  } = useAudioPlayer();

  const hasQueue = queue.length > 0;
  const canPrev = hasQueue && index > 0;
  const canNext = hasQueue && index < queue.length - 1;

  const onSeek = (e) => {
    const v = Number(e.target.value);
    seek(v);
  };

  return (
    <div className={styles.bar} role="region" aria-label="Плеер">
      <div className={styles.inner}>
        <div className={styles.meta}>
          <div className={styles.title}>
            {currentTrack ? currentTrack.title : "Нет трека"}
          </div>
          <div className={styles.sub}>
            {currentTrack?.artist ? currentTrack.artist : ""}
            {error ? <span className={styles.err}> · {String(error)}</span> : null}
            {loadingUrl ? <span className={styles.muted}> · загрузка…</span> : null}
          </div>
        </div>

        <div className={styles.controls}>
          <button
            type="button"
            className={styles.btn}
            onClick={prev}
            disabled={!hasQueue || !canPrev}
            title="Предыдущий"
          >
            ⏮
          </button>
          <button
            type="button"
            className={styles.play}
            onClick={togglePlayPause}
            disabled={!hasQueue || loadingUrl}
            title={isPlaying ? "Пауза" : "Играть"}
          >
            {isPlaying ? "⏸" : "▶"}
          </button>
          <button
            type="button"
            className={styles.btn}
            onClick={next}
            disabled={!hasQueue || !canNext}
            title="Следующий"
          >
            ⏭
          </button>
        </div>

        <div className={styles.timeline}>
          <span className={styles.tt}>{formatTime(currentTime)}</span>
          <input
            className={styles.range}
            type="range"
            min={0}
            max={Math.max(duration || 0, 0.001)}
            step={0.25}
            value={Math.min(currentTime, duration || 0)}
            onChange={onSeek}
            disabled={!hasQueue || !duration}
          />
          <span className={styles.tt}>{formatTime(duration)}</span>
        </div>
      </div>
    </div>
  );
}
