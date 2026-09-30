import { Dialog } from './Dialog';

export interface ConfirmDialogProps {
  title: string;
  message: string;
  confirmLabel: string;
  busy: boolean;
  error?: string | null;
  onConfirm: () => void;
  onCancel: () => void;
}

/** Модальное окно подтверждения опасного действия. */
export function ConfirmDialog({
  title,
  message,
  confirmLabel,
  busy,
  error = null,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
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
          <button type="button" className="button button--danger" onClick={onConfirm} disabled={busy}>
            {busy ? 'Удаление...' : confirmLabel}
          </button>
        </>
      }
    >
      <p className="dialog__text">{message}</p>
      {error !== null && <p className="form__error" role="alert">{error}</p>}
    </Dialog>
  );
}
