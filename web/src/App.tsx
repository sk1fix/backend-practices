import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { ToastProvider } from './components/Toasts';
import { FilesPage } from './pages/FilesPage';
import { LoginPage } from './pages/LoginPage';
import { NotFoundPage } from './pages/NotFoundPage';

/**
 * Корень приложения.
 * Используется BrowserRouter, поэтому сервер отдаёт index.html на любые
 * адреса, не начинающиеся с /api. basename совпадает с base сборки Vite,
 * чтобы роутинг работал и при отдаче из подкаталога (например, /cloud-storage/).
 */
const ROUTER_BASENAME = import.meta.env.BASE_URL.replace(/\/+$/, '') || '/';

export function App() {
  return (
    <BrowserRouter basename={ROUTER_BASENAME}>
      <ToastProvider>
        <Routes>
          <Route path="/" element={<Navigate to="/files" replace />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/files" element={<FilesPage />} />
          <Route path="/files/folder/:id" element={<FilesPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </ToastProvider>
    </BrowserRouter>
  );
}

export default App;
