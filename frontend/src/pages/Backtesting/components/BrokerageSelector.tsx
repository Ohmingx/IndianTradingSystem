import React from 'react';
import { ShieldCheck } from 'lucide-react';
import { Badge } from '../../../components/common/Badge';
import './BrokerageSelector.css';

interface BrokerageSelectorProps {
  selectedBroker: string;
}

export const BrokerageSelector: React.FC<BrokerageSelectorProps> = ({
  selectedBroker = 'zerodha',
}) => {
  void selectedBroker;

  return (
    <div className="quant-brokerage-selector">
      <div className="quant-selector-header">
        <label className="caption-label">Transaction Cost & Fee Model</label>
        <Badge variant="profit" size="sm">
          Zerodha Verified
        </Badge>
      </div>

      <div className="quant-broker-card is-active">
        <div className="quant-broker-top">
          <div className="flex items-center gap-2">
            <ShieldCheck size={16} className="text-profit" />
            <span className="quant-broker-name">Zerodha Securities India</span>
          </div>
          <Badge variant="profit" size="sm">
            Active Model
          </Badge>
        </div>

        <p className="quant-broker-desc">
          Accurate Indian exchange statutory charges implemented in LEAN algorithm:
        </p>

        <div className="quant-fee-grid">
          <div className="quant-fee-cell">
            <span className="meta-text">Brokerage (CNC):</span>
            <span className="font-mono text-profit font-bold">₹0</span>
          </div>
          <div className="quant-fee-cell">
            <span className="meta-text">STT (Delivery):</span>
            <span className="font-mono text-primary">0.1% Buy/Sell</span>
          </div>
          <div className="quant-fee-cell">
            <span className="meta-text">Turnover (NSE):</span>
            <span className="font-mono text-primary">0.00345%</span>
          </div>
          <div className="quant-fee-cell">
            <span className="meta-text">GST on Charges:</span>
            <span className="font-mono text-primary">18.0%</span>
          </div>
        </div>
      </div>

      <div className="quant-disabled-brokers">
        <div className="quant-disabled-broker">
          <span className="text-muted text-xs">Interactive Brokers (India)</span>
          <Badge variant="coming-soon" size="sm">
            Coming Soon
          </Badge>
        </div>
        <div className="quant-disabled-broker">
          <span className="text-muted text-xs">Groww / AngelOne</span>
          <Badge variant="coming-soon" size="sm">
            Coming Soon
          </Badge>
        </div>
      </div>
    </div>
  );
};
