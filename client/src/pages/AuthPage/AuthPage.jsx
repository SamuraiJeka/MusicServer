import { useState } from "react";
import styles from "./AuthPage.module.scss";

const AuthPage = () => {

    const [loginState, setLoginState] = useState(false);

    const openLoginForm = () => {
        setLoginState(true);
    }

    const closeLoginForm = () => {
        setLoginState(false);
    }

  return (
    <div className={styles.wrapper}>
      <div className={styles.main_container}>
        <div className={styles.main_text}>
          <h1>Music service</h1>
          <p>
            Lorem Ipsum - это текст-"рыба", часто используемый в печати и
            вэб-дизайне. Lorem Ipsum является стандартной "рыбой" для текстов на
            латинице с начала XVI века. В то время некий безымянный печатник
          </p>
        </div>

        <div className={styles.form_container}>
          <div className={styles.tabs}>
            <div className={`${styles.tab} ${loginState ? styles.active : ''}`} onClick={() => openLoginForm()} >Sign Up</div>
            <div className={`${styles.tab} ${!loginState ? styles.active : ''}`} onClick={() => closeLoginForm()}>Login</div>
          </div>
          {loginState ? 
          (<form key="signup" className={styles.form}>
            <div className={styles.row}>
              <input type="text" placeholder="Ваш логин" />
              <input type="text" placeholder="Ваша почта" />
            </div>

            <input type="email" className={styles.single_input} placeholder="Пароль"/>

            <button type="submit" className={styles.submit_btn}>
              Sign Up
            </button>

          </form>) :
          (<form key="login" className={styles.form}>
            <div className={styles.single_input}>
              <input type="text" placeholder="Логин" />
              <input type="text" placeholder="Пароль" />
            </div>

            <button type="submit" className={styles.submit_btn}>
              Sign Up
            </button>
            
          </form>)
          }
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
