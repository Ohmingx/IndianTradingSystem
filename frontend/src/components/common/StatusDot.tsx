import React from 'react';
import './StatusDot.css';

interface StatusDotProps {
  status?: 'online' | 'busy' | 'offline' | 'warning' | 'pending';
  pulse?: boolean;
  label?: string;
  className?: string;
}

export const StatusDot: React.FC<StatusDotProps> = ({
  status = 'online',
  pulse = false,
  label,
  className = '',
}) => {
  return (
    <div className={`quant-status-indicator ${className}`}>
      <span className={`quant-status-dot quant-status-dot--${status} ${pulse ? 'is-pulsing' : ''}`} />
      {label && <span className="quant-status-label">{label}</span>}
    </div>
  );
};
