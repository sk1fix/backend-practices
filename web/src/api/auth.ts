import { request } from './client';
import type { CurrentUser, User } from '../types';

export interface LoginPayload {
  login: string;
  password: string;
}

export interface RegisterPayload extends LoginPayload {
  username: string;
}

export interface AuthRequestOptions {
  /** Не перенаправлять на `/login` при 401: страница входа обрабатывает ошибку сама. */
  skipAuthRedirect?: boolean;
}

/** POST /api/auth/register — создание аккаунта. */
export function register(payload: RegisterPayload, options: AuthRequestOptions = {}): Promise<User> {
  return request<User>('/auth/register', {
    method: 'POST',
    body: payload,
    skipAuthRedirect: options.skipAuthRedirect ?? false,
  });
}

/** POST /api/auth/login — вход, сервер устанавливает httpOnly cookie. */
export function login(payload: LoginPayload, options: AuthRequestOptions = {}): Promise<User> {
  return request<User>('/auth/login', {
    method: 'POST',
    body: payload,
    skipAuthRedirect: options.skipAuthRedirect ?? false,
  });
}

/** POST /api/auth/logout — выход, сервер очищает cookie. */
export function logout(): Promise<void> {
  return request<void>('/auth/logout', { method: 'POST' });
}

/** GET /api/auth/me — текущий пользователь и статистика хранилища. */
export function getCurrentUser(options: { skipAuthRedirect?: boolean } = {}): Promise<CurrentUser> {
  return request<CurrentUser>('/auth/me', { skipAuthRedirect: options.skipAuthRedirect ?? false });
}
