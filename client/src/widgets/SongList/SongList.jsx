import { useState } from "react";
import styles from "./SongList.module.scss"


const SongList = () => {

    const [data, setData] = useState([
        {
            img: "src/static/picture.png",
            title: "Test",
            artist: "Test",
            is_like: false,
            timedelta: "3:10"
        },
        {
            img: "src/static/picture.png",
            title: "Test",
            artist: "Test",
            is_like: false,
            timedelta: "3:10"
        },
        {
            img: "src/static/picture.png",
            title: "Test",
            artist: "Test",
            is_like: false,
            timedelta: "3:10"
        },
        {
            img: "src/static/picture.png",
            title: "Test",
            artist: "Test",
            is_like: false,
            timedelta: "3:10"
        },
        {
            img: "src/static/picture.png",
            title: "Test",
            artist: "Test",
            is_like: false,
            timedelta: "3:10"
        },
        {
            img: "src/static/picture.png",
            title: "Test",
            artist: "Test",
            is_like: false,
            timedelta: "3:10"
        },
        {
            img: "src/static/picture.png",
            title: "Test",
            artist: "Test",
            is_like: false,
            timedelta: "3:10"
        },
    ])

    return (
        <div className={styles.wrapper}>
            <div className={styles.title_list}>
                <h1>Некий топ <span>песен</span></h1>
            </div>
            <div className={styles.song_list}>
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

export default SongList;
