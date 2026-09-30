import type { Folder } from '../types';
import { formatDate } from '../utils/format';
import { FolderIcon, RenameIcon, TrashIcon } from './Icons';

export interface FolderRowProps {
  folder: Folder;
  busy: boolean;
  onOpen: (folder: Folder) => void;
  onRename: (folder: Folder) => void;
  onDelete: (folder: Folder) => void;
}

/** Строка списка папок. */
export function FolderRow({ folder, busy, onOpen, onRename, onDelete }: FolderRowProps) {
  return (
    <li className="row">
      <span className="row__icon row__icon--folder" aria-hidden="true">
        <FolderIcon />
      </span>

      <button
        type="button"
        className="row__name"
        onClick={() => {
          onOpen(folder);
        }}
        title={folder.name}
      >
        {folder.name}
      </button>

      <span className="row__meta row__meta--kind">Папка</span>
      <span className="row__meta row__meta--size" />
      <span className="row__meta row__meta--date" title="Дата изменения">
        {formatDate(folder.updated_at)}
      </span>

      <span className="row__actions">
        <button
          type="button"
          className="icon-button"
          disabled={busy}
          onClick={() => {
            onRename(folder);
          }}
          aria-label={`Переименовать папку ${folder.name}`}
          title="Переименовать"
        >
          <RenameIcon width={18} height={18} />
        </button>
        <button
          type="button"
          className="icon-button icon-button--danger"
          disabled={busy}
          onClick={() => {
            onDelete(folder);
          }}
          aria-label={`Удалить папку ${folder.name}`}
          title="Удалить"
        >
          <TrashIcon width={18} height={18} />
        </button>
      </span>
    </li>
  );
}
