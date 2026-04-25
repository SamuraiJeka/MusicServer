import styles from "./PlaceholderPage.module.scss";

export default function ProfilePage() {
  return (
    <div className={styles.wrapper}>
      <div className={styles.card}>
        <h1 className={styles.title}>Моя карточка</h1>
        <p className={styles.text}>Здесь будет профиль пользователя.</p>
      </div>
    </div>
  );
}
