import { createBrowserRouter } from "react-router-dom"
import MainPage from "../../pages/MainPage/MainPage"
import AuthPage from "../../pages/AuthPage/AuthPage"
import ArtistPage from "../../pages/ArtistPage/ArtistPage"
import RequireAuth from "../../shared/auth/RequireAuth"


const router = createBrowserRouter(
    [
        {
            path: "/",
            element: (
                <RequireAuth>
                    <MainPage/>
                </RequireAuth>
            ),
            // errorElement: <App/>,
        },
        {
            path: "/auth",
            element: <AuthPage/>,
        },
        {
            path: "/artist",
            element: (
                <RequireAuth>
                    <ArtistPage/>
                </RequireAuth>
            ),
        },
    ]
)

export default router;