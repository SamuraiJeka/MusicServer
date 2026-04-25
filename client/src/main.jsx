import { createRoot } from 'react-dom/client'
import App from './app/App.jsx'
import { AuthProvider } from "./shared/auth/AuthContext.jsx";

createRoot(document.getElementById('root')).render(
    <AuthProvider>
        <App/>
    </AuthProvider>
)
