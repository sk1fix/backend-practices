import { useEffect, useRef, useState } from 'react';

function isFileDrag(event: DragEvent): boolean {
  const types = event.dataTransfer?.types;
  return types !== undefined && Array.from(types).indexOf('Files') !== -1;
}

/**
 * Перетаскивание файлов на любое место страницы.
 * Возвращает признак того, что пользователь сейчас держит файлы над окном.
 */
export function useFileDrop(onFiles: (files: File[]) => void): boolean {
  const [dragging, setDragging] = useState(false);
  const depth = useRef(0);

  useEffect(() => {
    const handleDragEnter = (event: DragEvent) => {
      if (!isFileDrag(event)) {
        return;
      }
      depth.current += 1;
      setDragging(true);
    };

    const handleDragOver = (event: DragEvent) => {
      if (!isFileDrag(event)) {
        return;
      }
      event.preventDefault();
      if (event.dataTransfer !== null) {
        event.dataTransfer.dropEffect = 'copy';
      }
    };

    const handleDragLeave = (event: DragEvent) => {
      if (!isFileDrag(event)) {
        return;
      }
      depth.current = Math.max(0, depth.current - 1);
      if (depth.current === 0) {
        setDragging(false);
      }
    };

    const handleDrop = (event: DragEvent) => {
      if (!isFileDrag(event)) {
        return;
      }
      event.preventDefault();
      depth.current = 0;
      setDragging(false);
      const files = event.dataTransfer === null ? [] : Array.from(event.dataTransfer.files);
      if (files.length > 0) {
        onFiles(files);
      }
    };

    window.addEventListener('dragenter', handleDragEnter);
    window.addEventListener('dragover', handleDragOver);
    window.addEventListener('dragleave', handleDragLeave);
    window.addEventListener('drop', handleDrop);

    return () => {
      window.removeEventListener('dragenter', handleDragEnter);
      window.removeEventListener('dragover', handleDragOver);
      window.removeEventListener('dragleave', handleDragLeave);
      window.removeEventListener('drop', handleDrop);
    };
  }, [onFiles]);

  return dragging;
}
