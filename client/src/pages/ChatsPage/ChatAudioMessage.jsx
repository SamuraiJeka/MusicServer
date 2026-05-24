import { useEffect, useMemo, useRef, useState } from "react";
import styles from "./ChatAudioMessage.module.scss";
import { useAudioPlayer } from "../../shared/player/AudioPlayerContext";

const BAR_COUNT = 38;

function formatTime(sec) {
  if (!Number.isFinite(sec) || sec < 0) return "0:00";
  const s = Math.floor(sec);
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${m}:${String(r).padStart(2, "0")}`;
}

function waveformBars(seedId) {
  const bars = [];
  let seed = Number(seedId) || 1;
  for (let i = 0; i < BAR_COUNT; i += 1) {
    seed = (seed * 9301 + 49297) % 233280;
    bars.push(0.22 + (seed / 233280) * 0.78);
  }
  return bars;
}

export default function ChatAudioMessage({
  messageId,
  src,
  mine = false,
  peerName = "",
}) {
  const waveRef = useRef(null);
  const [metaDuration, setMetaDuration] = useState(0);

  const {
    currentTrack,
    isPlaying,
    loadingUrl,
    currentTime,
    duration,
    playChatAudio,
    togglePlayPause,
    seek,
  } = useAudioPlayer();

  const trackId = `chat:${messageId}`;
  const isActive = currentTrack?.id === trackId;
  const playing = isActive && isPlaying;
  const loading = isActive && loadingUrl;

  const bars = useMemo(() => waveformBars(messageId), [messageId]);
  const activeDuration = isActive ? duration : metaDuration;
  const activeCurrent = isActive ? currentTime : 0;
  const progress =
    activeDuration > 0 ? Math.min(1, activeCurrent / activeDuration) : 0;
  const playedBars = Math.floor(progress * BAR_COUNT);

  useEffect(() => {
    if (!src || isActive) return undefined;
    const audio = new Audio();
    audio.preload = "metadata";
    audio.src = src;
    const onMeta = () => {
      if (Number.isFinite(audio.duration)) setMetaDuration(audio.duration);
    };
    audio.addEventListener("loadedmetadata", onMeta);
    if (audio.readyState >= 1) onMeta();
    return () => {
      audio.removeEventListener("loadedmetadata", onMeta);
      audio.src = "";
    };
  }, [src, isActive]);

  const togglePlay = () => {
    if (!src) return;
    if (isActive) {
      togglePlayPause();
      return;
    }
    playChatAudio({
      messageId,
      audioUrl: src,
      title: "Голосовое сообщение",
      artist: mine ? "Вы" : peerName || "Чат",
    });
  };

  const seekToRatio = (ratio) => {
    if (!isActive || !activeDuration) return;
    const clamped = Math.max(0, Math.min(1, ratio));
    seek(clamped * activeDuration);
  };

  const onWaveClick = (e) => {
    const rect = waveRef.current?.getBoundingClientRect();
    if (!rect?.width) return;
    const ratio = (e.clientX - rect.left) / rect.width;
    if (!isActive) {
      playChatAudio({
        messageId,
        audioUrl: src,
        title: "Голосовое сообщение",
        artist: mine ? "Вы" : peerName || "Чат",
      });
      return;
    }
    seekToRatio(ratio);
  };

  const onWaveKeyDown = (e) => {
    if (e.key !== "Enter" && e.key !== " ") return;
    e.preventDefault();
    togglePlay();
  };

  const timeLabel = playing
    ? formatTime(activeCurrent)
    : formatTime(activeDuration || 0);

  if (!src) {
    return <span className={styles.unavailable}>Аудио недоступно</span>;
  }

  return (
    <div
      className={`${styles.root} ${mine ? styles.mine : styles.theirs} ${
        isActive ? styles.active : ""
      }`}
      data-playing={playing || undefined}
    >
      <button
        type="button"
        className={styles.playBtn}
        onClick={togglePlay}
        disabled={loading}
        aria-label={playing ? "Пауза" : "Воспроизвести в плеере"}
      >
        {loading ? (
          <span className={styles.spinner} aria-hidden />
        ) : playing ? (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
            <rect x="6" y="5" width="4" height="14" rx="1" />
            <rect x="14" y="5" width="4" height="14" rx="1" />
          </svg>
        ) : (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
            <path d="M8 5.14v14.72a1 1 0 001.5.86l11.14-7.36a1 1 0 000-1.72L9.5 4.28A1 1 0 008 5.14z" />
          </svg>
        )}
      </button>

      <div
        ref={waveRef}
        className={styles.wave}
        onClick={onWaveClick}
        onKeyDown={onWaveKeyDown}
        role="slider"
        tabIndex={0}
        aria-label="Позиция воспроизведения"
        aria-valuemin={0}
        aria-valuemax={activeDuration || 0}
        aria-valuenow={activeCurrent}
      >
        {bars.map((h, i) => (
          <span
            key={i}
            className={`${styles.bar} ${i < playedBars ? styles.barPlayed : ""}`}
            style={{ "--h": h }}
          />
        ))}
      </div>

      <span className={styles.time}>{timeLabel}</span>
    </div>
  );
}
