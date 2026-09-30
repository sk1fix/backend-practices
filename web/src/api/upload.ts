import { ApiError, apiUrl, buildApiError, redirectToLogin } from './client';
import type { StoredFile } from '../types';

export interface UploadFileOptions {
  file: File;
  /** Папка назначения; `null` — корень хранилища. */
  folderId: number | null;
  /** Перезаписать файл с тем же именем. */
  overwrite?: boolean;
  /** Прогресс отправки в процентах (0-100). */
  onProgress?: (percent: number) => void;
  signal?: AbortSignal;
  skipAuthRedirect?: boolean;
}

/**
 * POST /api/files/upload — загрузка файла через XMLHttpRequest.
 * XHR выбран ради реального прогресса отправки (fetch не умеет upload-progress).
 * Признак перезаписи передаётся query-параметром, файл и папка — полями multipart.
 */
export function uploadFile(options: UploadFileOptions): Promise<StoredFile> {
  const { file, folderId, overwrite = false, onProgress, signal, skipAuthRedirect = false } = options;

  return new Promise<StoredFile>((resolve, reject) => {
    const form = new FormData();
    form.append('file', file, file.name);
    if (folderId !== null) {
      form.append('folder_id', String(folderId));
    }

    // Путь считается от базового пути приложения (VITE_BASE_PATH), иначе при
    // отдаче из подкаталога запрос уходит в корень домена и nginx отдаёт 404.
    const url = apiUrl(overwrite ? '/files/upload?overwrite=true' : '/files/upload');
    const xhr = new XMLHttpRequest();
    xhr.open('POST', url, true);
    xhr.withCredentials = true;
    xhr.responseType = 'text';

    const handleAbort = () => {
      xhr.abort();
    };

    if (signal !== undefined) {
      if (signal.aborted) {
        reject(new DOMException('Загрузка отменена', 'AbortError'));
        return;
      }
      signal.addEventListener('abort', handleAbort);
    }

    const cleanup = () => {
      if (signal !== undefined) {
        signal.removeEventListener('abort', handleAbort);
      }
    };

    xhr.upload.addEventListener('progress', (event: ProgressEvent) => {
      if (onProgress === undefined) {
        return;
      }
      const total = event.lengthComputable && event.total > 0 ? event.total : file.size;
      if (total <= 0) {
        return;
      }
      onProgress(Math.max(0, Math.min(100, Math.round((event.loaded / total) * 100))));
    });

    xhr.addEventListener('load', () => {
      cleanup();
      if (xhr.status >= 200 && xhr.status < 300) {
        onProgress?.(100);
        try {
          resolve(JSON.parse(xhr.responseText) as StoredFile);
        } catch {
          reject(new ApiError(xhr.status, 'Сервер вернул неожиданный ответ при загрузке файла.'));
        }
        return;
      }
      const error = buildApiError(xhr.status, xhr.responseText);
      if (error.status === 401 && !skipAuthRedirect) {
        redirectToLogin();
      }
      reject(error);
    });

    xhr.addEventListener('error', () => {
      cleanup();
      reject(new ApiError(0, 'Не удалось загрузить файл: соединение с сервером потеряно.'));
    });

    xhr.addEventListener('timeout', () => {
      cleanup();
      reject(new ApiError(0, 'Истекло время ожидания при загрузке файла.'));
    });

    xhr.addEventListener('abort', () => {
      cleanup();
      reject(new DOMException('Загрузка отменена', 'AbortError'));
    });

    try {
      xhr.send(form);
    } catch {
      cleanup();
      reject(new ApiError(0, 'Не удалось отправить файл на сервер.'));
    }
  });
}
