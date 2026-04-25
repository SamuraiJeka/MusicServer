import { createRoot } from 'react-dom/client'
import App from './app/App.jsx'
import { AuthProvider } from "./shared/auth/AuthContext.jsx";
import { AudioPlayerProvider } from "./shared/player/AudioPlayerContext.jsx";

createRoot(document.getElementById('root')).render(
    <AuthProvider>
        <AudioPlayerProvider>
            <App/>
        </AudioPlayerProvider>
    </AuthProvider>
)
