import { useRef, useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import styles from "./AppLayout.module.scss";
import { useAuth } from "../../shared/auth/AuthContext";
import SearchBar from "../../shared/search/SearchBar";
import { http } from "../../shared/api/http";

export default function AppLayout() {
  const auth = useAuth();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [avatarUploading, setAvatarUploading] = useState(false);
  const [avatarError, setAvatarError] = useState(null);

  const handleLogout = () => {
    auth.logout();
    navigate("/auth", { replace: true });
  };

  const openAvatarPicker = () => {
    fileInputRef.current?.click();
  };

  const handleAvatarFile = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file || !file.type.startsWith("image/")) return;
    setAvatarUploading(true);
    setAvatarError(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      await http.post("/user/me/avatar", formData);
      window.dispatchEvent(new CustomEvent("avatar-updated"));
    } catch {
      setAvatarError("Не удалось загрузить фото.");
    } finally {
      setAvatarUploading(false);
    }
  };

  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar} aria-label="Навигация">
        <div className={styles.sidebarInner}>
          <nav className={styles.navTop}>
            <NavLink to="/" end className={({ isActive }) => `${styles.navLink} ${isActive ? styles.navLinkActive : ""}`}>
              Главная
            </NavLink>
            <NavLink
              to="/library"
              className={({ isActive }) => `${styles.navLink} ${isActive ? styles.navLinkActive : ""}`}
            >
              Моя медиатека
            </NavLink>
            <NavLink
              to="/chats"
              className={({ isActive }) => `${styles.navLink} ${isActive ? styles.navLinkActive : ""}`}
            >
              Чаты
            </NavLink>
          </nav>
          <nav className={styles.navBottom}>
            <NavLink
              to="/artist"
              end
              className={({ isActive }) => `${styles.navLink} ${isActive ? styles.navLinkActive : ""}`}
            >
              Моя карточка
            </NavLink>
            <NavLink
              to="/create-album"
              className={({ isActive }) => `${styles.navLink} ${isActive ? styles.navLinkActive : ""}`}
            >
              Создать альбом
            </NavLink>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp,image/gif"
              className={styles.hiddenFileInput}
              aria-hidden
              tabIndex={-1}
              onChange={handleAvatarFile}
            />
            <button
              type="button"
              className={styles.changePhotoBtn}
              onClick={openAvatarPicker}
              disabled={avatarUploading}
            >
              {avatarUploading ? "Загрузка…" : "Изменить фото"}
            </button>
            {avatarError ? <p className={styles.avatarError}>{avatarError}</p> : null}
            <button type="button" className={styles.logoutBtn} onClick={handleLogout}>
              Выйти
            </button>
          </nav>
        </div>
      </aside>
      <main className={styles.main}>
        <div className={styles.topbar}>
          <div className={styles.topbarInner}>
            <SearchBar />
          </div>
        </div>
        <div className={styles.mainInner}>
          <Outlet />
        </div>
      </main>
    </div>
  );
}
