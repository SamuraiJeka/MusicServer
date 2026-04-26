import { useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./CreateAlbumPage.module.scss";
import { http } from "../../shared/api/http";

export default function CreateAlbumPage() {
  const navigate = useNavigate();
  const coverInputRef = useRef(null);
  const trackFileRefs = useRef({});

  const makeId = () => {
    if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID();
    return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  };

  const [title, setTitle] = useState("");
  const [coverFile, setCoverFile] = useState(null);
  const [coverPreviewUrl, setCoverPreviewUrl] = useState(null);
  const [tracks, setTracks] = useState([{ id: makeId(), title: "", file: null }]);
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const trimmedTitle = useMemo(() => title.trim(), [title]);

  const addTrack = () => {
    setTracks((prev) => [...prev, { id: makeId(), title: "", file: null }]);
  };

  const removeTrack = (id) => {
    setTracks((prev) => (prev.length <= 1 ? prev : prev.filter((t) => t.id !== id)));
    delete trackFileRefs.current[id];
  };

  const updateTrack = (id, patch) => {
    setTracks((prev) => prev.map((t) => (t.id === id ? { ...t, ...patch } : t)));
  };

  const pickCover = () => coverInputRef.current?.click();

  const onCoverChange = (e) => {
    const f = e.target.files?.[0] || null;
    e.target.value = "";
    setError(null);
    setCoverFile(f);
    if (coverPreviewUrl) URL.revokeObjectURL(coverPreviewUrl);
    setCoverPreviewUrl(f ? URL.createObjectURL(f) : null);
  };

  const pickTrackFile = (id) => {
    trackFileRefs.current[id]?.click();
  };

  const onTrackFileChange = (id, e) => {
    const f = e.target.files?.[0] || null;
    e.target.value = "";
    setError(null);
    updateTrack(id, { file: f });
  };

  const validate = () => {
    if (!trimmedTitle) return "Название альбома не должно быть пустым";
    const ready = tracks.filter((t) => t.title.trim() && t.file);
    if (ready.length === 0) return "Добавьте хотя бы один трек (название + mp3)";
    const bad = tracks.find((t) => (t.title.trim() && !t.file) || (!t.title.trim() && t.file));
    if (bad) return "У каждого трека должны быть и название, и аудиофайл";
    return null;
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    const v = validate();
    if (v) {
      setError(v);
      return;
    }
    setIsSubmitting(true);
    try {
      // 1) create album
      const albumResp = await http.post("/music/albums", { title: trimmedTitle });
      const albumId = albumResp.data?.id;
      if (!albumId) throw new Error("Missing album id");

      // 2) cover
      if (albumId && coverFile) {
        const fd = new FormData();
        fd.append("file", coverFile);
        await http.post(`/music/albums/${albumId}/image`, fd);
      }

      // 3) tracks (sequential to keep UX predictable)
      for (const t of tracks) {
        const tTitle = t.title.trim();
        if (!tTitle || !t.file) continue;
        const fd = new FormData();
        fd.append("title", tTitle);
        fd.append("file", t.file);
        await http.post(`/music/albums/${albumId}/tracks`, fd);
      }

      navigate("/library", { replace: true });
    } catch (err) {
      setError(err?.response?.data?.detail || "Ошибка создания альбома");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.wrapper}>
      <div className={styles.card}>
        <h1 className={styles.title}>Создать альбом</h1>
        <form className={styles.form} onSubmit={onSubmit}>
          <div>
            <div className={styles.label}>Заголовок</div>
            <input
              className={styles.input}
              value={title}
              onChange={(e) => {
                setTitle(e.target.value);
                setError(null);
              }}
              placeholder="Название альбома"
              disabled={isSubmitting}
            />
          </div>

          <div>
            <div className={styles.label}>Обложка (необязательно)</div>
            <div className={styles.coverRow}>
              <div className={styles.coverPreview} aria-label="Превью обложки">
                {coverPreviewUrl ? <img src={coverPreviewUrl} alt="" /> : null}
              </div>
              <input
                ref={coverInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp,image/gif"
                className={styles.hiddenFileInput}
                onChange={onCoverChange}
                disabled={isSubmitting}
              />
              <button type="button" className={styles.fileBtn} onClick={pickCover} disabled={isSubmitting}>
                Выбрать обложку
              </button>
              {coverFile ? <div className={styles.hint}>{coverFile.name}</div> : null}
            </div>
          </div>

          <div className={styles.tracksHeader}>
            <h2 className={styles.subtitle}>Треки</h2>
            <p className={styles.hint}>Слева mp3, справа заголовок</p>
          </div>

          {tracks.map((t) => (
            <div key={t.id} className={styles.trackRow}>
              <div className={styles.audioDrop}>
                <input
                  ref={(el) => {
                    if (el) trackFileRefs.current[t.id] = el;
                  }}
                  type="file"
                  accept="audio/mpeg,audio/mp3"
                  className={styles.hiddenFileInput}
                  onChange={(e) => onTrackFileChange(t.id, e)}
                  disabled={isSubmitting}
                />
                <button type="button" className={styles.fileBtn} onClick={() => pickTrackFile(t.id)} disabled={isSubmitting}>
                  Загрузить аудио
                </button>
                <div className={styles.audioName}>{t.file ? t.file.name : "Файл не выбран"}</div>
              </div>
              <div className={styles.trackRight}>
                <div className={styles.rowTop}>
                  <div className={styles.label} style={{ marginBottom: 0 }}>
                    Заголовок трека
                  </div>
                  <button
                    type="button"
                    className={styles.removeBtn}
                    onClick={() => removeTrack(t.id)}
                    disabled={isSubmitting || tracks.length <= 1}
                    title="Удалить"
                  >
                    Удалить
                  </button>
                </div>
                <input
                  className={styles.input}
                  value={t.title}
                  onChange={(e) => updateTrack(t.id, { title: e.target.value })}
                  placeholder="Название трека"
                  disabled={isSubmitting}
                />
              </div>
            </div>
          ))}

          <button type="button" className={styles.plusBtn} onClick={addTrack} disabled={isSubmitting} aria-label="Добавить трек">
            +
          </button>

          {error ? <p className={styles.error}>{error}</p> : null}

          <button type="submit" className={styles.submitBtn} disabled={isSubmitting}>
            {isSubmitting ? "Создаём…" : "Создать альбом"}
          </button>
        </form>
      </div>
    </div>
  );
}
