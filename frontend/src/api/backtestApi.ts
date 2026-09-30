import type { BacktestConfig } from '../types/backtest';

export interface ApiErrorBody {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface BacktestRunResponse {
  runId: string;
  status: 'queued' | 'running' | 'completed' | 'failed' | 'timeout';
  strategy: string;
  message: string;
  startedAt?: string | null;
  completedAt?: string | null;
  durationSeconds?: number | null;
  processId?: number | null;
  exitCode?: number | null;
  resultLocation?: string | null;
  summaryPath?: string | null;
  statistics?: Record<string, string> | null;
  error?: ApiErrorBody | null;
  runtimeConfigPath?: string | null;
}

export class BacktestApiError extends Error {
  code: string;
  details?: Record<string, unknown>;
  status: number;

  constructor(status: number, body: ApiErrorBody) {
    super(body.message);
    this.name = 'BacktestApiError';
    this.status = status;
    this.code = body.code;
    this.details = body.details;
  }
}

export async function runBacktest(config: BacktestConfig): Promise<BacktestRunResponse> {
  const response = await fetch('/api/backtest/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });

  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    const detail = (payload && payload.detail) || payload;
    const err: ApiErrorBody = {
      code: detail?.code || 'request_failed',
      message: detail?.message || `Request failed with status ${response.status}`,
      details: detail?.details,
    };
    throw new BacktestApiError(response.status, err);
  }

  return payload as BacktestRunResponse;
}