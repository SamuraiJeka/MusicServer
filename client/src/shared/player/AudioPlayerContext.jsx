import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { http } from "../api/http";
import PlayerBar from "./PlayerBar";
import { useAuth } from "../auth/AuthContext";

const AudioPlayerContext = createContext(null);

export function AudioPlayerProvider({ children }) {
  const audioRef = useRef(null);
  const queueRef = useRef([]);

  const [queue, setQueue] = useState([]);
  const [index, setIndex] = useState(0);
  const [loadingUrl, setLoadingUrl] = useState(false);
  const [error, setError] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.9);
  const [repeat, setRepeat] = useState(false);

  const { isAuthenticated } = useAuth();
  // NOTE: This provider is mounted above RouterProvider (see `src/main.jsx`),
  // so we must not use react-router hooks here. We still hide the bar on `/auth`.
  const shouldShowBar =
    isAuthenticated && !(typeof window !== "undefined" && window.location?.pathname === "/auth");

  queueRef.current = queue;

  const currentTrack = queue[index] ?? null;

  const playQueue = useCallback((tracks, startIndex = 0) => {
    if (!tracks?.length) return;
    const safeIndex = Math.max(0, Math.min(startIndex, tracks.length - 1));
    setQueue(tracks);
    setIndex(safeIndex);
    setError(null);
  }, []);

  const playTrack = useCallback((track) => {
    if (!track?.id) return;
    playQueue([track], 0);
  }, [playQueue]);

  const next = useCallback(() => {
    setIndex((i) => {
      const len = queueRef.current.length;
      if (len === 0) return 0;
      if (i < len - 1) return i + 1;
      return i;
    });
  }, []);

  const prev = useCallback(() => {
    setIndex((i) => (i > 0 ? i - 1 : 0));
  }, []);

  const togglePlayPause = useCallback(async () => {
    const el = audioRef.current;
    if (!el?.src) return;
    if (el.paused) {
      await el.play();
    } else {
      el.pause();
    }
  }, []);

  const seek = useCallback((t) => {
    const el = audioRef.current;
    if (!el) return;
    el.currentTime = t;
    setCurrentTime(t);
  }, []);

  useEffect(() => {
    const el = audioRef.current;
    if (!el) return;

    const onEnded = () => {
      if (repeat) {
        el.currentTime = 0;
        el.play().catch(() => {});
        return;
      }
      setIndex((i) => {
        const len = queueRef.current.length;
        if (len === 0) return 0;
        if (i < len - 1) return i + 1;
        return i;
      });
    };

    const onPlay = () => setIsPlaying(true);
    const onPause = () => setIsPlaying(false);
    const onTimeUpdate = () => setCurrentTime(el.currentTime);
    const onLoadedMeta = () => setDuration(el.duration || 0);

    el.addEventListener("ended", onEnded);
    el.addEventListener("play", onPlay);
    el.addEventListener("pause", onPause);
    el.addEventListener("timeupdate", onTimeUpdate);
    el.addEventListener("loadedmetadata", onLoadedMeta);

    return () => {
      el.removeEventListener("ended", onEnded);
      el.removeEventListener("play", onPlay);
      el.removeEventListener("pause", onPause);
      el.removeEventListener("timeupdate", onTimeUpdate);
      el.removeEventListener("loadedmetadata", onLoadedMeta);
    };
  }, []);

  useEffect(() => {
    const el = audioRef.current;
    if (!el) return;
    el.volume = Math.max(0, Math.min(volume, 1));
  }, [volume]);

  useEffect(() => {
    if (queue.length === 0) {
      const el = audioRef.current;
      if (el) {
        el.pause();
        el.removeAttribute("src");
        el.load();
      }
      setIsPlaying(false);
      setCurrentTime(0);
      setDuration(0);
      return;
    }

    if (index < 0 || index >= queue.length) return;

    const track = queue[index];
    let cancelled = false;

    (async () => {
      setLoadingUrl(true);
      setError(null);
      try {
        const { data } = await http.get(`/music/tracks/${track.id}/audio-url`);
        if (cancelled) return;
        const el = audioRef.current;
        if (!el) return;
        el.src = data.url;
        try {
          await el.play();
        } catch (playErr) {
          if (playErr?.name === "NotAllowedError") {
            // браузер мог заблокировать автозапуск — пользователь нажмёт Play
          } else if (!cancelled) {
            setError(String(playErr?.message || playErr));
          }
        }
      } catch (e) {
        if (!cancelled) {
          setError(e?.response?.data?.detail || "Не удалось загрузить аудио");
        }
      } finally {
        if (!cancelled) setLoadingUrl(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [queue, index]);

  const value = useMemo(
    () => ({
      queue,
      index,
      currentTrack,
      isPlaying,
      loadingUrl,
      error,
      currentTime,
      duration,
      volume,
      repeat,
      playQueue,
      playTrack,
      next,
      prev,
      togglePlayPause,
      seek,
      setVolume,
      toggleRepeat: () => setRepeat((v) => !v),
    }),
    [
      queue,
      index,
      currentTrack,
      isPlaying,
      loadingUrl,
      error,
      currentTime,
      duration,
      volume,
      repeat,
      playQueue,
      playTrack,
      next,
      prev,
      togglePlayPause,
      seek,
    ]
  );

  return (
    <AudioPlayerContext.Provider value={value}>
      <audio ref={audioRef} style={{ display: "none" }} preload="metadata" />
      {children}
      {shouldShowBar ? <PlayerBar /> : null}
    </AudioPlayerContext.Provider>
  );
}

export function useAudioPlayer() {
  const ctx = useContext(AudioPlayerContext);
  if (!ctx) throw new Error("useAudioPlayer must be used within AudioPlayerProvider");
  return ctx;
}
