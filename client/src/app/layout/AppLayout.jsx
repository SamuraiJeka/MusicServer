import { NavLink, Outlet, useNavigate } from "react-router-dom";
import styles from "./AppLayout.module.scss";
import { useAuth } from "../../shared/auth/AuthContext";
import SearchBar from "../../shared/search/SearchBar";

export default function AppLayout() {
  const auth = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    auth.logout();
    navigate("/auth", { replace: true });
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
