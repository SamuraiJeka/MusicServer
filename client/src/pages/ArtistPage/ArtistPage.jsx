import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import styles from "./ArtistPage.module.scss";

import MediaGrid from "../../widgets/MediaGrid/MediaGrid";
import { http } from "../../shared/api/http";
import TrackRow from "../../widgets/TrackRow/TrackRow";
import { useAudioPlayer } from "../../shared/player/AudioPlayerContext";

const ArtistPage = () => {
  const { userId: userIdParam } = useParams();
  const isOwnProfile = !userIdParam;
  const profileUserId = userIdParam ? Number(userIdParam) : null;

  const [profile, setProfile] = useState({ username: "…", avatar_url: null });
  const [albums, setAlbums] = useState([]);
  const [albumsLoading, setAlbumsLoading] = useState(true);
  const [topTracks, setTopTracks] = useState([]);
  const [tracksLoading, setTracksLoading] = useState(true);
  const navigate = useNavigate();
  const player = useAudioPlayer();

  const loadProfile = useCallback(async () => {
    try {
      const url = isOwnProfile ? "/user/me" : `/user/${profileUserId}`;
      const { data } = await http.get(url);
      setProfile({
        username: data.username,
        avatar_url: data.avatar_url ?? null,
      });
    } catch {
      setProfile({ username: "Профиль", avatar_url: null });
    }
  }, [isOwnProfile, profileUserId]);

  const loadAlbums = useCallback(async () => {
    setAlbumsLoading(true);
    try {
      const url = isOwnProfile
        ? "/music/me/albums"
        : `/music/users/${profileUserId}/albums`;
      const { data } = await http.get(url);
      const raw = data || [];
      const withCovers = await Promise.all(
        raw.map(async (al) => {
          if (!al?.image_filename) return al;
          try {
            const resp = await http.get(`/music/albums/${al.id}/image-url`);
            return { ...al, image_url: resp.data?.url || null };
          } catch {
            return { ...al, image_url: null };
          }
        })
      );
      setAlbums(withCovers);
    } catch {
      setAlbums([]);
    } finally {
      setAlbumsLoading(false);
    }
  }, [isOwnProfile, profileUserId]);

  const loadTopTracks = useCallback(async () => {
    setTracksLoading(true);
    try {
      const url = isOwnProfile
        ? "/music/me/tracks"
        : `/music/users/${profileUserId}/tracks`;
      const { data } = await http.get(url, { params: { limit: 20 } });
      const raw = data || [];
      const coverCache = new Map();
      const withCovers = await Promise.all(
        raw.map(async (tr) => {
          const albumId = tr?.created_album_id;
          if (!albumId) return { ...tr, cover_url: null };
          if (coverCache.has(albumId)) return { ...tr, cover_url: coverCache.get(albumId) };
          try {
            const resp = await http.get(`/music/albums/${albumId}/image-url`);
            const url = resp.data?.url || null;
            coverCache.set(albumId, url);
            return { ...tr, cover_url: url };
          } catch {
            coverCache.set(albumId, null);
            return { ...tr, cover_url: null };
          }
        })
      );
      setTopTracks(withCovers);
    } catch {
      setTopTracks([]);
    } finally {
      setTracksLoading(false);
    }
  }, [isOwnProfile, profileUserId]);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  useEffect(() => {
    loadAlbums();
  }, [loadAlbums]);

  useEffect(() => {
    loadTopTracks();
  }, [loadTopTracks]);

  useEffect(() => {
    if (!isOwnProfile) return undefined;
    const onAvatar = () => loadProfile();
    window.addEventListener("avatar-updated", onAvatar);
    return () => window.removeEventListener("avatar-updated", onAvatar);
  }, [loadProfile, isOwnProfile]);

  const queueTracks = topTracks.map((tr) => ({
    id: tr.id,
    title: tr.title,
    artist: profile.username,
  }));

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
        <h2 className={styles.sectionTitle}>
          Треки <span>по прослушиваниям</span>
        </h2>
        <div className={styles.tracks}>
          {tracksLoading ? <div style={{ color: "#ccc" }}>Загрузка…</div> : null}
          {!tracksLoading && topTracks.length === 0 ? (
            <div style={{ color: "#ccc" }}>Пока нет треков.</div>
          ) : null}
          {topTracks.map((tr, idx) => (
            <TrackRow
              key={String(tr.id)}
              index={idx + 1}
              trackId={tr.id}
              title={tr.title}
              author={profile.username}
              duration={tr.duration}
              coverSrc={tr.cover_url || "src/static/picture.png"}
              onClick={() => player.playQueue(queueTracks, idx)}
            />
          ))}
        </div>

        <MediaGrid
          title={
            <h1>
              Альбомы <span>артиста</span>
            </h1>
          }
          items={albums.map((a) => ({ ...a, author: profile.username }))}
          emptyText={albumsLoading ? "Загрузка…" : "Пока нет альбомов."}
          getTitle={(a) => a?.title ?? ""}
          getAuthor={(a) => a?.author ?? ""}
          getCoverSrc={(a) => a?.image_url || "src/static/picture.png"}
          getReleaseDate={(a) => a?.created_at}
          onItemClick={(a) => navigate(`/music/albums/${a.id}`)}
        />
      </div>
    </div>
  );
};

export default ArtistPage;
