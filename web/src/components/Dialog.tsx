import { useEffect, type ReactNode } from 'react';
import { CloseIcon } from './Icons';

export interface DialogProps {
  title: string;
  onClose: () => void;
  children: ReactNode;
  footer: ReactNode;
  closable?: boolean;
}

/** Общая оболочка модального окна: затемнение, заголовок, содержимое, кнопки. */
export function Dialog({ title, onClose, children, footer, closable = true }: DialogProps) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && closable) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [closable, onClose]);

  return (
    <div
      className="dialog-overlay"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget && closable) {
          onClose();
        }
      }}
    >
      <div className="dialog" role="dialog" aria-modal="true" aria-label={title}>
        <div className="dialog__header">
          <h2 className="dialog__title">{title}</h2>
          <button
            type="button"
            className="icon-button"
            onClick={onClose}
            disabled={!closable}
            aria-label="Закрыть окно"
            title="Закрыть"
          >
            <CloseIcon width={18} height={18} />
          </button>
        </div>
        <div className="dialog__body">{children}</div>
        <div className="dialog__footer">{footer}</div>
      </div>
    </div>
  );
}
