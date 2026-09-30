import { useEffect, useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { errorMessage, getCurrentUser, login, register } from '../api';
import { CloseIcon, StorageIcon } from '../components/Icons';
import { validateLogin, validatePassword, validateUsername } from '../utils/validation';

type AuthMode = 'login' | 'register';

/** На странице входа ответ 401 не должен приводить к повторному переходу на /login. */
const skipAuthRedirect = { skipAuthRedirect: true };

/** Страница входа и регистрации. */
export function LoginPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<AuthMode>('login');
  const [loginName, setLoginName] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    let cancelled = false;
    getCurrentUser({ skipAuthRedirect: true })
      .then(() => {
        if (!cancelled) {
          navigate('/files', { replace: true });
        }
      })
      .catch(() => {
        if (!cancelled) {
          setChecking(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [navigate]);

  const switchMode = (next: AuthMode) => {
    setMode(next);
    setError(null);
    setNotice(null);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const loginError = validateLogin(loginName);
    if (loginError !== null) {
      setError(loginError);
      return;
    }

    const passwordError = validatePassword(password);
    if (passwordError !== null) {
      setError(passwordError);
      return;
    }

    if (mode === 'register') {
      const usernameError = validateUsername(username);
      if (usernameError !== null) {
        setError(usernameError);
        return;
      }
    }

    setSubmitting(true);
    setError(null);
    setNotice(null);

    const credentials = { login: loginName.trim(), password };

    try {
      if (mode === 'register') {
        await register({ ...credentials, username: username.trim() }, skipAuthRedirect);
        try {
          // Регистрация не выдаёт cookie, поэтому сразу выполняем вход.
          await login(credentials, skipAuthRedirect);
        } catch {
          setMode('login');
          setNotice('Регистрация прошла успешно. Войдите под своими данными.');
          return;
        }
      } else {
        await login(credentials, skipAuthRedirect);
      }
      navigate('/files', { replace: true });
    } catch (submitError: unknown) {
      setError(errorMessage(submitError));
    } finally {
      setSubmitting(false);
    }
  };

  if (checking) {
    return (
      <div className="auth">
        <div className="auth__card">
          <p className="state state--loading">Проверка авторизации...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="auth">
      <div className="auth__card">
        <div className="auth__brand">
          <span className="auth__logo" aria-hidden="true">
            <StorageIcon width={26} height={26} />
          </span>
          <h1 className="auth__title">Облачное хранилище</h1>
          <p className="auth__subtitle">Файлы и папки доступны из любого места</p>
        </div>

        <div className="tabs" role="tablist" aria-label="Вход или регистрация">
          <button
            type="button"
            role="tab"
            aria-selected={mode === 'login'}
            className={`tabs__tab${mode === 'login' ? ' tabs__tab--active' : ''}`}
            onClick={() => {
              switchMode('login');
            }}
          >
            Вход
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={mode === 'register'}
            className={`tabs__tab${mode === 'register' ? ' tabs__tab--active' : ''}`}
            onClick={() => {
              switchMode('register');
            }}
          >
            Регистрация
          </button>
        </div>

        {notice !== null && (
          <div className="banner banner--info" role="status">
            <span className="banner__text">{notice}</span>
            <button
              type="button"
              className="icon-button icon-button--small"
              onClick={() => {
                setNotice(null);
              }}
              aria-label="Закрыть сообщение"
              title="Закрыть"
            >
              <CloseIcon width={16} height={16} />
            </button>
          </div>
        )}

        {error !== null && (
          <div className="banner banner--error" role="alert">
            <span className="banner__text">{error}</span>
            <button
              type="button"
              className="icon-button icon-button--small"
              onClick={() => {
                setError(null);
              }}
              aria-label="Закрыть сообщение об ошибке"
              title="Закрыть"
            >
              <CloseIcon width={16} height={16} />
            </button>
          </div>
        )}

        <form className="form" onSubmit={handleSubmit} noValidate>
          <label className="field">
            <span className="field__label">Логин</span>
            <input
              className="input"
              type="text"
              value={loginName}
              autoComplete="username"
              spellCheck={false}
              disabled={submitting}
              onChange={(event) => {
                setLoginName(event.target.value);
              }}
            />
          </label>

          {mode === 'register' && (
            <label className="field">
              <span className="field__label">Имя пользователя</span>
              <input
                className="input"
                type="text"
                value={username}
                autoComplete="nickname"
                disabled={submitting}
                onChange={(event) => {
                  setUsername(event.target.value);
                }}
              />
            </label>
          )}

          <label className="field">
            <span className="field__label">Пароль</span>
            <input
              className="input"
              type="password"
              value={password}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              minLength={8}
              disabled={submitting}
              onChange={(event) => {
                setPassword(event.target.value);
              }}
            />
            {mode === 'register' && <span className="field__hint">Не менее 8 символов</span>}
          </label>

          <button type="submit" className="button button--primary button--block" disabled={submitting}>
            {submitting ? 'Отправка...' : mode === 'login' ? 'Войти' : 'Зарегистрироваться'}
          </button>
        </form>
      </div>
    </div>
  );
}
