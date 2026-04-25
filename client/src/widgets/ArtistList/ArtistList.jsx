import { useState } from "react";
import styles from "./ArtistList.module.scss"


const ArtistList = ({title}) => {

    const [data, setData] = useState([
        {
            img: "src/static/picture.png",
            artist: "Test",
        },
        {
            img: "src/static/picture.png",
            artist: "Test",
        },
        {
            img: "src/static/picture.png",
            title: "Test",
            artist: "Test",
        },
        {
            img: "src/static/picture.png",
            artist: "Test",
        },
        {
            img: "src/static/picture.png",
            artist: "Test",
        }
    ])


    // TODO Тут обращение к сервису API и получение даты
    
    return (
        <div className={styles.wrapper}>
            <div className={styles.title_list}>
                {title}
            </div>
            <div className={styles.artist_list}>
                {
                    data.map((el) => {
                        return (
                        <div className={styles.element} key={`${el.artist}-${Math.random()}`}>
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


export default ArtistList;
