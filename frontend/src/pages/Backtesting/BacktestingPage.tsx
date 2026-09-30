import React, { useMemo, useState } from 'react';
import {
  Sliders,
  Terminal,
  FileText,
  Play,
  Info,
  AlertTriangle,
  RotateCcw,
  CheckCircle2,
} from 'lucide-react';
import { Card, CardHeader, CardContent, CardFooter } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';
import {
  AVAILABLE_STRATEGIES,
  DEFAULT_BACKTEST_CONFIG,
  VERIFIED_INDIAN_SYMBOLS,
  type BacktestConfig,
  type StrategyDefinition,
} from '../../types/backtest';
import { formatINR } from '../../utils/formatters';
import {
  BacktestApiError,
  runBacktest,
  type BacktestRunResponse,
} from '../../api/backtestApi';
import { StrategySelector } from './components/StrategySelector';
import { SymbolSelector } from './components/SymbolSelector';
import { PeriodPicker } from './components/PeriodPicker';
import { CapitalInput } from './components/CapitalInput';
import { BrokerageSelector } from './components/BrokerageSelector';
import { SmaParameterForm } from './components/SmaParameterForm';
import { UnsupportedControlsPanel } from './components/UnsupportedControlsPanel';
import './BacktestingPage.css';

type BacktestTab = 'configure' | 'execution' | 'results';

export const BacktestingPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<BacktestTab>('configure');
  const [config, setConfig] = useState<BacktestConfig>({ ...DEFAULT_BACKTEST_CONFIG });
  const [runNotice, setRunNotice] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [lastRun, setLastRun] = useState<BacktestRunResponse | null>(null);

  const selectedStrategy = useMemo(
    () => AVAILABLE_STRATEGIES.find((s) => s.id === config.strategy) ?? AVAILABLE_STRATEGIES[0],
    [config.strategy],
  );

  const isConfigValid =
    config.symbols.length > 0 &&
    config.fastPeriod < config.slowPeriod &&
    config.startingCapital > 0 &&
    config.startDate <= config.endDate;

  const updateConfig = <K extends keyof BacktestConfig>(key: K, value: BacktestConfig[K]) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
    setRunNotice(null);
  };

  const handleSelectStrategy = (strategy: StrategyDefinition) => {
    setConfig((prev) => ({
      ...prev,
      strategy: strategy.id,
      symbols: [...strategy.defaultSymbols],
      positionWeight:
        strategy.universeType === 'single-asset'
          ? 1.0
          : DEFAULT_BACKTEST_CONFIG.positionWeight,
    }));
    setRunNotice(null);
  };

  const handleToggleSymbol = (symbol: string) => {
    setConfig((prev) => {
      const exists = prev.symbols.includes(symbol);
      return {
        ...prev,
        symbols: exists
          ? prev.symbols.filter((s) => s !== symbol)
          : [...prev.symbols, symbol],
      };
    });
    setRunNotice(null);
  };

  const handleRunBacktest = async () => {
    if (!isConfigValid) {
      setRunNotice('Fix configuration errors before running a backtest.');
      return;
    }

    setIsSubmitting(true);
    setRunNotice('Submitting backtest to FastAPI… LEAN execution may take several minutes.');
    setActiveTab('execution');

    try {
      const result = await runBacktest(config);
      setLastRun(result);
      if (result.status === 'completed') {
        setRunNotice(
          `Run ${result.runId} completed. Duration ${result.durationSeconds?.toFixed(1) ?? '—'}s. Detailed monitoring arrives in Phase 4.`,
        );
      } else {
        setRunNotice(
          `Run ${result.runId} ended with status ${result.status}: ${result.error?.message || result.message}`,
        );
      }
    } catch (err) {
      const message =
        err instanceof BacktestApiError
          ? `${err.code}: ${err.message}`
          : err instanceof Error
            ? err.message
            : 'Unknown API error';
      setLastRun(null);
      setRunNotice(`Backtest request failed — ${message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setConfig({ ...DEFAULT_BACKTEST_CONFIG });
    setRunNotice(null);
  };

  return (
    <div className="quant-backtesting-view">
      <div className="quant-page-header">
        <div>
          <div className="quant-breadcrumb">
            <span className="caption-label">LEAN Quant Platform</span>
            <span className="quant-breadcrumb-sep">/</span>
            <span className="caption-label text-accent">Backtesting Workspace</span>
          </div>
          <h1 className="heading-display">Backtesting Engine</h1>
          <p className="quant-page-desc">
            Configure Indian equity backtests for QuantConnect LEAN. Phase 3 submits runs through
            FastAPI using isolated runtime configuration.
          </p>
        </div>

        <div className="quant-tab-strip" role="tablist" aria-label="Backtesting workflow">
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'configure'}
            className={`quant-tab-btn ${activeTab === 'configure' ? 'is-active' : ''}`}
            onClick={() => setActiveTab('configure')}
          >
            <Sliders size={15} />
            <span>1. Configure</span>
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'execution'}
            className={`quant-tab-btn ${activeTab === 'execution' ? 'is-active' : ''}`}
            onClick={() => setActiveTab('execution')}
          >
            <Terminal size={15} />
            <span>2. Execution</span>
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'results'}
            className={`quant-tab-btn ${activeTab === 'results' ? 'is-active' : ''}`}
            onClick={() => setActiveTab('results')}
          >
            <FileText size={15} />
            <span>3. Results</span>
          </button>
        </div>
      </div>

      {/* Workflow strip — visually connects the three stages */}
      <div className="quant-workflow-strip">
        <div className={`quant-workflow-step ${activeTab === 'configure' ? 'is-current' : 'is-done'}`}>
          <span className="quant-workflow-index">01</span>
          <div>
            <span className="quant-workflow-label">Configure</span>
            <span className="quant-workflow-meta">
              {selectedStrategy.className} · {config.symbols.length} symbols
            </span>
          </div>
        </div>
        <div className="quant-workflow-connector" />
        <div className={`quant-workflow-step ${activeTab === 'execution' ? 'is-current' : ''}`}>
          <span className="quant-workflow-index">02</span>
          <div>
            <span className="quant-workflow-label">Execution</span>
            <span className="quant-workflow-meta">LEAN process monitor · Phase 4</span>
          </div>
        </div>
        <div className="quant-workflow-connector" />
        <div className={`quant-workflow-step ${activeTab === 'results' ? 'is-current' : ''}`}>
          <span className="quant-workflow-index">03</span>
          <div>
            <span className="quant-workflow-label">Results</span>
            <span className="quant-workflow-meta">Equity · Trades · Fees · Phase 5</span>
          </div>
        </div>
      </div>

      {activeTab === 'configure' && (
        <div className="quant-tab-content">
          <div className="quant-config-layout">
            <div className="quant-config-main">
              <Card variant="surface-1">
                <CardHeader
                  title="Strategy & Universe"
                  subtitle="Select algorithm logic and Indian equity symbols"
                  action={
                    <Badge variant="info" size="sm">
                      Phase 3 API
                    </Badge>
                  }
                />
                <CardContent className="quant-form-stack">
                  <StrategySelector
                    selectedStrategyId={config.strategy}
                    onSelectStrategy={handleSelectStrategy}
                  />
                  <SymbolSelector
                    selectedSymbols={config.symbols}
                    onToggleSymbol={handleToggleSymbol}
                    onSelectAll={() =>
                      updateConfig(
                        'symbols',
                        VERIFIED_INDIAN_SYMBOLS.map((s) => s.symbol),
                      )
                    }
                    onSelect5Default={() =>
                      updateConfig('symbols', [
                        'RELIANCE.NS',
                        'TCS.NS',
                        'INFY.NS',
                        'HDFCBANK.NS',
                        'ICICIBANK.NS',
                      ])
                    }
                    onClearAll={() => updateConfig('symbols', [])}
                  />
                </CardContent>
              </Card>

              <Card variant="surface-1">
                <CardHeader
                  title="Period, Capital & Brokerage"
                  subtitle="Verified Indian market assumptions"
                />
                <CardContent className="quant-form-stack">
                  <PeriodPicker
                    startDate={config.startDate}
                    endDate={config.endDate}
                    onChangeStartDate={(d) => updateConfig('startDate', d)}
                    onChangeEndDate={(d) => updateConfig('endDate', d)}
                  />
                  <div className="quant-config-split">
                    <CapitalInput
                      capital={config.startingCapital}
                      onChangeCapital={(v) => updateConfig('startingCapital', v)}
                    />
                    <BrokerageSelector selectedBroker={config.brokerage} />
                  </div>
                </CardContent>
              </Card>

              <Card variant="surface-1">
                <CardHeader
                  title="Strategy Parameters"
                  subtitle="Parameters represented by the existing SMA implementation"
                />
                <CardContent>
                  <SmaParameterForm
                    fastPeriod={config.fastPeriod}
                    slowPeriod={config.slowPeriod}
                    positionWeight={config.positionWeight}
                    symbolCount={config.symbols.length}
                    onChangeFastPeriod={(v) => updateConfig('fastPeriod', v)}
                    onChangeSlowPeriod={(v) => updateConfig('slowPeriod', v)}
                    onChangePositionWeight={(v) => updateConfig('positionWeight', v)}
                  />
                </CardContent>
              </Card>

              <Card variant="surface-1">
                <CardHeader
                  title="Future Controls"
                  subtitle="Visible for roadmap clarity — not actionable in Phase 2"
                />
                <CardContent>
                  <UnsupportedControlsPanel />
                </CardContent>
              </Card>
            </div>

            <aside className="quant-config-rail">
              <Card variant="surface-2" className="quant-config-summary-card">
                <CardHeader
                  title="Run Summary"
                  subtitle="Typed payload for Phase 3 API"
                  action={
                    <Badge variant={isConfigValid ? 'profit' : 'warning'} size="sm">
                      {isConfigValid ? 'Valid' : 'Incomplete'}
                    </Badge>
                  }
                />
                <CardContent className="quant-summary-stack">
                  <div className="quant-summary-row">
                    <span className="caption-label">Strategy</span>
                    <span className="font-mono text-xs text-primary">{selectedStrategy.className}</span>
                  </div>
                  <div className="quant-summary-row">
                    <span className="caption-label">Symbols</span>
                    <span className="font-mono text-xs text-accent">
                      {config.symbols.length > 0 ? config.symbols.join(', ') : '—'}
                    </span>
                  </div>
                  <div className="quant-summary-row">
                    <span className="caption-label">Period</span>
                    <span className="font-mono text-xs text-primary">
                      {config.startDate} → {config.endDate}
                    </span>
                  </div>
                  <div className="quant-summary-row">
                    <span className="caption-label">Capital</span>
                    <span className="font-mono text-xs text-profit">
                      {formatINR(config.startingCapital)}
                    </span>
                  </div>
                  <div className="quant-summary-row">
                    <span className="caption-label">Brokerage</span>
                    <span className="font-mono text-xs text-primary">Zerodha</span>
                  </div>
                  <div className="quant-summary-row">
                    <span className="caption-label">SMA / Weight</span>
                    <span className="font-mono text-xs text-primary">
                      {config.fastPeriod}/{config.slowPeriod} ·{' '}
                      {(config.positionWeight * 100).toFixed(0)}%
                    </span>
                  </div>

                  <div className="quant-payload-preview">
                    <span className="caption-label">API Payload Preview</span>
                    <pre className="quant-payload-json font-mono">{JSON.stringify(config, null, 2)}</pre>
                  </div>
                </CardContent>
                <CardFooter className="quant-run-footer">
                  <Button
                    variant="subtle"
                    size="sm"
                    icon={<RotateCcw size={13} />}
                    onClick={handleReset}
                  >
                    Reset Defaults
                  </Button>
                  <Button
                    variant="primary"
                    size="lg"
                    icon={<Play size={15} />}
                    disabled={!isConfigValid || isSubmitting}
                    isLoading={isSubmitting}
                    onClick={handleRunBacktest}
                    className="quant-run-btn"
                  >
                    {isSubmitting ? 'Running…' : 'Run Backtest'}
                  </Button>
                </CardFooter>
              </Card>

              {runNotice && (
                <div className="quant-run-notice" role="status">
                  <Info size={15} className="text-accent" />
                  <p className="meta-text">{runNotice}</p>
                </div>
              )}

              <div className="quant-config-notice">
                <AlertTriangle size={15} className="text-warning" />
                <p className="meta-text">
                  <strong>Phase 3:</strong> Run Backtest POSTs to{' '}
                  <code className="font-mono">/api/backtest/run</code>. Live progress streaming is
                  Phase 4.
                </p>
              </div>

              <div className="quant-config-notice quant-config-notice--muted">
                <CheckCircle2 size={15} className="text-profit" />
                <p className="meta-text">
                  Canonical strategy files remain read-only. Isolated runtime config under{' '}
                  <code className="font-mono">.runtime/</code> injects parameters without rewriting{' '}
                  <code className="font-mono">sma_crossover_algorithm.py</code>.
                </p>
              </div>
            </aside>
          </div>
        </div>
      )}

      {activeTab === 'execution' && (
        <div className="quant-tab-content">
          <Card variant="surface-1">
            <CardHeader
              title="Execution Monitor"
              subtitle="Phase 3 submission status — detailed streaming in Phase 4"
              action={
                <Badge
                  variant={
                    isSubmitting
                      ? 'warning'
                      : lastRun?.status === 'completed'
                        ? 'profit'
                        : lastRun
                          ? 'loss'
                          : 'coming-soon'
                  }
                  size="sm"
                >
                  {isSubmitting
                    ? 'Running'
                    : lastRun
                      ? lastRun.status
                      : 'Idle'}
                </Badge>
              }
            />
            <CardContent>
              <div className="quant-execution-preview">
                <div className="quant-exec-status-card">
                  <div className="flex items-center gap-3">
                    <div className="quant-engine-status-dot" />
                    <div>
                      <h4 className="quant-exec-title">
                        {isSubmitting
                          ? 'LEAN backtest in progress…'
                          : lastRun
                            ? `Run ${lastRun.runId}`
                            : 'No run submitted yet'}
                      </h4>
                      <p className="meta-text">
                        {lastRun?.message ||
                          'Submit from Configure to invoke FastAPI → runtime config → LEAN.'}
                      </p>
                    </div>
                  </div>
                  <Button variant="secondary" size="md" onClick={() => setActiveTab('configure')}>
                    Back to Configure
                  </Button>
                </div>

                <div className="quant-console-preview">
                  <div className="quant-console-bar">
                    <span className="caption-label">Execution Snapshot</span>
                    <Badge variant="neutral" size="sm">
                      {lastRun?.status || (isSubmitting ? 'running' : 'idle')}
                    </Badge>
                  </div>
                  <pre className="quant-terminal-text font-mono">
{`[PHASE 3] POST /api/backtest/run
[CONFIG ] strategy        = ${config.strategy}
[CONFIG ] symbols         = ${config.symbols.join(', ') || '(none)'}
[CONFIG ] period          = ${config.startDate} → ${config.endDate}
[CONFIG ] capital         = ${formatINR(config.startingCapital)}
[CONFIG ] brokerage       = ${config.brokerage}
[CONFIG ] fast/slow/wt    = ${config.fastPeriod}/${config.slowPeriod}/${config.positionWeight}
[RUN    ] id              = ${lastRun?.runId ?? (isSubmitting ? '(pending)' : '—')}
[RUN    ] status          = ${lastRun?.status ?? (isSubmitting ? 'running' : '—')}
[RUN    ] pid             = ${lastRun?.processId ?? '—'}
[RUN    ] duration_s      = ${lastRun?.durationSeconds ?? '—'}
[RUN    ] summary         = ${lastRun?.summaryPath ?? '—'}
[RUN    ] runtime_config  = ${lastRun?.runtimeConfigPath ?? '—'}
[STATS  ] ${lastRun?.statistics ? JSON.stringify(lastRun.statistics) : '—'}
[STATUS ] Real-time LEAN log monitoring coming in Phase 4`}
                  </pre>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'results' && (
        <div className="quant-tab-content">
          <div className="quant-results-overview">
            <div className="quant-results-header-card">
              <div>
                <Badge variant="profit" size="sm">
                  Verified Checkpoint Result
                </Badge>
                <h2 className="heading-section mt-1">
                  SmaCrossoverAlgorithm — 5-Stock Portfolio Run
                </h2>
                <p className="meta-text">
                  Static reference metrics from the pre-frontend checkpoint. Interactive charts
                  connect in Phase 5.
                </p>
              </div>
              <Button
                variant="secondary"
                size="sm"
                icon={<Sliders size={14} />}
                onClick={() => setActiveTab('configure')}
              >
                Modify Parameters
              </Button>
            </div>

            <div className="quant-results-stat-grid">
              <div className="quant-stat-card">
                <span className="caption-label">Sharpe Ratio</span>
                <span className="metric-value font-mono">0.512</span>
                <span className="meta-text text-profit">Benchmark Validated</span>
              </div>
              <div className="quant-stat-card">
                <span className="caption-label">Sortino Ratio</span>
                <span className="metric-value font-mono">0.576</span>
                <span className="meta-text">Downside Risk Adjusted</span>
              </div>
              <div className="quant-stat-card">
                <span className="caption-label">CAGR</span>
                <span className="metric-value font-mono text-profit">7.583%</span>
                <span className="meta-text">Multi-year timeline</span>
              </div>
              <div className="quant-stat-card">
                <span className="caption-label">Max Drawdown</span>
                <span className="metric-value font-mono text-loss">19.8%</span>
                <span className="meta-text text-loss">Within Risk Limits</span>
              </div>
              <div className="quant-stat-card">
                <span className="caption-label">Win Rate</span>
                <span className="metric-value font-mono">45.0%</span>
                <span className="meta-text">Profit Factor 2.45</span>
              </div>
              <div className="quant-stat-card">
                <span className="caption-label">Final Equity</span>
                <span className="metric-value font-mono">₹19,30,342</span>
                <span className="meta-text text-profit">+₹9,30,342 Profit</span>
              </div>
              <div className="quant-stat-card">
                <span className="caption-label">Zerodha Fees</span>
                <span className="metric-value font-mono">₹18,579</span>
                <span className="meta-text">Deducted from Equity</span>
              </div>
              <div className="quant-stat-card">
                <span className="caption-label">Closed Trades</span>
                <span className="metric-value font-mono">119</span>
                <span className="meta-text">245 Order Events</span>
              </div>
            </div>

            <Card variant="surface-1">
              <CardHeader
                title="Results Dashboard Integration"
                subtitle="Scheduled for Phase 5"
                action={
                  <Badge variant="coming-soon" size="sm">
                    Coming Soon
                  </Badge>
                }
              />
              <CardContent>
                <p className="quant-card-text">
                  Full interactive equity curve, drawdown underlay, trade tables, and order events
                  will parse verified LEAN JSON outputs in Phase 5. No fabricated series are shown
                  here.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
};
