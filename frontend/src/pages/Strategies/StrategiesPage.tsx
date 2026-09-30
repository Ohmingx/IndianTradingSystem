import React from 'react';
import { Cpu, ShieldCheck, Lock } from 'lucide-react';
import { Card, CardHeader, CardContent } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import './StrategiesPage.css';

export const StrategiesPage: React.FC = () => {
  const algorithms = [
    {
      id: 'sma-crossover-5stock',
      name: 'SmaCrossoverAlgorithm',
      file: 'src/lean_integration/sma_crossover_algorithm.py',
      description: 'Primary 5-stock dual moving average crossover strategy on Indian equities.',
      status: 'Verified Working',
      symbols: ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK'],
      params: [
        { name: 'FAST_PERIOD', value: '20', desc: 'Fast SMA lookback window (days)' },
        { name: 'SLOW_PERIOD', value: '50', desc: 'Slow SMA lookback window (days)' },
        { name: 'POSITION_WEIGHT', value: '0.18', desc: 'Max 18% portfolio equity per position' },
        { name: 'LOOKAHEAD_GUARD', value: 'T signal → T+1 order → T+2 fill', desc: 'Execution timing guard' },
      ],
      brokerage: 'Zerodha Custom Model (Equity Delivery ₹0, statutory fees modeled)',
      result: '₹19,30,342 End Equity (93.03% Net Return, Sharpe 0.512)',
    },
    {
      id: 'wipro-sma',
      name: 'WiproSmaAlgorithm',
      file: 'src/lean_integration/wipro_sma_algorithm.py',
      description: 'Single-stock dual moving average crossover baseline strategy on WIPRO.',
      status: 'Verified Working',
      symbols: ['WIPRO'],
      params: [
        { name: 'FAST_PERIOD', value: '20', desc: 'Fast SMA period' },
        { name: 'SLOW_PERIOD', value: '50', desc: 'Slow SMA period' },
        { name: 'POSITION_WEIGHT', value: '1.0', desc: 'Single-asset full allocation' },
      ],
      brokerage: 'Zerodha Model',
      result: 'Verified Completed',
    },
    {
      id: 'minimal-algorithm',
      name: 'MinimalIndianAlgorithm',
      file: 'src/lean_integration/minimal_algorithm.py',
      description: 'Phase 3 integration test algorithm validating custom Indian data adapter and market hours.',
      status: 'Verified Working',
      symbols: ['RELIANCE'],
      params: [
        { name: 'RESOLUTION', value: 'Daily', desc: 'Market.India equity bars' },
        { name: 'DATA_READER', value: 'IndianDataAdapter (PythonData)', desc: 'Custom CSV reader' },
      ],
      brokerage: 'Zerodha Model',
      result: 'Integration Verified',
    },
    {
      id: 'trading-model-algorithm',
      name: 'TradingModelAlgorithm',
      file: 'src/lean_integration/trading_model_algorithm.py',
      description: 'Phase 4 test algorithm for execution modeling, order events, and fee calculation assertion.',
      status: 'Verified Working',
      symbols: ['RELIANCE'],
      params: [
        { name: 'ASSERT_FEES', value: 'True', desc: 'Ensures Zerodha fees are non-zero' },
      ],
      brokerage: 'Zerodha Model',
      result: 'Asserts Passed',
    },
  ];

  return (
    <div className="quant-strategies-view">
      <div className="quant-page-header">
        <div>
          <div className="quant-breadcrumb">
            <span className="caption-label">LEAN Quant Platform</span>
            <span className="quant-breadcrumb-sep">/</span>
            <span className="caption-label text-accent">Strategy Catalog</span>
          </div>
          <h1 className="heading-display">Algorithm Catalog & Parameters</h1>
          <p className="quant-page-desc">
            Canonical LEAN Python algorithms verified in the repository. Source files remain strictly immutable.
          </p>
        </div>

        <div className="quant-immutability-badge">
          <Lock size={14} className="text-accent" />
          <span className="font-mono text-xs">CANONICAL SOURCE IMMUTABLE</span>
        </div>
      </div>

      {/* Architecture Guarantee Callout */}
      <div className="quant-immutability-card">
        <div className="flex items-start gap-3">
          <ShieldCheck size={20} className="text-profit mt-1" />
          <div>
            <h3 className="heading-sub text-primary">Canonical Strategy Immutability Architecture</h3>
            <p className="quant-card-text mt-1">
              Existing strategy implementation files in <code className="font-mono">src/lean_integration/</code> are
              strictly read-only and will never be modified or rewritten by frontend backtest execution.
              In Phase 3, frontend parameter overrides are injected via an isolated temporary runtime configuration
              mechanism without mutating the canonical source.
            </p>
          </div>
        </div>
      </div>

      {/* Strategy Cards */}
      <div className="quant-strategies-grid">
        {algorithms.map((algo) => (
          <Card key={algo.id} variant="surface-1">
            <CardHeader
              title={
                <div className="flex items-center gap-2">
                  <Cpu size={16} className="text-accent" />
                  <span>{algo.name}</span>
                </div>
              }
              subtitle={<code className="font-mono text-muted">{algo.file}</code>}
              action={<Badge variant="profit" size="sm">{algo.status}</Badge>}
            />
            <CardContent className="quant-card-grid-content">
              <p className="quant-card-text">{algo.description}</p>

              <div className="quant-algo-section">
                <span className="caption-label">Universe</span>
                <div className="quant-symbol-chips">
                  {algo.symbols.map((sym) => (
                    <span key={sym} className="quant-symbol-chip">
                      <span className="font-mono">{sym}</span>
                    </span>
                  ))}
                </div>
              </div>

              <div className="quant-algo-section">
                <span className="caption-label">Parameters (Default Constants)</span>
                <div className="quant-params-table">
                  {algo.params.map((p) => (
                    <div key={p.name} className="quant-param-row">
                      <span className="font-mono text-accent text-xs">{p.name}</span>
                      <span className="font-mono text-xs text-primary font-bold">{p.value}</span>
                      <span className="text-muted text-xs">{p.desc}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="quant-algo-meta-footer">
                <div className="quant-spec-item">
                  <span className="caption-label">Brokerage:</span>
                  <span className="text-xs text-secondary">{algo.brokerage}</span>
                </div>
                <div className="quant-spec-item">
                  <span className="caption-label">Verified Result:</span>
                  <span className="text-xs text-profit font-mono">{algo.result}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};
