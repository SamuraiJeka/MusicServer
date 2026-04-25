import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./AuthPage.module.scss";
import { http } from "../../shared/api/http";
import { useAuth } from "../../shared/auth/AuthContext";

const MIN_PASSWORD_LEN = 8;

function formatServerDetail(detail) {
  if (detail == null) return "Ошибка авторизации";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const parts = detail.map((item) => {
      if (typeof item === "string") return item;
      if (item && typeof item === "object" && "msg" in item) return item.msg;
      return JSON.stringify(item);
    });
    return parts.filter(Boolean).join("\n");
  }
  if (typeof detail === "object") {
    if ("msg" in detail) return String(detail.msg);
    try {
      return JSON.stringify(detail);
    } catch {
      return "Ошибка авторизации";
    }
  }
  return String(detail);
}

function validateSignup(values) {
  const errors = {};
  const username = values.username?.trim() ?? "";
  const email = values.email?.trim() ?? "";
  const password = values.password ?? "";

  if (!username) errors.username = "Заполните поле";
  if (!email) errors.email = "Заполните поле";
  if (!password.trim()) errors.password = "Заполните поле";
  else if (password.length < MIN_PASSWORD_LEN) {
    errors.password = `Пароль не короче ${MIN_PASSWORD_LEN} символов`;
  }

  return errors;
}

function validateLogin(values) {
  const errors = {};
  const email = values.email?.trim() ?? "";
  const password = values.password ?? "";

  if (!email) errors.email = "Заполните поле";
  if (!password.trim()) errors.password = "Заполните поле";
  else if (password.length < MIN_PASSWORD_LEN) {
    errors.password = `Пароль не короче ${MIN_PASSWORD_LEN} символов`;
  }

  return errors;
}

const AuthPage = () => {

    const [loginState, setLoginState] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [serverError, setServerError] = useState(null);
    const [signupErrors, setSignupErrors] = useState({});
    const [loginErrors, setLoginErrors] = useState({});
    const navigate = useNavigate();
    const auth = useAuth();

    const [signup, setSignup] = useState({ username: "", email: "", password: "" });
    const [login, setLogin] = useState({ email: "", password: "" });

    const openLoginForm = () => {
        setLoginState(true);
        setServerError(null);
        setSignupErrors({});
        setLoginErrors({});
    }

    const closeLoginForm = () => {
        setLoginState(false);
        setServerError(null);
        setSignupErrors({});
        setLoginErrors({});
    }

    const submitLabel = useMemo(() => (loginState ? "Sign Up" : "Login"), [loginState]);

    const onSubmit = async (e) => {
      e.preventDefault();
      setServerError(null);

      if (loginState) {
        const se = validateSignup(signup);
        setSignupErrors(se);
        setLoginErrors({});
        if (Object.keys(se).length > 0) return;
      } else {
        const le = validateLogin(login);
        setLoginErrors(le);
        setSignupErrors({});
        if (Object.keys(le).length > 0) return;
      }

      setIsSubmitting(true);
      try {
        if (loginState) {
          await http.post("/auth/registration", signup);
          // auto-login after registration
          const resp = await http.post("/auth/login", { email: signup.email, password: signup.password });
          auth.login(resp.data);
          navigate("/", { replace: true });
        } else {
          const resp = await http.post("/auth/login", login);
          auth.login(resp.data);
          navigate("/", { replace: true });
        }
      } catch (err) {
        const detail = err?.response?.data?.detail;
        setServerError(formatServerDetail(detail));
      } finally {
        setIsSubmitting(false);
      }
    };

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
          (<form key="signup" className={styles.form} onSubmit={onSubmit}>
            <div className={styles.row}>
              <div className={styles.field}>
                <input
                  type="text"
                  placeholder="Ваш логин"
                  value={signup.username}
                  onChange={(e) => {
                    setSignup((s) => ({ ...s, username: e.target.value }));
                    setSignupErrors((prev) => ({ ...prev, username: undefined }));
                    setServerError(null);
                  }}
                  autoComplete="username"
                />
                {signupErrors.username ? (
                  <span className={styles.fieldError}>{signupErrors.username}</span>
                ) : null}
              </div>
              <div className={styles.field}>
                <input
                  type="text"
                  placeholder="Ваша почта"
                  value={signup.email}
                  onChange={(e) => {
                    setSignup((s) => ({ ...s, email: e.target.value }));
                    setSignupErrors((prev) => ({ ...prev, email: undefined }));
                    setServerError(null);
                  }}
                  autoComplete="email"
                />
                {signupErrors.email ? (
                  <span className={styles.fieldError}>{signupErrors.email}</span>
                ) : null}
              </div>
            </div>

            <div className={styles.field}>
              <input
                type="password"
                placeholder="Пароль"
                value={signup.password}
                onChange={(e) => {
                  setSignup((s) => ({ ...s, password: e.target.value }));
                  setSignupErrors((prev) => ({ ...prev, password: undefined }));
                  setServerError(null);
                }}
                autoComplete="new-password"
              />
              {signupErrors.password ? (
                <span className={styles.fieldError}>{signupErrors.password}</span>
              ) : null}
            </div>

            {serverError ? <div className={styles.error}>{serverError}</div> : null}

            <button type="submit" className={styles.submit_btn} disabled={isSubmitting}>
              {isSubmitting ? "..." : submitLabel}
            </button>

          </form>) :
          (<form key="login" className={styles.form} onSubmit={onSubmit}>
            <div className={styles.single_input}>
              <div className={styles.field}>
                <input
                  type="text"
                  placeholder="Почта"
                  value={login.email}
                  onChange={(e) => {
                    setLogin((s) => ({ ...s, email: e.target.value }));
                    setLoginErrors((prev) => ({ ...prev, email: undefined }));
                    setServerError(null);
                  }}
                  autoComplete="email"
                />
                {loginErrors.email ? (
                  <span className={styles.fieldError}>{loginErrors.email}</span>
                ) : null}
              </div>
              <div className={styles.field}>
                <input
                  type="password"
                  placeholder="Пароль"
                  value={login.password}
                  onChange={(e) => {
                    setLogin((s) => ({ ...s, password: e.target.value }));
                    setLoginErrors((prev) => ({ ...prev, password: undefined }));
                    setServerError(null);
                  }}
                  autoComplete="current-password"
                />
                {loginErrors.password ? (
                  <span className={styles.fieldError}>{loginErrors.password}</span>
                ) : null}
              </div>
            </div>

            {serverError ? <div className={styles.error}>{serverError}</div> : null}

            <button type="submit" className={styles.submit_btn} disabled={isSubmitting}>
              {isSubmitting ? "..." : submitLabel}
            </button>
            
          </form>)
          }
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
