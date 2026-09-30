import React from 'react';
import { AlertCircle } from 'lucide-react';
import './SmaParameterForm.css';

interface SmaParameterFormProps {
  fastPeriod: number;
  slowPeriod: number;
  positionWeight: number;
  symbolCount: number;
  onChangeFastPeriod: (val: number) => void;
  onChangeSlowPeriod: (val: number) => void;
  onChangePositionWeight: (val: number) => void;
}

export const SmaParameterForm: React.FC<SmaParameterFormProps> = ({
  fastPeriod,
  slowPeriod,
  positionWeight,
  symbolCount,
  onChangeFastPeriod,
  onChangeSlowPeriod,
  onChangePositionWeight,
}) => {
  const isInvalidPeriods = fastPeriod >= slowPeriod;
  const totalAllocation = symbolCount * positionWeight * 100;
  const isOverAllocated = totalAllocation > 100;

  return (
    <div className="quant-sma-params-root">
      <div className="quant-selector-header">
        <label className="caption-label">Algorithm Parameters (SMA Crossover)</label>
        <span className="meta-text">Canonical constants in src/</span>
      </div>

      <div className="quant-params-grid">
        <div className="quant-param-card">
          <div className="quant-param-header">
            <span className="quant-param-title">Fast Period (T_fast)</span>
            <span className="font-mono text-xs text-accent font-bold">{fastPeriod} Days</span>
          </div>
          <p className="meta-text">Short-term moving average window</p>
          <div className="quant-slider-row">
            <input
              type="range"
              min="5"
              max="60"
              step="1"
              value={fastPeriod}
              onChange={(e) => onChangeFastPeriod(parseInt(e.target.value, 10))}
              className="quant-param-slider"
            />
            <input
              type="number"
              min="5"
              max="60"
              value={fastPeriod}
              onChange={(e) => onChangeFastPeriod(parseInt(e.target.value, 10) || 5)}
              className="quant-param-num-input font-mono"
            />
          </div>
        </div>

        <div className="quant-param-card">
          <div className="quant-param-header">
            <span className="quant-param-title">Slow Period (T_slow)</span>
            <span className="font-mono text-xs text-accent font-bold">{slowPeriod} Days</span>
          </div>
          <p className="meta-text">Long-term baseline trend window</p>
          <div className="quant-slider-row">
            <input
              type="range"
              min="15"
              max="150"
              step="1"
              value={slowPeriod}
              onChange={(e) => onChangeSlowPeriod(parseInt(e.target.value, 10))}
              className="quant-param-slider"
            />
            <input
              type="number"
              min="15"
              max="150"
              value={slowPeriod}
              onChange={(e) => onChangeSlowPeriod(parseInt(e.target.value, 10) || 20)}
              className="quant-param-num-input font-mono"
            />
          </div>
        </div>

        <div className="quant-param-card">
          <div className="quant-param-header">
            <span className="quant-param-title">Position Weight / Symbol</span>
            <span className="font-mono text-xs text-profit font-bold">
              {(positionWeight * 100).toFixed(0)}%
            </span>
          </div>
          <p className="meta-text">Target portfolio equity per open position</p>
          <div className="quant-slider-row">
            <input
              type="range"
              min="0.05"
              max="1"
              step="0.01"
              value={positionWeight}
              onChange={(e) => onChangePositionWeight(parseFloat(e.target.value))}
              className="quant-param-slider"
            />
            <input
              type="number"
              min="5"
              max="100"
              value={Math.round(positionWeight * 100)}
              onChange={(e) => {
                const pct = Math.min(100, Math.max(5, parseInt(e.target.value, 10) || 5));
                onChangePositionWeight(pct / 100);
              }}
              className="quant-param-num-input font-mono"
            />
          </div>
        </div>
      </div>

      {isInvalidPeriods && (
        <div className="quant-param-warning">
          <AlertCircle size={15} className="text-loss" />
          <span className="text-xs text-loss font-semibold">
            Validation Error: Fast period ({fastPeriod}) must be strictly less than Slow period (
            {slowPeriod}).
          </span>
        </div>
      )}

      <div className="quant-allocation-summary">
        <div className="flex items-center justify-between text-xs">
          <span className="meta-text">Portfolio Allocation Budget:</span>
          <span className="font-mono text-primary font-semibold">
            {symbolCount} assets × {(positionWeight * 100).toFixed(0)}% ={' '}
            <span className={isOverAllocated ? 'text-loss font-bold' : 'text-profit font-bold'}>
              {totalAllocation.toFixed(0)}%
            </span>{' '}
            {totalAllocation <= 100 ? (
              <span className="text-muted">({(100 - totalAllocation).toFixed(0)}% cash buffer)</span>
            ) : (
              <span className="text-loss">(Overallocation warning)</span>
            )}
          </span>
        </div>
      </div>
    </div>
  );
};
