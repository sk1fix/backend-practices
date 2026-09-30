import { formatBytes } from '../utils/format';

export type UploadStatus = 'uploading' | 'done' | 'error' | 'conflict' | 'canceled';

export interface UploadEntry {
  id: number;
  file: File;
  progress: number;
  status: UploadStatus;
  message: string | null;
}

export interface UploadListProps {
  entries: UploadEntry[];
  onCancel: (entry: UploadEntry) => void;
  onOverwrite: (entry: UploadEntry) => void;
  onRetry: (entry: UploadEntry) => void;
  onDismiss: (entry: UploadEntry) => void;
  onClearFinished: () => void;
}

const STATUS_LABELS: Record<UploadStatus, string> = {
  uploading: 'Загрузка',
  done: 'Загружен',
  error: 'Ошибка',
  conflict: 'Конфликт имени',
  canceled: 'Отменено',
};

/** Список загружаемых файлов с прогрессом и действиями. */
export function UploadList({
  entries,
  onCancel,
  onOverwrite,
  onRetry,
  onDismiss,
  onClearFinished,
}: UploadListProps) {
  if (entries.length === 0) {
    return null;
  }

  const finishedCount = entries.filter((entry) => entry.status !== 'uploading').length;

  return (
    <section className="uploads" aria-label="Загрузка файлов">
      <div className="uploads__header">
        <h2 className="section-title">Загрузка ({entries.length})</h2>
        {finishedCount > 0 && (
          <button type="button" className="link-button" onClick={onClearFinished}>
            Убрать завершённые
          </button>
        )}
      </div>

      <ul className="uploads__list">
        {entries.map((entry) => (
          <li className="upload" key={entry.id}>
            <div className="upload__row">
              <span className="upload__name" title={entry.file.name}>
                {entry.file.name}
              </span>
              <span className="upload__size">{formatBytes(entry.file.size)}</span>
              <span className={`upload__status upload__status--${entry.status}`}>
                {entry.status === 'uploading' ? `${STATUS_LABELS[entry.status]} ${entry.progress}%` : STATUS_LABELS[entry.status]}
              </span>
            </div>

            <div className="progress" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={entry.progress}>
              <div
                className={`progress__bar progress__bar--${entry.status}`}
                style={{ width: `${entry.progress}%` }}
              />
            </div>

            {entry.message !== null && <p className="upload__message">{entry.message}</p>}

            <div className="upload__actions">
              {entry.status === 'uploading' && (
                <button type="button" className="link-button" onClick={() => onCancel(entry)}>
                  Отменить
                </button>
              )}
              {entry.status === 'conflict' && (
                <>
                  <button type="button" className="link-button" onClick={() => onOverwrite(entry)}>
                    Перезаписать
                  </button>
                  <button type="button" className="link-button" onClick={() => onDismiss(entry)}>
                    Пропустить
                  </button>
                </>
              )}
              {entry.status === 'error' && (
                <>
                  <button type="button" className="link-button" onClick={() => onRetry(entry)}>
                    Повторить
                  </button>
                  <button type="button" className="link-button" onClick={() => onDismiss(entry)}>
                    Убрать
                  </button>
                </>
              )}
              {(entry.status === 'done' || entry.status === 'canceled') && (
                <button type="button" className="link-button" onClick={() => onDismiss(entry)}>
                  Убрать
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
