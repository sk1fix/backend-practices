import { useCallback, useEffect, useMemo, useRef, useState, type FormEvent } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

import {
  ApiError,
  createFolder,
  deleteFile,
  deleteFolder,
  errorMessage,
  getCurrentUser,
  getUsage,
  isAbortError,
  listFolder,
  logout,
  renameFile,
  renameFolder,
  uploadFile,
} from '../api';
import { AppHeader } from '../components/AppHeader';
import { Breadcrumbs } from '../components/Breadcrumbs';
import { ConfirmDialog } from '../components/ConfirmDialog';
import { FileRow } from '../components/FileRow';
import { FolderRow } from '../components/FolderRow';
import { FolderPlusIcon } from '../components/Icons';
import { RenameDialog } from '../components/RenameDialog';
import { UploadDropzone } from '../components/UploadDropzone';
import { UploadList, type UploadEntry } from '../components/UploadList';
import { useToasts } from '../components/Toasts';
import { useFileDrop } from '../hooks/useFileDrop';
import type { CurrentUser, Folder, FolderListing, StoredFile, Usage } from '../types';
import { validateEntryName } from '../utils/validation';

interface MutationTarget {
  kind: 'folder' | 'file';
  id: number;
  name: string;
}

/** Основная страница: содержимое корня или выбранной папки. */
export function FilesPage() {
  const params = useParams();
  const navigate = useNavigate();
  const { push } = useToasts();

  const rawFolderId = params.id;
  const parsedFolderId = rawFolderId === undefined ? null : Number(rawFolderId);
  const folderIdIsValid =
    parsedFolderId === null || (Number.isSafeInteger(parsedFolderId) && parsedFolderId > 0);
  const folderId = folderIdIsValid ? parsedFolderId : null;

  const [listing, setListing] = useState<FolderListing | null>(null);
  const [listingError, setListingError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [reloadKey, setReloadKey] = useState(0);

  const [user, setUser] = useState<CurrentUser | null>(null);
  const [usage, setUsage] = useState<Usage | null>(null);
  const [loggingOut, setLoggingOut] = useState(false);

  const [newFolderName, setNewFolderName] = useState('');
  const [creatingFolder, setCreatingFolder] = useState(false);

  const [renameTarget, setRenameTarget] = useState<MutationTarget | null>(null);
  const [renameBusy, setRenameBusy] = useState(false);
  const [renameError, setRenameError] = useState<string | null>(null);

  const [deleteTarget, setDeleteTarget] = useState<MutationTarget | null>(null);
  const [deleteBusy, setDeleteBusy] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const [uploads, setUploads] = useState<UploadEntry[]>([]);
  const uploadIdRef = useRef(0);
  const queueRef = useRef<Promise<void>>(Promise.resolve());
  const controllersRef = useRef(new Map<number, AbortController>());
  const cancelledUploadsRef = useRef(new Set<number>());

  const refresh = useCallback(() => {
    setReloadKey((key) => key + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;
    getCurrentUser()
      .then((current) => {
        if (!cancelled) {
          setUser(current);
        }
      })
      .catch(() => {
        // Ответ 401 уже обработан централизованно в api/client.ts.
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!folderIdIsValid) {
      setLoading(false);
      return;
    }

    const controller = new AbortController();
    setLoading(true);
    setListingError(null);

    listFolder(folderId, controller.signal)
      .then((data) => {
        setListing(data);
      })
      .catch((error: unknown) => {
        if (isAbortError(error)) {
          return;
        }
        setListingError(errorMessage(error));
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      });

    return () => {
      controller.abort();
    };
  }, [folderId, folderIdIsValid, reloadKey]);

  useEffect(() => {
    const controller = new AbortController();
    getUsage(controller.signal)
      .then((data) => {
        setUsage(data);
      })
      .catch(() => {
        // Сводка не критична: шапка просто покажет прежние значения.
      });
    return () => {
      controller.abort();
    };
  }, [reloadKey]);

  useEffect(() => {
    const controllers = controllersRef.current;
    return () => {
      controllers.forEach((controller) => {
        controller.abort();
      });
      controllers.clear();
    };
  }, []);

  const patchUpload = useCallback((id: number, patch: Partial<UploadEntry>) => {
    setUploads((current) => current.map((entry) => (entry.id === id ? { ...entry, ...patch } : entry)));
  }, []);

  const runUpload = useCallback(
    async (entry: UploadEntry, overwrite: boolean) => {
      if (cancelledUploadsRef.current.has(entry.id)) {
        patchUpload(entry.id, { status: 'canceled', message: 'Загрузка отменена.' });
        return;
      }

      const controller = new AbortController();
      controllersRef.current.set(entry.id, controller);
      patchUpload(entry.id, { status: 'uploading', progress: 0, message: null });

      try {
        await uploadFile({
          file: entry.file,
          folderId,
          overwrite,
          signal: controller.signal,
          onProgress: (percent) => {
            patchUpload(entry.id, { progress: percent });
          },
        });
        patchUpload(entry.id, { status: 'done', progress: 100, message: null });
        push('success', `Файл «${entry.file.name}» загружен.`);
        refresh();
      } catch (error: unknown) {
        if (isAbortError(error)) {
          patchUpload(entry.id, { status: 'canceled', message: 'Загрузка отменена.' });
        } else if (error instanceof ApiError && error.status === 409) {
          patchUpload(entry.id, { status: 'conflict', message: `${error.message} Заменить файл?` });
        } else {
          patchUpload(entry.id, { status: 'error', progress: 0, message: errorMessage(error) });
        }
      } finally {
        controllersRef.current.delete(entry.id);
      }
    },
    [folderId, patchUpload, push, refresh],
  );

  const enqueueUploads = useCallback(
    (files: File[]) => {
      if (files.length === 0) {
        return;
      }

      const entries: UploadEntry[] = files.map((file) => {
        uploadIdRef.current += 1;
        return { id: uploadIdRef.current, file, progress: 0, status: 'uploading', message: null };
      });

      setUploads((current) => [...entries, ...current]);

      queueRef.current = queueRef.current.then(async () => {
        for (const entry of entries) {
          await runUpload(entry, false);
        }
      });
    },
    [runUpload],
  );

  const handleOverwrite = useCallback(
    (entry: UploadEntry) => {
      cancelledUploadsRef.current.delete(entry.id);
      queueRef.current = queueRef.current.then(() => runUpload(entry, true));
    },
    [runUpload],
  );

  const handleRetryUpload = useCallback(
    (entry: UploadEntry) => {
      cancelledUploadsRef.current.delete(entry.id);
      queueRef.current = queueRef.current.then(() => runUpload(entry, false));
    },
    [runUpload],
  );

  const handleCancelUpload = useCallback(
    (entry: UploadEntry) => {
      cancelledUploadsRef.current.add(entry.id);
      const controller = controllersRef.current.get(entry.id);
      if (controller !== undefined) {
        controller.abort();
      } else {
        patchUpload(entry.id, { status: 'canceled', message: 'Загрузка отменена.' });
      }
    },
    [patchUpload],
  );

  const handleDismissUpload = useCallback((entry: UploadEntry) => {
    cancelledUploadsRef.current.delete(entry.id);
    setUploads((current) => current.filter((item) => item.id !== entry.id));
  }, []);

  const handleClearFinishedUploads = useCallback(() => {
    setUploads((current) => current.filter((item) => item.status === 'uploading'));
  }, []);

  const dragging = useFileDrop(enqueueUploads);

  const handleCreateFolder = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const validationError = validateEntryName(newFolderName);
    if (validationError !== null) {
      push('error', validationError);
      return;
    }

    setCreatingFolder(true);
    try {
      await createFolder({ name: newFolderName.trim(), parent_id: folderId });
      setNewFolderName('');
      push('success', 'Папка создана.');
      refresh();
    } catch (error: unknown) {
      push('error', errorMessage(error));
    } finally {
      setCreatingFolder(false);
    }
  };

  const handleRenameSubmit = async (value: string) => {
    if (renameTarget === null) {
      return;
    }

    setRenameBusy(true);
    setRenameError(null);

    try {
      if (renameTarget.kind === 'folder') {
        await renameFolder(renameTarget.id, value);
      } else {
        await renameFile(renameTarget.id, value);
      }
      setRenameTarget(null);
      push('success', renameTarget.kind === 'folder' ? 'Папка переименована.' : 'Файл переименован.');
      refresh();
    } catch (error: unknown) {
      setRenameError(errorMessage(error));
    } finally {
      setRenameBusy(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (deleteTarget === null) {
      return;
    }

    setDeleteBusy(true);
    setDeleteError(null);

    try {
      if (deleteTarget.kind === 'folder') {
        await deleteFolder(deleteTarget.id);
      } else {
        await deleteFile(deleteTarget.id);
      }
      setDeleteTarget(null);
      push('success', deleteTarget.kind === 'folder' ? 'Папка удалена.' : 'Файл удалён.');
      refresh();
    } catch (error: unknown) {
      setDeleteError(errorMessage(error));
    } finally {
      setDeleteBusy(false);
    }
  };

  const handleOpenFolder = (folder: Folder) => {
    navigate(`/files/folder/${folder.id}`);
  };

  const handleLogout = async () => {
    setLoggingOut(true);
    try {
      await logout();
    } catch {
      // Выход из системы выполняется в любом случае.
    } finally {
      setLoggingOut(false);
    }
    navigate('/login', { replace: true });
  };

  const isEmpty = listing !== null && listing.folders.length === 0 && listing.files.length === 0;
  const mutationBusy = creatingFolder || renameBusy || deleteBusy;

  const countsLabel = useMemo(() => {
    if (listing === null) {
      return '';
    }
    return `Папок: ${listing.folders.length} · Файлов: ${listing.files.length}`;
  }, [listing]);

  if (!folderIdIsValid) {
    return (
      <div className="app">
        <main className="app-main">
          <div className="state state--error" role="alert">
            <p>Адрес папки указан неверно.</p>
            <Link className="button" to="/files">
              Вернуться в корень хранилища
            </Link>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="app">
      <AppHeader user={user} usage={usage} loggingOut={loggingOut} onLogout={handleLogout} />

      <main className="app-main">
        <Breadcrumbs items={listing?.breadcrumbs ?? []} />

        <div className="toolbar">
          <form className="toolbar__form" onSubmit={handleCreateFolder}>
            <input
              className="input"
              type="text"
              value={newFolderName}
              placeholder="Имя новой папки"
              aria-label="Имя новой папки"
              maxLength={255}
              disabled={creatingFolder}
              onChange={(event) => {
                setNewFolderName(event.target.value);
              }}
            />
            <button type="submit" className="button button--primary" disabled={creatingFolder}>
              <FolderPlusIcon width={18} height={18} />
              {creatingFolder ? 'Создание...' : 'Создать папку'}
            </button>
          </form>

          <button
            type="button"
            className="button"
            onClick={refresh}
            disabled={loading}
            title="Обновить список"
          >
            Обновить
          </button>
        </div>

        <UploadDropzone dragging={dragging} onFiles={enqueueUploads} />

        <UploadList
          entries={uploads}
          onCancel={handleCancelUpload}
          onOverwrite={handleOverwrite}
          onRetry={handleRetryUpload}
          onDismiss={handleDismissUpload}
          onClearFinished={handleClearFinishedUploads}
        />

        <section className="listing" aria-label="Содержимое папки">
          <div className="listing__header">
            <h2 className="section-title">Содержимое</h2>
            {listing !== null && <span className="listing__count">{countsLabel}</span>}
          </div>

          {loading && <p className="state state--loading">Загрузка содержимого...</p>}

          {!loading && listingError !== null && (
            <div className="state state--error" role="alert">
              <p>{listingError}</p>
              <button type="button" className="button" onClick={refresh}>
                Повторить
              </button>
            </div>
          )}

          {!loading && listingError === null && isEmpty && (
            <div className="state state--empty">
              <p className="state__title">Здесь пока ничего нет</p>
              <p className="state__hint">Создайте папку или загрузите первый файл.</p>
            </div>
          )}

          {!loading && listingError === null && listing !== null && !isEmpty && (
            <ul className="rows">
              {listing.folders.map((folder) => (
                <FolderRow
                  key={`folder-${folder.id}`}
                  folder={folder}
                  busy={mutationBusy}
                  onOpen={handleOpenFolder}
                  onRename={(target) => {
                    setRenameError(null);
                    setRenameTarget({ kind: 'folder', id: target.id, name: target.name });
                  }}
                  onDelete={(target) => {
                    setDeleteError(null);
                    setDeleteTarget({ kind: 'folder', id: target.id, name: target.name });
                  }}
                />
              ))}

              {listing.files.map((file: StoredFile) => (
                <FileRow
                  key={`file-${file.id}`}
                  file={file}
                  busy={mutationBusy}
                  onRename={(target) => {
                    setRenameError(null);
                    setRenameTarget({ kind: 'file', id: target.id, name: target.filename });
                  }}
                  onDelete={(target) => {
                    setDeleteError(null);
                    setDeleteTarget({ kind: 'file', id: target.id, name: target.filename });
                  }}
                />
              ))}
            </ul>
          )}
        </section>
      </main>

      {dragging && (
        <div className="drop-overlay" aria-hidden="true">
          <span className="drop-overlay__text">Отпустите файлы, чтобы загрузить их в текущую папку</span>
        </div>
      )}

      {renameTarget !== null && (
        <RenameDialog
          key={`rename-${renameTarget.kind}-${renameTarget.id}`}
          title={renameTarget.kind === 'folder' ? 'Переименование папки' : 'Переименование файла'}
          fieldLabel={renameTarget.kind === 'folder' ? 'Новое имя папки' : 'Новое имя файла'}
          initialValue={renameTarget.name}
          busy={renameBusy}
          error={renameError}
          validate={validateEntryName}
          onSubmit={handleRenameSubmit}
          onCancel={() => {
            setRenameTarget(null);
            setRenameError(null);
          }}
        />
      )}

      {deleteTarget !== null && (
        <ConfirmDialog
          title={deleteTarget.kind === 'folder' ? 'Удаление папки' : 'Удаление файла'}
          message={
            deleteTarget.kind === 'folder'
              ? `Папка «${deleteTarget.name}» будет удалена вместе со всеми вложенными папками и файлами. Это действие нельзя отменить.`
              : `Файл «${deleteTarget.name}» будет удалён безвозвратно.`
          }
          confirmLabel="Удалить"
          busy={deleteBusy}
          error={deleteError}
          onConfirm={handleDeleteConfirm}
          onCancel={() => {
            setDeleteTarget(null);
            setDeleteError(null);
          }}
        />
      )}
    </div>
  );
}
