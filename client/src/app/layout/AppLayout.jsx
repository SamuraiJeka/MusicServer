import { NavLink, Outlet, useNavigate } from "react-router-dom";
import styles from "./AppLayout.module.scss";
import { useAuth } from "../../shared/auth/AuthContext";

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
            <button type="button" className={styles.navButton} disabled title="Скоро">
              Чаты
            </button>
          </nav>
          <nav className={styles.navBottom}>
            <NavLink
              to="/profile"
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
        <Outlet />
      </main>
    </div>
  );
}
