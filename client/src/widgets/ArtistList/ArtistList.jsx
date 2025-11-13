import { useState } from "react";
import styles from "./ArtistList.module.scss"


const AlbumList = () => {

    const [data, setData] = useState([
        {
            img: "src/static/svagajpg.jpg",
            artist: "я казах",
        },
        {
            img: "src/static/svagajpg.jpg",
            artist: "я казах",
        },
        {
            img: "src/static/svagajpg.jpg",
            title: "Я ебанутый фронт разраб",
            artist: "я казах",
        },
        {
            img: "src/static/svagajpg.jpg",
            artist: "я казах",
        },
        {
            img: "src/static/svagajpg.jpg",
            artist: "ебаните меня топором",
        }
    ])


    // TODO Тут обращение к сервису API и получение даты
    
    return (
        <div className={styles.wrapper}>
            <div className={styles.title_list}>
                <h1>А вот тут уже другой текст <span>есть</span></h1>
            </div>
            <div className={styles.artist_list}>
                {
                    data.map((el) => {
                        return (
                        <div className={styles.element}>
                            <img src={el.img} alt="" />
                            <div>
                                <span>{el.artist}</span>
                            </div>
                        </div>
                    )})
                }
            </div>
        </div>
    )
};

export default AlbumList;
