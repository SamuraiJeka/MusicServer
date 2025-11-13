import styles from "./MainPage.module.scss"
import AlbumList from "../../widgets/albumList/albumList";


const MainPage = () => {
    return (
        <div className={styles.wrapper}>
            <AlbumList/>
        </div>
         
    )
};


export default MainPage;
