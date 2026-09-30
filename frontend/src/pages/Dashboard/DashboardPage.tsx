import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Database,
  PlayCircle,
  CheckCircle2,
  ArrowUpRight,
  Clock,
  Cpu,
} from 'lucide-react';
import { Card, CardHeader, CardContent } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';
import './DashboardPage.css';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="quant-dashboard">
      {/* Page Title & Status */}
      <div className="quant-page-header">
        <div>
          <div className="quant-breadcrumb">
            <span className="caption-label">LEAN Quant Platform</span>
            <span className="quant-breadcrumb-sep">/</span>
            <span className="caption-label text-accent">Overview</span>
          </div>
          <h1 className="heading-display">Quantitative Trading Workspace</h1>
          <p className="quant-page-desc">
            Indian market backtesting and algorithmic trading environment powered by QuantConnect LEAN.
          </p>
        </div>

        <div className="quant-page-actions">
          <Button
            variant="secondary"
            size="md"
            icon={<Database size={15} />}
            onClick={() => navigate('/data')}
          >
            Data Catalog (6 Symbols)
          </Button>
          <Button
            variant="primary"
            size="md"
            icon={<PlayCircle size={15} />}
            onClick={() => navigate('/backtesting')}
          >
            Open Backtest Workspace
          </Button>
        </div>
      </div>

      {/* Verified Baseline Performance Highlight */}
      <div className="quant-verified-banner">
        <div className="quant-verified-badge-row">
          <Badge variant="profit" dot size="sm">CHECKPOINT VERIFIED</Badge>
          <span className="meta-text">Algorithm: SmaCrossoverAlgorithm · 5-Stock Portfolio</span>
        </div>
        <div className="quant-metrics-strip">
          <div className="quant-strip-metric">
            <span className="caption-label">Final Equity</span>
            <span className="metric-value font-mono">₹19,30,342</span>
            <span className="quant-metric-sub text-profit">+93.03% Net Profit</span>
          </div>
          <div className="quant-strip-metric">
            <span className="caption-label">Sharpe Ratio</span>
            <span className="metric-value font-mono">0.512</span>
            <span className="quant-metric-sub">Sortino 0.576</span>
          </div>
          <div className="quant-strip-metric">
            <span className="caption-label">CAGR</span>
            <span className="metric-value font-mono">7.58%</span>
            <span className="quant-metric-sub">Annualized Return</span>
          </div>
          <div className="quant-strip-metric">
            <span className="caption-label">Max Drawdown</span>
            <span className="metric-value font-mono text-loss">19.80%</span>
            <span className="quant-metric-sub">Peak-to-Trough</span>
          </div>
          <div className="quant-strip-metric">
            <span className="caption-label">Closed Trades</span>
            <span className="metric-value font-mono">119</span>
            <span className="quant-metric-sub">245 Total Orders</span>
          </div>
          <div className="quant-strip-metric">
            <span className="caption-label">Zerodha Fees</span>
            <span className="metric-value font-mono">₹18,579</span>
            <span className="quant-metric-sub text-profit">Verified Deducted</span>
          </div>
        </div>
      </div>

      {/* Quick Navigation Cards Grid */}
      <div className="quant-dashboard-grid">
        {/* Backtesting Engine Card */}
        <Card variant="surface-1" elevation="elevated">
          <CardHeader
            title="Backtesting Engine"
            subtitle="QuantConnect LEAN v2.5.0.0 integration"
            action={<Badge variant="profit" size="sm">Active</Badge>}
          />
          <CardContent className="quant-card-grid-content">
            <p className="quant-card-text">
              Dual-SMA crossover logic running on daily Indian equity bars with Zerodha transaction fee model,
              cash allocation constraints, and look-ahead execution protection.
            </p>
            <div className="quant-spec-list">
              <div className="quant-spec-item">
                <span className="quant-spec-key">Execution Mode:</span>
                <span className="quant-spec-val font-mono">Daily Resolution</span>
              </div>
              <div className="quant-spec-item">
                <span className="quant-spec-key">Look-Ahead Guard:</span>
                <span className="quant-spec-val font-mono">T Signal → T+1 Order → T+2 Fill</span>
              </div>
              <div className="quant-spec-item">
                <span className="quant-spec-key">Runtime Bridge:</span>
                <span className="quant-spec-val font-mono">PythonNet 3.x (CLR 4.0)</span>
              </div>
            </div>
            <div className="quant-card-action-row">
              <Button
                variant="outline"
                size="sm"
                icon={<ArrowUpRight size={14} />}
                onClick={() => navigate('/backtesting')}
              >
                Configure Run
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Indian Market Data Card */}
        <Card variant="surface-1" elevation="elevated">
          <CardHeader
            title="Indian Market Data"
            subtitle="NSE/BSE historical cache & LEAN archives"
            action={<Badge variant="info" size="sm">6 Symbols Ready</Badge>}
          />
          <CardContent className="quant-card-grid-content">
            <p className="quant-card-text">
              Curated Indian blue-chip equity symbols fully validated, normalized to LEAN daily format (price × 10,000 scale),
              and packaged into ZIP archives for direct engine ingestion.
            </p>
            <div className="quant-symbol-chips">
              {['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'WIPRO'].map((sym) => (
                <span key={sym} className="quant-symbol-chip">
                  <span className="quant-chip-dot" />
                  <span className="font-mono">{sym}</span>
                </span>
              ))}
            </div>
            <div className="quant-card-action-row">
              <Button
                variant="secondary"
                size="sm"
                icon={<Database size={14} />}
                onClick={() => navigate('/data')}
              >
                Inspect Data Catalog
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Strategy Catalog Card */}
        <Card variant="surface-1" elevation="elevated">
          <CardHeader
            title="Strategy Catalog"
            subtitle="Immutable canonical algorithms"
            action={<Badge variant="neutral" size="sm">4 Algorithms</Badge>}
          />
          <CardContent className="quant-card-grid-content">
            <p className="quant-card-text">
              Canonical strategies stored in <code className="font-mono">src/lean_integration/</code>.
              Source files remain strictly immutable; parameters are passed via runtime config files.
            </p>
            <div className="quant-spec-list">
              <div className="quant-spec-item">
                <span className="quant-spec-key">Primary:</span>
                <span className="quant-spec-val font-mono">SmaCrossoverAlgorithm (5 stocks)</span>
              </div>
              <div className="quant-spec-item">
                <span className="quant-spec-key">Single-Asset:</span>
                <span className="quant-spec-val font-mono">WiproSmaAlgorithm (WIPRO)</span>
              </div>
              <div className="quant-spec-item">
                <span className="quant-spec-key">Validation:</span>
                <span className="quant-spec-val font-mono">MinimalIndianAlgorithm</span>
              </div>
            </div>
            <div className="quant-card-action-row">
              <Button
                variant="subtle"
                size="sm"
                icon={<Cpu size={14} />}
                onClick={() => navigate('/strategies')}
              >
                View Strategy Catalog
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* System Architecture & Health Card */}
        <Card variant="surface-1" elevation="elevated">
          <CardHeader
            title="Platform Architecture"
            subtitle="Phase 1 Foundation Status"
            action={<Badge variant="profit" size="sm">Nominal</Badge>}
          />
          <CardContent className="quant-card-grid-content">
            <div className="quant-health-list">
              <div className="quant-health-row">
                <CheckCircle2 size={16} className="text-profit" />
                <span className="quant-health-name">Design Token System:</span>
                <span className="quant-health-status font-mono text-profit">12 Token Categories Active</span>
              </div>
              <div className="quant-health-row">
                <CheckCircle2 size={16} className="text-profit" />
                <span className="quant-health-name">Navigation Architecture:</span>
                <span className="quant-health-status font-mono text-profit">8 Core Areas Structured</span>
              </div>
              <div className="quant-health-row">
                <CheckCircle2 size={16} className="text-profit" />
                <span className="quant-health-name">Baseline Checkpoint:</span>
                <span className="quant-health-status font-mono text-profit">Tag PRE_FRONTEND_CHECKPOINT</span>
              </div>
              <div className="quant-health-row">
                <Clock size={16} className="text-accent" />
                <span className="quant-health-name">Backend FastAPI (Phase 3):</span>
                <span className="quant-health-status font-mono text-muted">Awaiting Phase 2-3</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
