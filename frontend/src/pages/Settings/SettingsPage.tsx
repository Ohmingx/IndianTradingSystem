import React from 'react';
import { ShieldCheck, Terminal, Bookmark } from 'lucide-react';
import { Card, CardHeader, CardContent } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import './SettingsPage.css';

export const SettingsPage: React.FC = () => {
  return (
    <div className="quant-settings-view">
      <div className="quant-page-header">
        <div>
          <div className="quant-breadcrumb">
            <span className="caption-label">LEAN Quant Platform</span>
            <span className="quant-breadcrumb-sep">/</span>
            <span className="caption-label text-accent">Settings & Environment</span>
          </div>
          <h1 className="heading-display">Platform Settings & Environment</h1>
          <p className="quant-page-desc">
            System paths, QuantConnect LEAN engine configuration, PythonNet CLR bridge, and brokerage fee models.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="profit" dot size="md">System Online</Badge>
          <Badge variant="neutral" size="md">Windows PowerShell</Badge>
        </div>
      </div>

      <div className="quant-settings-grid">
        {/* Environment Variables */}
        <Card variant="surface-1">
          <CardHeader
            title={
              <div className="flex items-center gap-2">
                <Terminal size={16} className="text-accent" />
                <span>Environment Configuration</span>
              </div>
            }
            subtitle="Verified environment variables required by LEAN and runner scripts"
          />
          <CardContent className="quant-settings-stack">
            <div className="quant-setting-item">
              <span className="caption-label">Project Root Directory</span>
              <div className="quant-setting-field font-mono">
                D:\LeanT\IndianTradingSystem
              </div>
              <span className="meta-text">Variable: INDIAN_TRADING_SYSTEM_ROOT</span>
            </div>

            <div className="quant-setting-item">
              <span className="caption-label">Historical Data Directory</span>
              <div className="quant-setting-field font-mono">
                D:\LeanT\IndianTradingSystem\data
              </div>
              <span className="meta-text">Variable: INDIAN_TRADING_SYSTEM_DATA_DIR</span>
            </div>

            <div className="quant-setting-item">
              <span className="caption-label">PythonNet Bridge DLL</span>
              <div className="quant-setting-field font-mono">
                D:\LeanT\IndianTradingSystem\.venv\...\python311.dll
              </div>
              <span className="meta-text">Variable: PYTHONNET_PYDLL (Required for C# ↔ Python interop)</span>
            </div>

            <div className="quant-setting-item">
              <span className="caption-label">LEAN Engine Launcher</span>
              <div className="quant-setting-field font-mono">
                D:\LeanT\Lean\Launcher\bin\Debug\QuantConnect.Lean.Launcher.exe
              </div>
              <span className="meta-text">Compiled LEAN binary v2.5.0.0</span>
            </div>
          </CardContent>
        </Card>

        {/* Brokerage Model & Fees */}
        <Card variant="surface-1">
          <CardHeader
            title={
              <div className="flex items-center gap-2">
                <ShieldCheck size={16} className="text-profit" />
                <span>Zerodha Indian Brokerage Model</span>
              </div>
            }
            subtitle="Accurate fee simulation applied to all equity orders"
          />
          <CardContent className="quant-settings-stack">
            <div className="quant-fee-table">
              <div className="quant-fee-row">
                <span className="quant-fee-name">Equity Delivery Brokerage</span>
                <span className="font-mono text-profit font-bold">₹0 (Zero)</span>
              </div>
              <div className="quant-fee-row">
                <span className="quant-fee-name">Securities Transaction Tax (STT)</span>
                <span className="font-mono text-primary">0.1% Buy & Sell</span>
              </div>
              <div className="quant-fee-row">
                <span className="quant-fee-name">Exchange Turnover Charge</span>
                <span className="font-mono text-primary">0.00345% (NSE)</span>
              </div>
              <div className="quant-fee-row">
                <span className="quant-fee-name">GST</span>
                <span className="font-mono text-primary">18% on (Brokerage + Turnover)</span>
              </div>
              <div className="quant-fee-row">
                <span className="quant-fee-name">SEBI Turnover Charges</span>
                <span className="font-mono text-primary">₹10 / crore</span>
              </div>
              <div className="quant-fee-row">
                <span className="quant-fee-name">Stamp Duty (State)</span>
                <span className="font-mono text-primary">0.015% (Buy only)</span>
              </div>
            </div>

            <div className="quant-checkpoint-info">
              <div className="flex items-center gap-2">
                <Bookmark size={15} className="text-accent" />
                <span className="font-sans font-semibold text-xs text-primary">Baseline Recovery Checkpoint</span>
              </div>
              <p className="meta-text mt-1">
                Tag: <code className="font-mono text-accent">PRE_FRONTEND_CHECKPOINT</code> · Commit: <code className="font-mono">d1e0918</code> (70 files tracked).
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
