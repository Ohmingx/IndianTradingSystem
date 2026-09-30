import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, Activity, Clock, ShieldCheck } from 'lucide-react';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { StatusDot } from '../common/StatusDot';
import './TopBar.css';

export const TopBar: React.FC = () => {
  const navigate = useNavigate();

  return (
    <header className="quant-topbar">
      {/* Left side: Context & Market status */}
      <div className="quant-topbar-left">
        <div className="quant-topbar-item">
          <Activity size={14} className="quant-topbar-icon" />
          <span className="quant-topbar-label">Market:</span>
          <span className="quant-topbar-value">NSE / BSE</span>
          <Badge variant="profit" size="sm">India Daily</Badge>
        </div>

        <div className="quant-topbar-divider" />

        <div className="quant-topbar-item">
          <Clock size={14} className="quant-topbar-icon" />
          <span className="quant-topbar-label">TZ:</span>
          <span className="quant-topbar-value font-mono">Asia/Kolkata</span>
        </div>

        <div className="quant-topbar-divider" />

        <div className="quant-topbar-item">
          <ShieldCheck size={14} className="quant-topbar-icon" />
          <span className="quant-topbar-label">Brokerage:</span>
          <span className="quant-topbar-value">Zerodha Model</span>
        </div>
      </div>

      {/* Right side: Engine health & Action */}
      <div className="quant-topbar-right">
        <div className="quant-topbar-item">
          <StatusDot status="online" pulse label="LEAN Engine Ready" />
        </div>

        <div className="quant-topbar-divider" />

        <Button
          variant="primary"
          size="sm"
          icon={<Play size={13} />}
          onClick={() => navigate('/backtesting')}
        >
          Run Backtest
        </Button>
      </div>
    </header>
  );
};
