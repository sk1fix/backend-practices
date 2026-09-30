import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { CloseIcon } from './Icons';

export type ToastKind = 'error' | 'success' | 'info';

export interface Toast {
  id: number;
  kind: ToastKind;
  message: string;
}

export interface ToastApi {
  push: (kind: ToastKind, message: string) => void;
  dismiss: (id: number) => void;
}

const ToastContext = createContext<ToastApi | null>(null);

const TOAST_TIMEOUT_MS = 7000;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const nextId = useRef(0);
  const timers = useRef(new Map<number, number>());

  const dismiss = useCallback((id: number) => {
    const timer = timers.current.get(id);
    if (timer !== undefined) {
      window.clearTimeout(timer);
      timers.current.delete(id);
    }
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  const push = useCallback(
    (kind: ToastKind, message: string) => {
      const id = (nextId.current += 1);
      setToasts((current) => [...current, { id, kind, message }]);
      const timer = window.setTimeout(() => {
        dismiss(id);
      }, TOAST_TIMEOUT_MS);
      timers.current.set(id, timer);
    },
    [dismiss],
  );

  useEffect(() => {
    const pending = timers.current;
    return () => {
      pending.forEach((timer) => {
        window.clearTimeout(timer);
      });
      pending.clear();
    };
  }, []);

  const api = useMemo<ToastApi>(() => ({ push, dismiss }), [push, dismiss]);

  return (
    <ToastContext.Provider value={api}>
      {children}
      <Toasts toasts={toasts} onDismiss={dismiss} />
    </ToastContext.Provider>
  );
}

export function useToasts(): ToastApi {
  const context = useContext(ToastContext);
  if (context === null) {
    throw new Error('useToasts должен вызываться внутри ToastProvider.');
  }
  return context;
}

export interface ToastsProps {
  toasts: Toast[];
  onDismiss: (id: number) => void;
}

/** Список всплывающих уведомлений в правом нижнем углу. */
export function Toasts({ toasts, onDismiss }: ToastsProps) {
  if (toasts.length === 0) {
    return null;
  }

  return (
    <div className="toasts" role="status" aria-live="polite">
      {toasts.map((toast) => (
        <div className={`toast toast--${toast.kind}`} key={toast.id}>
          <span className="toast__message">{toast.message}</span>
          <button
            type="button"
            className="icon-button icon-button--small"
            onClick={() => {
              onDismiss(toast.id);
            }}
            aria-label="Закрыть уведомление"
            title="Закрыть"
          >
            <CloseIcon width={16} height={16} />
          </button>
        </div>
      ))}
    </div>
  );
}
