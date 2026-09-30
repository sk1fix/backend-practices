import { request } from './client';
import type { HealthStatus, Usage } from '../types';

/** GET /api/storage/usage — занятое место и количество объектов. */
export function getUsage(signal?: AbortSignal): Promise<Usage> {
  return request<Usage>('/storage/usage', { signal });
}

/** GET /api/health — проверка доступности сервиса (без авторизации). */
export function getHealth(): Promise<HealthStatus> {
  return request<HealthStatus>('/health');
}
