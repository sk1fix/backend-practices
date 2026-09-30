import { apiUrl, request } from './client';
import type { StoredFile } from '../types';

/** PATCH /api/files/{id} — переименование файла. */
export function renameFile(id: number, filename: string): Promise<StoredFile> {
  return request<StoredFile>(`/files/${id}`, { method: 'PATCH', body: { filename } });
}

/** DELETE /api/files/{id} — удаление файла. */
export function deleteFile(id: number): Promise<void> {
  return request<void>(`/files/${id}`, { method: 'DELETE' });
}

/**
 * Прямая ссылка на скачивание.
 * Cookie уходит автоматически, поэтому скачивание делается обычной ссылкой `<a href>`.
 */
export function downloadFileUrl(id: number): string {
  return apiUrl(`/files/${id}/download`);
}
