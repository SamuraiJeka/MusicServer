import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "../ProfilePage/PlaceholderPage.module.scss";
import { http } from "../../shared/api/http";

export default function CreatePlaylistPage() {
  const [title, setTitle] = useState("");
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const trimmed = useMemo(() => title.trim(), [title]);

  const onSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    if (!trimmed) {
      setError("Название не должно быть пустым");
      return;
    }
    setIsSubmitting(true);
    try {
      await http.post("/music/playlists", { title: trimmed });
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
        <form onSubmit={onSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <input
            value={title}
            onChange={(e) => {
              setTitle(e.target.value);
              setError(null);
            }}
            placeholder="Название плейлиста"
            style={{
              height: 40,
              paddingLeft: 12,
              borderRadius: 10,
              border: "none",
              outline: "none",
              backgroundColor: "#014861",
              color: "white",
              fontSize: 14,
            }}
          />
          {error ? <div className={styles.text} style={{ color: "#fff" }}>{error}</div> : null}
          <button
            type="submit"
            disabled={isSubmitting}
            style={{
              backgroundColor: "#007BFF",
              border: "none",
              padding: "10px 14px",
              borderRadius: 10,
              fontWeight: 800,
              color: "white",
              cursor: isSubmitting ? "default" : "pointer",
              opacity: isSubmitting ? 0.7 : 1,
            }}
          >
            {isSubmitting ? "..." : "Создать"}
          </button>
        </form>
      </div>
    </div>
  );
}

