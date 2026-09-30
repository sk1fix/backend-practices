import type { CurrentUser, Usage } from '../types';
import { LogoutIcon, StorageIcon } from './Icons';
import { UsageBar } from './UsageBar';

export interface AppHeaderProps {
  user: CurrentUser | null;
  usage: Usage | null;
  loggingOut: boolean;
  onLogout: () => void;
}

/** Шапка приложения: пользователь, занятое место, выход. */
export function AppHeader({ user, usage, loggingOut, onLogout }: AppHeaderProps) {
  return (
    <header className="app-header">
      <div className="app-header__brand">
        <span className="app-header__logo" aria-hidden="true">
          <StorageIcon width={22} height={22} />
        </span>
        <span className="app-header__title">Облачное хранилище</span>
      </div>

      {usage !== null && (
        <div className="app-header__usage">
          <UsageBar used={usage.used_storage} quota={usage.storage_quota_bytes} />
        </div>
      )}

      <div className="app-header__user">
        {user !== null && (
          <span className="app-header__user-info">
            <span className="app-header__username">{user.username}</span>
            <span className="app-header__login">{user.login}</span>
          </span>
        )}
        <button type="button" className="button button--ghost" onClick={onLogout} disabled={loggingOut}>
          <LogoutIcon width={18} height={18} />
          {loggingOut ? 'Выход...' : 'Выйти'}
        </button>
      </div>
    </header>
  );
}
