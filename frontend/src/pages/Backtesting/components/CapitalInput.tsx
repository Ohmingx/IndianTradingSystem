import React from 'react';
import { IndianRupee } from 'lucide-react';
import { formatINR, getIndianDenominationWord } from '../../../utils/formatters';
import './CapitalInput.css';

interface CapitalInputProps {
  capital: number;
  onChangeCapital: (val: number) => void;
}

export const CapitalInput: React.FC<CapitalInputProps> = ({
  capital,
  onChangeCapital,
}) => {
  const presets = [
    { label: '₹5 Lakhs', val: 500000 },
    { label: '₹10 Lakhs (Default)', val: 1000000 },
    { label: '₹25 Lakhs', val: 2500000 },
    { label: '₹50 Lakhs', val: 5000000 },
    { label: '₹1 Crore', val: 10000000 },
  ];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Strip non-digit characters
    const cleanStr = e.target.value.replace(/[^0-9]/g, '');
    const num = parseInt(cleanStr, 10);
    onChangeCapital(isNaN(num) ? 0 : num);
  };

  return (
    <div className="quant-capital-input-root">
      <div className="quant-selector-header">
        <label className="caption-label">Initial Account Capital</label>
        <span className="quant-denom-badge font-mono">
          {getIndianDenominationWord(capital)}
        </span>
      </div>

      <div className="quant-capital-field">
        <div className="quant-capital-icon-box">
          <IndianRupee size={16} className="text-accent" />
        </div>
        <input
          type="text"
          className="quant-capital-native-input font-mono"
          value={formatINR(capital, false)}
          onChange={handleInputChange}
          placeholder="10,00,000"
        />
        <span className="quant-currency-tag font-mono">INR</span>
      </div>

      <div className="quant-preset-chips">
        {presets.map((p) => {
          const isActive = capital === p.val;
          return (
            <button
              key={p.label}
              type="button"
              className={`quant-preset-btn ${isActive ? 'is-active' : ''}`}
              onClick={() => onChangeCapital(p.val)}
            >
              {p.label}
            </button>
          );
        })}
      </div>
    </div>
  );
};
