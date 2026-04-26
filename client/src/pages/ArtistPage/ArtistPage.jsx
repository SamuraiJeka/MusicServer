import { useCallback, useEffect, useState } from "react";
import styles from "./ArtistPage.module.scss";

import SongList from "../../widgets/SongList/SongList";
import AlbumList from "../../widgets/AlbumList/AlbumList";
import ArtisList from "../../widgets/ArtistList/ArtistList";
import { http } from "../../shared/api/http";

const ArtistPage = () => {
  const [profile, setProfile] = useState({ username: "…", avatar_url: null });

  const loadProfile = useCallback(async () => {
    try {
      const { data } = await http.get("/user/me");
      setProfile({
        username: data.username,
        avatar_url: data.avatar_url ?? null,
      });
    } catch {
      setProfile({ username: "Профиль", avatar_url: null });
    }
  }, []);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  useEffect(() => {
    const onAvatar = () => loadProfile();
    window.addEventListener("avatar-updated", onAvatar);
    return () => window.removeEventListener("avatar-updated", onAvatar);
  }, [loadProfile]);

  return (
    <div className={styles.wrapper}>
      <div className={styles.main_content}>
        <div className={styles.preview_background}>
          {profile.avatar_url ? (
            <img src={profile.avatar_url} alt="" className={styles.previewImage} />
          ) : null}
          <div className={styles.previewForeground}>
            <h1>{profile.username}</h1>
          </div>
        </div>
        <SongList />
        <AlbumList title={<h1>Альбомы <span>артиста</span></h1>} />
        <AlbumList title={<h1>Мини-альбомы и <span>синглы</span></h1>} />
        <ArtisList title={<h1>Связанные <span>артисты</span></h1>} />
      </div>
    </div>
  );
};

export default ArtistPage;
