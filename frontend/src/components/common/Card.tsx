import React from 'react';
import './Card.css';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  variant?: 'surface-1' | 'surface-2' | 'surface-3';
  elevation?: 'flat' | 'elevated' | 'glow';
  className?: string;
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'surface-1',
  elevation = 'flat',
  className = '',
  ...props
}) => {
  return (
    <div
      className={`quant-card quant-card--${variant} quant-card--${elevation} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

interface CardHeaderProps {
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

export const CardHeader: React.FC<CardHeaderProps> = ({
  title,
  subtitle,
  action,
  className = '',
}) => {
  return (
    <div className={`quant-card-header ${className}`}>
      <div className="quant-card-header-titles">
        <h3 className="quant-card-title">{title}</h3>
        {subtitle && <p className="quant-card-subtitle">{subtitle}</p>}
      </div>
      {action && <div className="quant-card-header-action">{action}</div>}
    </div>
  );
};

export const CardContent: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className = '',
}) => {
  return <div className={`quant-card-content ${className}`}>{children}</div>;
};

export const CardFooter: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className = '',
}) => {
  return <div className={`quant-card-footer ${className}`}>{children}</div>;
};
