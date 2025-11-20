import { createBrowserRouter } from "react-router-dom"
import MainPage from "../../pages/MainPage/MainPage"
import AuthPage from "../../pages/AuthPage/AuthPage"
import ArtistPage from "../../pages/ArtistPage/ArtistPage"


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
        {
            path: "/artist",
            element: <ArtistPage/>,
        },
    ]
)

export default router;