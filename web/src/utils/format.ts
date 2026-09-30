/** Форматирование размеров, дат и процентов для интерфейса. */

const numberFormatter = new Intl.NumberFormat('ru-RU', {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

const dateFormatter = new Intl.DateTimeFormat('ru-RU', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
});

const SIZE_UNITS = ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ'] as const;

/** Размер в человекочитаемом виде с одним знаком после запятой: «1,2 МБ». */
export function formatBytes(bytes: number): string {
  if (!Number.isFinite(bytes) || bytes <= 0) {
    return `0,0 ${SIZE_UNITS[0]}`;
  }

  let value = bytes;
  let unitIndex = 0;
  while (value >= 1024 && unitIndex < SIZE_UNITS.length - 1) {
    value /= 1024;
    unitIndex += 1;
  }

  return `${numberFormatter.format(value)} ${SIZE_UNITS[unitIndex]}`;
}

/** Дата в формате ru-RU; строки без часового пояса считаются временем UTC. */
export function formatDate(value: string): string {
  if (value === '') {
    return '—';
  }
  const hasZone = /(?:Z|[+-]\d{2}:?\d{2})$/.test(value);
  const date = new Date(hasZone ? value : `${value}Z`);
  if (Number.isNaN(date.getTime())) {
    return '—';
  }
  return dateFormatter.format(date);
}

/** Доля занятого места в процентах (0-100). */
export function usagePercent(used: number, quota: number): number {
  if (!Number.isFinite(quota) || quota <= 0) {
    return 0;
  }
  return Math.max(0, Math.min(100, (used / quota) * 100));
}
