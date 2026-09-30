import React from 'react';
import { Lock } from 'lucide-react';
import { Badge } from '../../../components/common/Badge';
import './UnsupportedControlsPanel.css';

export const UnsupportedControlsPanel: React.FC = () => {
  const unsupportedItems = [
    {
      id: 'stop_loss',
      name: 'Dynamic Stop Loss & ATR Trailing Stop',
      description: 'Automated trailing stop loss based on Average True Range multiples.',
      status: 'Coming Soon',
      category: 'Risk Management',
    },
    {
      id: 'take_profit',
      name: 'Profit Target & Partial Scaling',
      description: 'Staged profit-taking at 2R and 3R risk-reward milestones.',
      status: 'Not Implemented',
      category: 'Exit Rules',
    },
    {
      id: 'slippage_model',
      name: 'Nonlinear Slippage & Impact Model',
      description: 'Market-impact and spread slippage estimation for larger order sizes.',
      status: 'Coming Soon',
      category: 'Execution',
    },
    {
      id: 'margin_leverage',
      name: 'Intraday MIS Leverage & Short Selling',
      description: 'Margin intraday square-off (MIS) multiplier and overnight haircut rules.',
      status: 'Not Implemented',
      category: 'Margin',
    },
    {
      id: 'parameter_optimization',
      name: 'Grid & Bayesian Parameter Optimization',
      description: 'Automated hyperparameter search across fast/slow period combinations.',
      status: 'Roadmap',
      category: 'Research',
    },
    {
      id: 'walk_forward',
      name: 'Walk-Forward Out-of-Sample Testing',
      description: 'Rolling in-sample training and out-of-sample forward efficiency validation.',
      status: 'Roadmap',
      category: 'Validation',
    },
  ];

  return (
    <div className="quant-unsupported-panel">
      <div className="quant-selector-header">
        <div className="flex items-center gap-2">
          <label className="caption-label">Advanced Quant Capabilities</label>
          <Badge variant="coming-soon" size="sm">
            Coming Soon / Not Implemented
          </Badge>
        </div>
        <span className="meta-text">Read-only preview</span>
      </div>

      <div className="quant-unsupported-grid">
        {unsupportedItems.map((item) => (
          <div key={item.id} className="quant-unsupported-card">
            <div className="quant-unsupported-top">
              <div className="flex items-center gap-2">
                <Lock size={12} className="text-muted" />
                <span className="quant-unsupported-name">{item.name}</span>
              </div>
              <Badge variant="coming-soon" size="sm">
                {item.status}
              </Badge>
            </div>
            <p className="quant-unsupported-desc">{item.description}</p>
            <div className="quant-unsupported-footer">
              <span className="quant-unsupported-cat">{item.category}</span>
              <span className="meta-text">Awaiting Engine Support</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
