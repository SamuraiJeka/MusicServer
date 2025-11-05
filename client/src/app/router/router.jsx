import { createBrowserRouter } from "react-router-dom"
import MainPage from "../../pages/MainPage/MainPage"

const router = createBrowserRouter(
    [
        {
            path: "/",
            element: <MainPage/>,
            // errorElement: <App/>,
            
        }
    ]
)

export default router;