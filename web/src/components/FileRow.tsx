import { downloadFileUrl } from '../api/files';
import type { StoredFile } from '../types';
import { formatBytes, formatDate } from '../utils/format';
import { DownloadIcon, FileIcon, RenameIcon, TrashIcon } from './Icons';

export interface FileRowProps {
  file: StoredFile;
  busy: boolean;
  onRename: (file: StoredFile) => void;
  onDelete: (file: StoredFile) => void;
}

/** Строка списка файлов. */
export function FileRow({ file, busy, onRename, onDelete }: FileRowProps) {
  return (
    <li className="row">
      <span className="row__icon row__icon--file" aria-hidden="true">
        <FileIcon />
      </span>

      <a
        className="row__name"
        href={downloadFileUrl(file.id)}
        title={`Скачать ${file.filename}`}
        download={file.filename}
      >
        {file.filename}
      </a>

      <span className="row__meta row__meta--kind" title={file.mime_type}>
        {file.mime_type === '' ? 'Файл' : file.mime_type}
      </span>
      <span className="row__meta row__meta--size">{formatBytes(file.size)}</span>
      <span className="row__meta row__meta--date" title="Дата изменения">
        {formatDate(file.updated_at)}
      </span>

      <span className="row__actions">
        <a
          className="icon-button"
          href={downloadFileUrl(file.id)}
          download={file.filename}
          aria-label={`Скачать файл ${file.filename}`}
          title="Скачать"
        >
          <DownloadIcon width={18} height={18} />
        </a>
        <button
          type="button"
          className="icon-button"
          disabled={busy}
          onClick={() => {
            onRename(file);
          }}
          aria-label={`Переименовать файл ${file.filename}`}
          title="Переименовать"
        >
          <RenameIcon width={18} height={18} />
        </button>
        <button
          type="button"
          className="icon-button icon-button--danger"
          disabled={busy}
          onClick={() => {
            onDelete(file);
          }}
          aria-label={`Удалить файл ${file.filename}`}
          title="Удалить"
        >
          <TrashIcon width={18} height={18} />
        </button>
      </span>
    </li>
  );
}
