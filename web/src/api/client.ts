/**
 * Тонкая обёртка над fetch для всего API.
 *
 * Особенности:
 *  - все запросы уходят с `credentials: 'include'` (авторизация — httpOnly cookie);
 *  - тело ошибки `{ "detail": ... }` превращается в {@link ApiError} с русским текстом;
 *  - любой ответ 401 (кроме страницы входа) переводит пользователя на `/login`.
 */

const API_PREFIX = '/api';
const LOGIN_PATH = '/login';

/** Ошибка запроса к API: HTTP-статус плюс готовое для показа сообщение. */
export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE';
  body?: unknown;
  /** Не перенаправлять на `/login` при 401 (нужно самой странице входа). */
  skipAuthRedirect?: boolean;
  signal?: AbortSignal;
}

/** Один элемент массива `detail` у ошибок валидации FastAPI (422). */
interface ValidationIssue {
  loc?: (string | number)[];
  msg?: string;
  type?: string;
  input?: unknown;
}

const FALLBACK_MESSAGES: Record<number, string> = {
  400: 'Некорректный запрос.',
  401: 'Требуется вход в систему.',
  403: 'Доступ запрещён.',
  404: 'Запрашиваемый объект не найден.',
  408: 'Сервер не дождался запроса. Попробуйте ещё раз.',
  409: 'Объект с таким именем уже существует.',
  413: 'Недостаточно места в хранилище или файл слишком большой.',
  422: 'Проверьте правильность заполнения полей.',
  429: 'Слишком много запросов. Попробуйте позже.',
  500: 'Внутренняя ошибка сервера. Попробуйте позже.',
  502: 'Сервер недоступен. Попробуйте позже.',
  503: 'Сервис временно недоступен. Попробуйте позже.',
};

function isValidationIssue(value: unknown): value is ValidationIssue {
  return typeof value === 'object' && value !== null;
}

/** Путь до поля из `loc`: ['body', 'folder_id'] -> 'folder_id'. */
function fieldPath(loc: (string | number)[] | undefined): string {
  if (loc === undefined || loc.length === 0) {
    return '';
  }
  return loc
    .filter((part) => part !== 'body' && part !== 'query' && part !== 'path')
    .join('.');
}

/** Превращает массив ошибок валидации FastAPI в одно понятное сообщение. */
function describeIssues(issues: ValidationIssue[]): string {
  const parts = issues.slice(0, 4).map((issue) => {
    const path = fieldPath(issue.loc);
    const text = typeof issue.msg === 'string' && issue.msg.trim() !== '' ? issue.msg.trim() : 'недопустимое значение';
    return path === '' ? text : `${path}: ${text}`;
  });

  const unique = Array.from(new Set(parts));
  return `Некорректные данные. ${unique.join('; ')}.`;
}

function extractDetail(payload: unknown): unknown {
  if (typeof payload === 'object' && payload !== null && 'detail' in payload) {
    // После оператора `in` TypeScript выводит тип свойства как `unknown`.
    return payload.detail;
  }
  return undefined;
}

/**
 * Собирает {@link ApiError} из сырого тела ответа.
 * Используется и обычными запросами, и загрузкой файлов через XMLHttpRequest.
 */
export function buildApiError(status: number, rawBody: string): ApiError {
  let detail: unknown;

  if (rawBody.trim() !== '') {
    try {
      detail = extractDetail(JSON.parse(rawBody));
    } catch {
      detail = undefined;
    }
  }

  if (typeof detail === 'string' && detail.trim() !== '') {
    return new ApiError(status, detail);
  }

  if (Array.isArray(detail)) {
    const issues = detail.filter(isValidationIssue);
    if (issues.length > 0) {
      return new ApiError(status, describeIssues(issues));
    }
  }

  return new ApiError(status, FALLBACK_MESSAGES[status] ?? `Не удалось выполнить запрос (код ${status}).`);
}

/** Отправляет пользователя на страницу входа (однократно, вне самой страницы входа). */
export function redirectToLogin(): void {
  if (typeof window === 'undefined') {
    return;
  }
  if (window.location.pathname === LOGIN_PATH) {
    return;
  }
  window.location.assign(LOGIN_PATH);
}

/** Прерван ли запрос через AbortController. */
export function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError';
}

/** Текст ошибки для показа пользователю. */
export function errorMessage(error: unknown, fallback = 'Непредвиденная ошибка. Попробуйте ещё раз.'): string {
  if (error instanceof ApiError) {
    return error.message;
  }
  return fallback;
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, skipAuthRedirect = false, signal } = options;

  const headers: Record<string, string> = { Accept: 'application/json' };
  let payload: BodyInit | undefined;

  if (body !== undefined) {
    if (body instanceof FormData) {
      payload = body;
    } else {
      headers['Content-Type'] = 'application/json';
      payload = JSON.stringify(body);
    }
  }

  let response: Response;
  try {
    response = await fetch(`${API_PREFIX}${path}`, {
      method,
      headers,
      body: payload,
      credentials: 'include',
      signal,
    });
  } catch (error) {
    if (isAbortError(error)) {
      throw error;
    }
    throw new ApiError(0, 'Не удалось соединиться с сервером. Проверьте подключение к сети.');
  }

  if (!response.ok) {
    const apiError = buildApiError(response.status, await response.text());
    if (apiError.status === 401 && !skipAuthRedirect) {
      redirectToLogin();
    }
    throw apiError;
  }

  if (response.status === 204) {
    return undefined as unknown as T;
  }

  const text = await response.text();
  if (text === '') {
    return undefined as unknown as T;
  }

  try {
    return JSON.parse(text) as T;
  } catch {
    throw new ApiError(response.status, 'Сервер вернул неожиданный ответ.');
  }
}
