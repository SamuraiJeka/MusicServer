import { createBrowserRouter } from "react-router-dom"
import MainPage from "../../pages/MainPage/MainPage"
import AuthPage from "../../pages/AuthPage/AuthPage"

const router = createBrowserRouter(
    [
        {
            path: "/",
            element: <MainPage/>,
            // errorElement: <App/>,
        },
        {
            path: "/auth",
            element: <AuthPage/>,
        },
    ]
)

export default router;