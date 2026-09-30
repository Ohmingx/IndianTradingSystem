import React from 'react';
import { Cpu, Shield } from 'lucide-react';
import { AVAILABLE_STRATEGIES } from '../../../types/backtest';
import type { StrategyDefinition } from '../../../types/backtest';
import { Badge } from '../../../components/common/Badge';
import './StrategySelector.css';

interface StrategySelectorProps {
  selectedStrategyId: string;
  onSelectStrategy: (strategy: StrategyDefinition) => void;
}

export const StrategySelector: React.FC<StrategySelectorProps> = ({
  selectedStrategyId,
  onSelectStrategy,
}) => {
  return (
    <div className="quant-strategy-selector">
      <div className="quant-selector-header">
        <label className="caption-label">Algorithmic Strategy</label>
        <span className="meta-text">Canonical LEAN QCAlgorithm</span>
      </div>

      <div className="quant-strategy-list">
        {AVAILABLE_STRATEGIES.map((strat) => {
          const isSelected = strat.id === selectedStrategyId;
          return (
            <div
              key={strat.id}
              className={`quant-strategy-card ${isSelected ? 'is-selected' : ''}`}
              onClick={() => onSelectStrategy(strat)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') onSelectStrategy(strat);
              }}
            >
              <div className="quant-strategy-top">
                <div className="flex items-center gap-2">
                  <div className={`quant-strategy-radio ${isSelected ? 'is-checked' : ''}`}>
                    {isSelected && <div className="quant-strategy-radio-dot" />}
                  </div>
                  <Cpu size={16} className={isSelected ? 'text-accent' : 'text-muted'} />
                  <div className="quant-strategy-titles">
                    <span className="quant-strategy-name">{strat.name}</span>
                    <code className="quant-strategy-classname font-mono">{strat.className}</code>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="profit" size="sm">
                    Active
                  </Badge>
                  <Badge variant="outline" size="sm">
                    {strat.universeType}
                  </Badge>
                </div>
              </div>

              <p className="quant-strategy-desc">{strat.description}</p>

              <div className="quant-strategy-footer">
                <div className="flex items-center gap-1">
                  <Shield size={12} className="text-profit" />
                  <code className="font-mono text-2xs text-muted">{strat.filePath}</code>
                </div>
                <span className="quant-strategy-note">{strat.notes}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
