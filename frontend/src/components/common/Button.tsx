import React from 'react';
import './Button.css';

export type ButtonVariant = 'primary' | 'secondary' | 'subtle' | 'outline' | 'danger';
export type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  icon?: React.ReactNode;
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  icon,
  isLoading = false,
  disabled,
  className = '',
  ...props
}) => {
  return (
    <button
      className={`quant-btn quant-btn--${variant} quant-btn--${size} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="quant-btn-spinner" />
      ) : icon ? (
        <span className="quant-btn-icon">{icon}</span>
      ) : null}
      <span className="quant-btn-text">{children}</span>
    </button>
  );
};
