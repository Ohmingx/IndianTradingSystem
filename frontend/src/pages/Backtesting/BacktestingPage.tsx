import React, { useState } from 'react';
import {
  Sliders,
  Terminal,
  FileText,
  Play,
  IndianRupee,
  Shield,
  Info,
} from 'lucide-react';
import { Card, CardHeader, CardContent, CardFooter } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';
import './BacktestingPage.css';

type BacktestTab = 'configure' | 'execution' | 'results';

export const BacktestingPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<BacktestTab>('configure');

  // Available Indian symbols verified in repository
  const availableSymbols = [
    { symbol: 'RELIANCE', name: 'Reliance Industries Ltd.', status: 'LEAN Ready' },
    { symbol: 'TCS', name: 'Tata Consultancy Services Ltd.', status: 'LEAN Ready' },
    { symbol: 'INFY', name: 'Infosys Ltd.', status: 'LEAN Ready' },
    { symbol: 'HDFCBANK', name: 'HDFC Bank Ltd.', status: 'LEAN Ready' },
    { symbol: 'ICICIBANK', name: 'ICICI Bank Ltd.', status: 'LEAN Ready' },
    { symbol: 'WIPRO', name: 'Wipro Ltd.', status: 'LEAN Ready' },
  ];

  return (
    <div className="quant-backtesting-view">
      {/* View Header */}
      <div className="quant-page-header">
        <div>
          <div className="quant-breadcrumb">
            <span className="caption-label">LEAN Quant Platform</span>
            <span className="quant-breadcrumb-sep">/</span>
            <span className="caption-label text-accent">Backtesting Workspace</span>
          </div>
          <h1 className="heading-display">Backtesting Engine</h1>
          <p className="quant-page-desc">
            Dual-SMA crossover strategy backtesting using QuantConnect LEAN on daily Indian equity bars.
          </p>
        </div>

        {/* Sub-navigation tabs */}
        <div className="quant-tab-strip">
          <button
            className={`quant-tab-btn ${activeTab === 'configure' ? 'is-active' : ''}`}
            onClick={() => setActiveTab('configure')}
          >
            <Sliders size={15} />
            <span>1. Configuration</span>
          </button>
          <button
            className={`quant-tab-btn ${activeTab === 'execution' ? 'is-active' : ''}`}
            onClick={() => setActiveTab('execution')}
          >
            <Terminal size={15} />
            <span>2. Execution</span>
          </button>
          <button
            className={`quant-tab-btn ${activeTab === 'results' ? 'is-active' : ''}`}
            onClick={() => setActiveTab('results')}
          >
            <FileText size={15} />
            <span>3. Results</span>
          </button>
        </div>
      </div>

      {/* TAB 1: CONFIGURE */}
      {activeTab === 'configure' && (
        <div className="quant-tab-content">
          <div className="quant-config-grid">
            {/* Strategy & Asset Selection */}
            <Card variant="surface-1">
              <CardHeader
                title="Strategy & Assets"
                subtitle="Select algorithmic logic and universe"
                action={<Badge variant="profit" size="sm">Phase 2 Target</Badge>}
              />
              <CardContent className="quant-form-stack">
                <div className="quant-form-group">
                  <label className="caption-label">Algorithm Strategy</label>
                  <div className="quant-mock-select">
                    <span>SmaCrossoverAlgorithm (QCAlgorithm)</span>
                    <Badge variant="neutral" size="sm">NSE Daily</Badge>
                  </div>
                  <span className="meta-text">
                    5-stock dual moving average crossover with Zerodha brokerage model.
                  </span>
                </div>

                <div className="quant-form-group">
                  <div className="flex items-center justify-between">
                    <label className="caption-label">Indian Equity Universe</label>
                    <span className="meta-text">6 of 6 Available</span>
                  </div>
                  <div className="quant-symbol-selector">
                    {availableSymbols.map((s) => (
                      <div key={s.symbol} className="quant-symbol-row is-selected">
                        <div className="flex items-center gap-2">
                          <input type="checkbox" defaultChecked readOnly />
                          <span className="quant-symbol-code font-mono">{s.symbol}</span>
                          <span className="quant-symbol-name">{s.name}</span>
                        </div>
                        <Badge variant="profit" size="sm">Active</Badge>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Parameters & Capital */}
            <div className="quant-config-col">
              <Card variant="surface-1">
                <CardHeader
                  title="Capital & Portfolio Constraints"
                  subtitle="Initial allocation and brokerage model"
                />
                <CardContent className="quant-form-stack">
                  <div className="quant-form-group">
                    <label className="caption-label">Starting Cash (INR)</label>
                    <div className="quant-input-addon">
                      <IndianRupee size={15} className="text-muted" />
                      <input
                        type="text"
                        className="quant-input font-mono"
                        defaultValue="10,00,000"
                        readOnly
                      />
                      <Badge variant="neutral" size="sm">INR</Badge>
                    </div>
                  </div>

                  <div className="quant-form-group">
                    <label className="caption-label">Brokerage Fee Model</label>
                    <div className="quant-mock-select">
                      <span>Zerodha Custom Brokerage Model</span>
                      <Shield size={14} className="text-profit" />
                    </div>
                    <span className="meta-text">
                      STT, turnover charges, GST, SEBI charges, stamp duty accurately modeled.
                    </span>
                  </div>

                  <div className="quant-form-group">
                    <label className="caption-label">Moving Average Parameters</label>
                    <div className="quant-params-inline">
                      <div className="quant-param-box">
                        <span className="meta-text">Fast SMA</span>
                        <span className="font-mono text-md font-bold">20 Days</span>
                      </div>
                      <div className="quant-param-box">
                        <span className="meta-text">Slow SMA</span>
                        <span className="font-mono text-md font-bold">50 Days</span>
                      </div>
                      <div className="quant-param-box">
                        <span className="meta-text">Weight / Asset</span>
                        <span className="font-mono text-md font-bold">18% Max</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
                <CardFooter>
                  <span className="meta-text">Immutable canonical code; runtime config will be injected in Phase 3.</span>
                  <Button
                    variant="primary"
                    size="md"
                    icon={<Play size={14} />}
                    onClick={() => setActiveTab('execution')}
                  >
                    Proceed to Execution
                  </Button>
                </CardFooter>
              </Card>

              {/* Informational Callout */}
              <div className="quant-config-notice">
                <Info size={16} className="text-accent" />
                <p className="meta-text">
                  <strong>Phase 1 Visual Foundation:</strong> Interactive parameter binding and non-mutating
                  runtime execution will be activated in Phase 2 & Phase 3.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: EXECUTION */}
      {activeTab === 'execution' && (
        <div className="quant-tab-content">
          <Card variant="surface-1">
            <CardHeader
              title="Execution Monitor"
              subtitle="LEAN engine process tracking and runtime status"
              action={<Badge variant="profit" size="sm">Engine Standby</Badge>}
            />
            <CardContent>
              <div className="quant-execution-preview">
                <div className="quant-exec-status-card">
                  <div className="flex items-center gap-3">
                    <div className="quant-engine-status-dot" />
                    <div>
                      <h4 className="quant-exec-title">Ready for Execution</h4>
                      <p className="meta-text">Engine binary: QuantConnect.Lean.Launcher.exe</p>
                    </div>
                  </div>
                  <Button
                    variant="primary"
                    size="md"
                    icon={<Play size={14} />}
                    onClick={() => setActiveTab('results')}
                  >
                    View Last Verified Results
                  </Button>
                </div>

                <div className="quant-console-preview">
                  <div className="quant-console-bar">
                    <span className="caption-label">Process Log Stream Preview</span>
                    <Badge variant="neutral" size="sm">PowerShell Orchestration</Badge>
                  </div>
                  <pre className="quant-terminal-text font-mono">
{`[SYSTEM] Environment variables verified:
         INDIAN_TRADING_SYSTEM_ROOT = D:\\LeanT\\IndianTradingSystem
         INDIAN_TRADING_SYSTEM_DATA_DIR = D:\\LeanT\\IndianTradingSystem\\data
         PYTHONNET_PYDLL = D:\\LeanT\\IndianTradingSystem\\.venv\\...\\python311.dll
[ENGINE] LEAN Engine Launcher v2.5.0.0
[ALGO]   SmaCrossoverAlgorithm initialized with 5 symbols
[STATUS] Ready to execute via Phase 3 non-mutating runtime adapter`}
                  </pre>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* TAB 3: RESULTS */}
      {activeTab === 'results' && (
        <div className="quant-tab-content">
          <div className="quant-results-overview">
            <div className="quant-results-header-card">
              <div>
                <Badge variant="profit" size="sm">Verified Checkpoint Result</Badge>
                <h2 className="heading-section mt-1">SmaCrossoverAlgorithm — 5-Stock Portfolio Run</h2>
                <p className="meta-text">
                  Source: <code className="font-mono">D:\LeanT\Lean\Launcher\bin\Debug\results\SmaCrossoverAlgorithm-summary.json</code>
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
                <span className="caption-label">Compounded Annual Return (CAGR)</span>
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
                <span className="caption-label">Zerodha Brokerage Fees</span>
                <span className="metric-value font-mono">₹18,579</span>
                <span className="meta-text">Deducted from Equity</span>
              </div>
              <div className="quant-stat-card">
                <span className="caption-label">Total Closed Trades</span>
                <span className="metric-value font-mono">119</span>
                <span className="meta-text">245 Order Events</span>
              </div>
            </div>

            <Card variant="surface-1">
              <CardHeader
                title="Results Dashboard Integration Notice"
                subtitle="Scheduled for Phase 5"
              />
              <CardContent>
                <p className="quant-card-text">
                  Full interactive equity curve charts, drawdown plots, trade tables, and order events
                  will be connected in <strong>Phase 5</strong> directly from the verified 30KB summary
                  and 2.96MB result JSON files.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
};
