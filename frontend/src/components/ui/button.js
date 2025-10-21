import React from 'react';
import './button.css';

export const Button = React.forwardRef(({ 
  children, 
  variant = 'default', 
  size = 'default',
  className = '',
  disabled = false,
  type = 'button',
  ...props 
}, ref) => {
  return (
    <button
      ref={ref}
      type={type}
      disabled={disabled}
      className={`ui-button ui-button-${variant} ui-button-${size} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
});

Button.displayName = 'Button';
