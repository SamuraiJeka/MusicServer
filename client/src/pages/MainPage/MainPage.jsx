import styles from "./MainPage.module.scss"

import AlbumList from "../../widgets/albumList/albumList";
import ArtistList from "../../widgets/ArtistList/ArtistList"
import SongList from "../../widgets/SongList/SongList";


const MainPage = () => {
    return (
        <div className={styles.wrapper}>
            <div className={styles.main_container}>
                <SongList/>
                <AlbumList/>
                <ArtistList/>
            </div>
        </div>
         
    )
};


export default MainPage;
