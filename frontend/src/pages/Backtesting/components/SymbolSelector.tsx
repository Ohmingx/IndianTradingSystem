import React from 'react';
import { Check } from 'lucide-react';
import { VERIFIED_INDIAN_SYMBOLS } from '../../../types/backtest';
import { Badge } from '../../../components/common/Badge';
import './SymbolSelector.css';

interface SymbolSelectorProps {
  selectedSymbols: string[];
  onToggleSymbol: (symbol: string) => void;
  onSelectAll: () => void;
  onSelect5Default: () => void;
  onClearAll: () => void;
}

export const SymbolSelector: React.FC<SymbolSelectorProps> = ({
  selectedSymbols,
  onToggleSymbol,
  onSelectAll,
  onSelect5Default,
  onClearAll,
}) => {
  return (
    <div className="quant-symbol-selector-root">
      <div className="quant-selector-header">
        <div>
          <label className="caption-label">Indian Equity Universe</label>
          <span className="quant-selected-count font-mono">
            {selectedSymbols.length} of {VERIFIED_INDIAN_SYMBOLS.length} Selected
          </span>
        </div>

        <div className="quant-quick-actions">
          <button
            type="button"
            className="quant-action-link"
            onClick={onSelectAll}
            title="Select all 6 available Indian equity symbols"
          >
            Select All (6)
          </button>
          <span className="quant-action-sep">·</span>
          <button
            type="button"
            className="quant-action-link"
            onClick={onSelect5Default}
            title="Preset: the 5 symbols used by SmaCrossoverAlgorithm (excludes WIPRO.NS)"
          >
            SMA Default 5
          </button>
          <span className="quant-action-sep">·</span>
          <button type="button" className="quant-action-link" onClick={onClearAll}>
            Clear
          </button>
        </div>
      </div>

      <p className="quant-preset-hint meta-text">
        All 6 symbols are available. <strong>SMA Default 5</strong> is only a convenience
        preset matching the canonical multi-stock algorithm universe (excludes WIPRO.NS).
      </p>

      <div className="quant-chips-strip">
        {selectedSymbols.length === 0 ? (
          <span className="meta-text text-loss">
            No assets selected. Select at least 1 symbol to backtest.
          </span>
        ) : (
          selectedSymbols.map((sym) => (
            <span
              key={sym}
              className="quant-selected-chip"
              onClick={() => onToggleSymbol(sym)}
              title="Click to remove"
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') onToggleSymbol(sym);
              }}
            >
              <span className="quant-chip-dot" />
              <span className="font-mono">{sym}</span>
              <span className="quant-chip-remove">×</span>
            </span>
          ))
        )}
      </div>

      <div className="quant-symbol-grid">
        {VERIFIED_INDIAN_SYMBOLS.map((s) => {
          const isSelected = selectedSymbols.includes(s.symbol);
          return (
            <div
              key={s.symbol}
              className={`quant-symbol-card ${isSelected ? 'is-selected' : ''}`}
              onClick={() => onToggleSymbol(s.symbol)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') onToggleSymbol(s.symbol);
              }}
            >
              <div className="flex items-center gap-3">
                <div className={`quant-checkbox ${isSelected ? 'is-checked' : ''}`}>
                  {isSelected ? <Check size={12} strokeWidth={3} /> : null}
                </div>
                <div className="quant-symbol-info">
                  <div className="flex items-center gap-2">
                    <span className="quant-symbol-ticker font-mono">{s.symbol}</span>
                    <Badge variant="profit" size="sm">
                      Daily ZIP
                    </Badge>
                  </div>
                  <span className="quant-symbol-full-name">{s.name}</span>
                </div>
              </div>

              <div className="quant-symbol-meta">
                <span className="quant-sector-badge">{s.sector}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
