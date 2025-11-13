import styles from "./MainPage.module.scss"
import AlbumList from "../../widgets/albumList/albumList";
import ArtistList from "../../widgets/ArtistList/ArtistList"


const MainPage = () => {
    return (
        <div className={styles.wrapper}>
            <AlbumList/>
            <ArtistList/>
        </div>
         
    )
};


export default MainPage;
