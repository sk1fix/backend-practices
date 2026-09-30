import { useId, useRef } from 'react';
import { UploadIcon } from './Icons';

export interface UploadDropzoneProps {
  /** Пользователь держит файлы над страницей. */
  dragging: boolean;
  disabled?: boolean;
  onFiles: (files: File[]) => void;
}

/** Зона загрузки: выбор файлов кнопкой и подсказка про перетаскивание. */
export function UploadDropzone({ dragging, disabled = false, onFiles }: UploadDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const inputId = useId();
  const className = ['dropzone', dragging ? 'dropzone--active' : '', disabled ? 'dropzone--disabled' : '']
    .filter((part) => part !== '')
    .join(' ');

  return (
    <section className={className} aria-label="Загрузка файлов">
      <span className="dropzone__icon" aria-hidden="true">
        <UploadIcon width={28} height={28} />
      </span>
      <p className="dropzone__title">Перетащите файлы в это окно</p>
      <p className="dropzone__hint">Поддерживается загрузка нескольких файлов одновременно</p>

      <input
        id={inputId}
        ref={inputRef}
        className="visually-hidden"
        type="file"
        multiple
        disabled={disabled}
        onChange={(event) => {
          const selected = event.target.files;
          if (selected !== null && selected.length > 0) {
            onFiles(Array.from(selected));
          }
          event.target.value = '';
        }}
      />

      <button
        type="button"
        className="button button--primary"
        disabled={disabled}
        onClick={() => {
          inputRef.current?.click();
        }}
      >
        Выбрать файлы
      </button>
    </section>
  );
}
