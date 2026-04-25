import { createBrowserRouter } from "react-router-dom"
import MainPage from "../../pages/MainPage/MainPage"
import AuthPage from "../../pages/AuthPage/AuthPage"
import ArtistPage from "../../pages/ArtistPage/ArtistPage"
import ProfilePage from "../../pages/ProfilePage/ProfilePage"
import CreateAlbumPage from "../../pages/CreateAlbumPage/CreateAlbumPage"
import MyLibraryPage from "../../pages/MyLibraryPage/MyLibraryPage"
import CreatePlaylistPage from "../../pages/CreatePlaylistPage/CreatePlaylistPage"
import AppLayout from "../layout/AppLayout"
import RequireAuth from "../../shared/auth/RequireAuth"


const router = createBrowserRouter(
    [
        {
            path: "/",
            element: (
                <RequireAuth>
                    <AppLayout />
                </RequireAuth>
            ),
            children: [
                {
                    index: true,
                    element: <MainPage />,
                },
                {
                    path: "artist",
                    element: <ArtistPage />,
                },
                {
                    path: "profile",
                    element: <ProfilePage />,
                },
                {
                    path: "create-album",
                    element: <CreateAlbumPage />,
                },
                {
                    path: "library",
                    element: <MyLibraryPage />,
                },
                {
                    path: "create-playlist",
                    element: <CreatePlaylistPage />,
                },
            ],
        },
        {
            path: "/auth",
            element: <AuthPage/>,
        },
    ]
)

export default router;