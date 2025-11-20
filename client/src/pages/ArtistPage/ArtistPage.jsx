import { useState } from "react";
import styles from "./ArtistPage.module.scss";

import SongList from "../../widgets/SongList/SongList";
import AlbumList from "../../widgets/AlbumList/AlbumList";
import ArtisList from "../../widgets/ArtistList/ArtistList"

const ArtistPage = () => {

    const [data, setData] = useState(
        {
            preview_img: "src/static/black.png",
            artist: "Оксимирон",
        }
    )

    return (
        <div className={styles.wrapper}>
            <div className={styles.main_content}>
                <div className={styles.preview_background} style={{'--preview_img': `url(${data.preview_img})`}}>
                    <h1>{data.artist}</h1>
                </div>
                <SongList/>
                <AlbumList title={<h1>Альбомы <span>артиста</span></h1>}/>
                <AlbumList title={<h1>Мини-альбомы и <span>синглы</span></h1>}/>
                <ArtisList title={<h1>Связанные <span>артисты</span></h1>}/>
            </div>
        </div>
    )
};


export default ArtistPage;
