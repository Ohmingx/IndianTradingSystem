import React from 'react';
import { Calendar } from 'lucide-react';
import './PeriodPicker.css';

interface PeriodPickerProps {
  startDate: string;
  endDate: string;
  onChangeStartDate: (date: string) => void;
  onChangeEndDate: (date: string) => void;
}

export const PeriodPicker: React.FC<PeriodPickerProps> = ({
  startDate,
  endDate,
  onChangeStartDate,
  onChangeEndDate,
}) => {
  const presets = [
    { label: 'Full Verified (2015–2023)', start: '2015-01-01', end: '2023-12-31' },
    { label: '5 Years (2019–2023)', start: '2019-01-01', end: '2023-12-31' },
    { label: '3 Years (2021–2023)', start: '2021-01-01', end: '2023-12-31' },
    { label: 'COVID Era (2020–2021)', start: '2020-01-01', end: '2021-12-31' },
  ];

  const start = new Date(startDate);
  const end = new Date(endDate);
  const diffDays = Math.max(
    0,
    Math.round((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)),
  );
  const diffYears = (diffDays / 365.25).toFixed(1);

  return (
    <div className="quant-period-picker">
      <div className="quant-selector-header">
        <label className="caption-label">Backtesting Time Horizon</label>
        <span className="quant-duration-badge font-mono">
          {diffYears} Years (~{Math.round(diffDays * 0.69)} Trading Days)
        </span>
      </div>

      <div className="quant-date-inputs-row">
        <div className="quant-date-box">
          <span className="quant-date-label">Start Date (T₀)</span>
          <div className="quant-date-field">
            <Calendar size={14} className="text-accent" />
            <input
              type="date"
              className="quant-native-date font-mono"
              value={startDate}
              min="2015-01-01"
              max={endDate}
              onChange={(e) => onChangeStartDate(e.target.value)}
            />
          </div>
        </div>

        <div className="quant-date-box">
          <span className="quant-date-label">End Date (T_final)</span>
          <div className="quant-date-field">
            <Calendar size={14} className="text-accent" />
            <input
              type="date"
              className="quant-native-date font-mono"
              value={endDate}
              min={startDate}
              max="2023-12-31"
              onChange={(e) => onChangeEndDate(e.target.value)}
            />
          </div>
        </div>
      </div>

      <div className="quant-preset-chips">
        {presets.map((p) => {
          const isActive = startDate === p.start && endDate === p.end;
          return (
            <button
              key={p.label}
              type="button"
              className={`quant-preset-btn ${isActive ? 'is-active' : ''}`}
              onClick={() => {
                onChangeStartDate(p.start);
                onChangeEndDate(p.end);
              }}
            >
              {p.label}
            </button>
          );
        })}
      </div>
    </div>
  );
};
