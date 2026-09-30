/**
 * Клиентская проверка полей.
 * Правила совпадают с ограничениями бэкенда, чтобы не гонять заведомо
 * некорректные данные на сервер.
 */

export const NAME_MAX_LENGTH = 255;
export const PASSWORD_MIN_LENGTH = 8;

/** Возвращает текст ошибки или `null`, если имя папки/файла корректно. */
export function validateEntryName(raw: string): string | null {
  const name = raw.trim();
  if (name === '') {
    return 'Имя не может быть пустым.';
  }
  if (name.length > NAME_MAX_LENGTH) {
    return `Имя не должно превышать ${NAME_MAX_LENGTH} символов.`;
  }
  if (name === '.' || name === '..') {
    return 'Имена «.» и «..» использовать нельзя.';
  }
  if (name.includes('/')) {
    return 'Имя не может содержать символ «/».';
  }
  if (name.includes('\\')) {
    return 'Имя не может содержать символ «\\».';
  }
  return null;
}

export function validateLogin(login: string): string | null {
  const value = login.trim();
  if (value === '') {
    return 'Введите логин.';
  }
  if (value.includes(' ')) {
    return 'Логин не может содержать пробелы.';
  }
  return null;
}

export function validatePassword(password: string): string | null {
  if (password === '') {
    return 'Введите пароль.';
  }
  if (password.length < PASSWORD_MIN_LENGTH) {
    return `Пароль должен содержать не менее ${PASSWORD_MIN_LENGTH} символов.`;
  }
  return null;
}

export function validateUsername(username: string): string | null {
  if (username.trim() === '') {
    return 'Введите имя пользователя.';
  }
  return null;
}
