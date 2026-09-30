import { useEffect, useId, useRef, useState, type FormEvent } from 'react';
import { Dialog } from './Dialog';

export interface RenameDialogProps {
  title: string;
  fieldLabel: string;
  initialValue: string;
  busy: boolean;
  /** Ошибка, пришедшая от сервера. */
  error: string | null;
  validate: (value: string) => string | null;
  onSubmit: (value: string) => void;
  onCancel: () => void;
}

/** Модальное окно переименования папки или файла. */
export function RenameDialog({
  title,
  fieldLabel,
  initialValue,
  busy,
  error,
  validate,
  onSubmit,
  onCancel,
}: RenameDialogProps) {
  const [value, setValue] = useState(initialValue);
  const [localError, setLocalError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const inputId = useId();

  useEffect(() => {
    const input = inputRef.current;
    if (input === null) {
      return;
    }
    input.focus();
    input.select();
  }, []);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const validationError = validate(value);
    if (validationError !== null) {
      setLocalError(validationError);
      return;
    }
    setLocalError(null);
    onSubmit(value.trim());
  };

  const shownError = localError ?? error;

  return (
    <Dialog
      title={title}
      onClose={onCancel}
      closable={!busy}
      footer={
        <>
          <button type="button" className="button" onClick={onCancel} disabled={busy}>
            Отмена
          </button>
          <button type="submit" form="rename-form" className="button button--primary" disabled={busy}>
            {busy ? 'Сохранение...' : 'Сохранить'}
          </button>
        </>
      }
    >
      <form id="rename-form" className="form" onSubmit={handleSubmit} noValidate>
        <label className="field" htmlFor={inputId}>
          <span className="field__label">{fieldLabel}</span>
          <input
            id={inputId}
            ref={inputRef}
            className="input"
            type="text"
            value={value}
            maxLength={255}
            autoComplete="off"
            disabled={busy}
            onChange={(event) => {
              setValue(event.target.value);
              setLocalError(null);
            }}
          />
        </label>
        {shownError !== null && <p className="form__error" role="alert">{shownError}</p>}
      </form>
    </Dialog>
  );
}
