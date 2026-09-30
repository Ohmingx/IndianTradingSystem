import React from 'react';
import { LineChart, PieChart, Info } from 'lucide-react';
import { Card, CardHeader, CardContent } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import './AnalyticsPage.css';

export const AnalyticsPage: React.FC = () => {
  return (
    <div className="quant-analytics-view">
      <div className="quant-page-header">
        <div>
          <div className="quant-breadcrumb">
            <span className="caption-label">LEAN Quant Platform</span>
            <span className="quant-breadcrumb-sep">/</span>
            <span className="caption-label text-accent">Performance Analytics</span>
          </div>
          <h1 className="heading-display">Quantitative Analytics & Tearsheets</h1>
          <p className="quant-page-desc">
            Deep-dive performance decomposition, trade distribution, risk metrics, and drawdown analysis.
          </p>
        </div>

        <Badge variant="info" size="md">Phase 5-6 Target</Badge>
      </div>

      <div className="quant-analytics-grid">
        <Card variant="surface-1">
          <CardHeader
            title={
              <div className="flex items-center gap-2">
                <LineChart size={16} className="text-accent" />
                <span>Cumulative Returns & Benchmark Tearsheet</span>
              </div>
            }
            subtitle="Equity curve vs NIFTY 50 benchmark comparison"
          />
          <CardContent>
            <div className="quant-analytics-placeholder-body">
              <p className="quant-card-text">
                This tearsheet will visualize the ~470 equity curve data points from the verified
                <code className="font-mono"> SmaCrossoverAlgorithm-summary.json</code> file.
              </p>
              <div className="quant-metric-mini-row">
                <div className="quant-mini-metric">
                  <span className="caption-label">Sharpe Ratio</span>
                  <span className="font-mono font-bold text-primary">0.512</span>
                </div>
                <div className="quant-mini-metric">
                  <span className="caption-label">Sortino Ratio</span>
                  <span className="font-mono font-bold text-primary">0.576</span>
                </div>
                <div className="quant-mini-metric">
                  <span className="caption-label">Annualized CAGR</span>
                  <span className="font-mono font-bold text-profit">7.583%</span>
                </div>
                <div className="quant-mini-metric">
                  <span className="caption-label">Peak Drawdown</span>
                  <span className="font-mono font-bold text-loss">-19.8%</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card variant="surface-1">
          <CardHeader
            title={
              <div className="flex items-center gap-2">
                <PieChart size={16} className="text-accent" />
                <span>Trade Performance & Exposure Breakdown</span>
              </div>
            }
            subtitle="119 Closed Trades & 245 Orders Decomposition"
          />
          <CardContent>
            <div className="quant-analytics-placeholder-body">
              <p className="quant-card-text">
                Detailed win/loss ratios, holding duration distributions, and profit factor analysis
                derived from <code className="font-mono">SmaCrossoverAlgorithm-order-events.json</code>.
              </p>
              <div className="quant-metric-mini-row">
                <div className="quant-mini-metric">
                  <span className="caption-label">Win Rate</span>
                  <span className="font-mono font-bold text-primary">45.0%</span>
                </div>
                <div className="quant-mini-metric">
                  <span className="caption-label">Profit-Loss Ratio</span>
                  <span className="font-mono font-bold text-primary">2.45</span>
                </div>
                <div className="quant-mini-metric">
                  <span className="caption-label">Total Zerodha Fees</span>
                  <span className="font-mono font-bold text-primary">₹18,579</span>
                </div>
                <div className="quant-mini-metric">
                  <span className="caption-label">Net Profit</span>
                  <span className="font-mono font-bold text-profit">+93.03%</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="quant-arch-callout">
        <Info size={16} className="text-accent" />
        <p>
          <strong>Phase 6 Data Verification Protocol:</strong> Interactive candlestick charts, SMA indicator overlays,
          and monthly return heatmaps will be implemented only after running the explicit schema audit on
          <code className="font-mono"> SmaCrossoverAlgorithm.json</code> (2.96 MB) to verify which series are genuinely present.
        </p>
      </div>
    </div>
  );
};
