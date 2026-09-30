import { Link } from 'react-router-dom';
import type { Breadcrumb } from '../types';

export interface BreadcrumbsProps {
  items: Breadcrumb[];
}

/** Навигационная цепочка: корень и все родительские папки. */
export function Breadcrumbs({ items }: BreadcrumbsProps) {
  if (items.length === 0) {
    return null;
  }

  return (
    <nav className="breadcrumbs" aria-label="Путь к текущей папке">
      <ol className="breadcrumbs__list">
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          const key = item.id === null ? 'root' : `folder-${item.id}`;

          return (
            <li className="breadcrumbs__item" key={key}>
              {isLast ? (
                <span className="breadcrumbs__current" aria-current="page">
                  {item.name}
                </span>
              ) : (
                <Link className="breadcrumbs__link" to={item.id === null ? '/files' : `/files/folder/${item.id}`}>
                  {item.name}
                </Link>
              )}
              {!isLast && (
                <span className="breadcrumbs__separator" aria-hidden="true">
                  {'/'}
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
