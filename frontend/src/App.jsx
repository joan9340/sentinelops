import SettingsBar from './components/SettingsBar';
import { AuthProvider, useAuth } from './context/AuthContext';
import { SettingsProvider } from './context/SettingsContext';
import AuthPage from './pages/AuthPage';
import DashboardPage from './pages/DashboardPage';

function Shell() {
  const { token } = useAuth();
  return (
    <>
      <div className="app-root">{token ? <DashboardPage /> : <AuthPage />}</div>
      {/* Siempre visible, en login y dentro del panel */}
      <SettingsBar />
    </>
  );
}

export default function App() {
  return (
    <SettingsProvider>
      <AuthProvider>
        <Shell />
      </AuthProvider>
    </SettingsProvider>
  );
}
