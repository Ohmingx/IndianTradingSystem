import React from 'react';
import './Badge.css';

export type BadgeVariant =
  | 'neutral'
  | 'profit'
  | 'loss'
  | 'warning'
  | 'info'
  | 'coming-soon'
  | 'outline';

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  size?: 'sm' | 'md';
  dot?: boolean;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  size = 'md',
  dot = false,
  className = '',
}) => {
  return (
    <span className={`quant-badge quant-badge--${variant} quant-badge--${size} ${className}`}>
      {dot && <span className="quant-badge-dot" />}
      {children}
    </span>
  );
};
