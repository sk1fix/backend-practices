import { formatBytes, usagePercent } from '../utils/format';

export interface UsageBarProps {
  used: number;
  quota: number;
  compact?: boolean;
}

/** Полоса занятого места в хранилище. */
export function UsageBar({ used, quota, compact = false }: UsageBarProps) {
  const percent = usagePercent(used, quota);
  const tone = percent >= 90 ? 'danger' : percent >= 70 ? 'warning' : 'ok';

  return (
    <div className={`usage${compact ? ' usage--compact' : ''}`}>
      <div className="usage__header">
        <span className="usage__label">Хранилище</span>
        <span className="usage__value">
          {formatBytes(used)} из {formatBytes(quota)}
        </span>
      </div>
      <div
        className="progress progress--tall"
        role="progressbar"
        aria-label="Занятое место"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={Math.round(percent)}
      >
        <div className={`progress__bar progress__bar--${tone}`} style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}
