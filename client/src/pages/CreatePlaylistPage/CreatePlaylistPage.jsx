import { useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./CreatePlaylistPage.module.scss";
import { http } from "../../shared/api/http";

export default function CreatePlaylistPage() {
  const coverInputRef = useRef(null);
  const [title, setTitle] = useState("");
  const [coverFile, setCoverFile] = useState(null);
  const [coverPreviewUrl, setCoverPreviewUrl] = useState(null);
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const trimmed = useMemo(() => title.trim(), [title]);

  const pickCover = () => coverInputRef.current?.click();

  const onCoverChange = (e) => {
    const f = e.target.files?.[0] || null;
    e.target.value = "";
    setError(null);
    setCoverFile(f);
    if (coverPreviewUrl) URL.revokeObjectURL(coverPreviewUrl);
    setCoverPreviewUrl(f ? URL.createObjectURL(f) : null);
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    if (!trimmed) {
      setError("Название не должно быть пустым");
      return;
    }
    setIsSubmitting(true);
    try {
      const resp = await http.post("/music/playlists", { title: trimmed });
      const playlistId = resp.data?.id;
      if (!playlistId) throw new Error("Missing playlist id");

      if (coverFile) {
        const fd = new FormData();
        fd.append("file", coverFile);
        await http.post(`/music/playlists/${playlistId}/image`, fd);
      }
      navigate("/library", { replace: true });
    } catch (err) {
      setError(err?.response?.data?.detail || "Ошибка создания плейлиста");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.wrapper}>
      <div className={styles.card}>
        <h1 className={styles.title}>Создать плейлист</h1>
        <form className={styles.form} onSubmit={onSubmit}>
          <div>
            <div className={styles.label}>Название</div>
            <input
              className={styles.input}
            value={title}
            onChange={(e) => {
              setTitle(e.target.value);
              setError(null);
            }}
            placeholder="Название плейлиста"
              disabled={isSubmitting}
            />
          </div>

          <div>
            <div className={styles.label}>Фотография плейлиста (необязательно)</div>
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
                Выбрать фото
              </button>
              {coverFile ? <p className={styles.hint}>{coverFile.name}</p> : null}
            </div>
          </div>

          {error ? <p className={styles.error}>{error}</p> : null}

          <button type="submit" className={styles.submitBtn} disabled={isSubmitting}>
            {isSubmitting ? "Создаём…" : "Создать"}
          </button>
        </form>
      </div>
    </div>
  );
}

