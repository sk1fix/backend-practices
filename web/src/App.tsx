import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { ToastProvider } from './components/Toasts';
import { FilesPage } from './pages/FilesPage';
import { LoginPage } from './pages/LoginPage';
import { NotFoundPage } from './pages/NotFoundPage';

/**
 * Корень приложения.
 * Используется BrowserRouter, поэтому сервер отдаёт index.html на любые
 * адреса, не начинающиеся с /api.
 */
export function App() {
  return (
    <BrowserRouter>
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
