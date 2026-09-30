/** Общие типы данных, разделяемые всеми слоями приложения. */

/** Пользователь, как его возвращают ручки регистрации и входа. */
export interface User {
  id: number;
  login: string;
  username: string;
}

/** Текущий пользователь вместе со статистикой хранилища. */
export interface CurrentUser extends User {
  used_storage: number;
  storage_quota_bytes: number;
}

/** Папка в хранилище. */
export interface Folder {
  id: number;
  name: string;
  parent_id: number | null;
  create_date: string;
  updated_at: string;
}

/** Файл в хранилище. */
export interface StoredFile {
  id: number;
  filename: string;
  folder_id: number | null;
  size: number;
  mime_type: string;
  create_date: string;
  updated_at: string;
}

/** Элемент навигационной цепочки. У корня `id === null`. */
export interface Breadcrumb {
  id: number | null;
  name: string;
}

/** Сводка по хранилищу. */
export interface Usage {
  used_storage: number;
  storage_quota_bytes: number;
  files_count: number;
  folders_count: number;
}

/** Содержимое одной папки (или корня). */
export interface FolderListing {
  breadcrumbs: Breadcrumb[];
  folders: Folder[];
  files: StoredFile[];
}

/** Ответ ручки проверки здоровья сервиса. */
export interface HealthStatus {
  status: string;
}
