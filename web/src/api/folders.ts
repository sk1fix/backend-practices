import { request } from './client';
import type { Folder, FolderListing } from '../types';

/**
 * GET /api/folders — содержимое папки.
 * Для корня параметр `parent_id` не передаётся вовсе.
 */
export function listFolder(parentId: number | null, signal?: AbortSignal): Promise<FolderListing> {
  const query = parentId === null ? '' : `?parent_id=${parentId}`;
  return request<FolderListing>(`/folders${query}`, { signal });
}

/** POST /api/folders — создание папки. */
export function createFolder(payload: { name: string; parent_id: number | null }): Promise<Folder> {
  return request<Folder>('/folders', { method: 'POST', body: payload });
}

/** PATCH /api/folders/{id} — переименование папки. */
export function renameFolder(id: number, name: string): Promise<Folder> {
  return request<Folder>(`/folders/${id}`, { method: 'PATCH', body: { name } });
}

/** DELETE /api/folders/{id} — рекурсивное удаление папки. */
export function deleteFolder(id: number): Promise<void> {
  return request<void>(`/folders/${id}`, { method: 'DELETE' });
}
