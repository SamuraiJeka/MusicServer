import { useState } from "react";
import styles from "./AlbumList.module.scss"


const AlbumList = ({title}) => {

    const [data, setData] = useState([
        {
            img: "src/static/picture.png",
            title: "Test",
            artist: "Test",
        },
        {
            img: "src/static/picture.png",
            title: "Test",
            artist: "Test",
        },
        {
            img: "src/static/picture.png",
            title: "Test",
            artist: "Test",
        },
        {
            img: "src/static/picture.png",
            title: "Test",
            artist: "Test",
        },
        {
            img: "src/static/picture.png",
            title: "Test",
            artist: "Test",
        }
    ])


    // TODO Тут обращение к сервису API и получение даты
    
    return (
        <div className={styles.wrapper}>
            <div className={styles.title_list}>
                {title}
            </div>
            <div className={styles.album_list}>
                {
                    data.map((el) => {
                        return (
                        <div className={styles.element} key={`${el.title}-${el.artist}-${Math.random()}`}>
                            <img src={el.img} alt="" />
                            <div>
                                <p>{el.title}</p>
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
