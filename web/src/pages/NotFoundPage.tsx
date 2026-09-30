import { Link } from 'react-router-dom';

/** Страница для неизвестных адресов. */
export function NotFoundPage() {
  return (
    <div className="auth">
      <div className="auth__card">
        <h1 className="auth__title">Страница не найдена</h1>
        <p className="auth__subtitle">Такого раздела в приложении нет.</p>
        <Link className="button button--primary button--block" to="/files">
          Перейти к файлам
        </Link>
      </div>
    </div>
  );
}
