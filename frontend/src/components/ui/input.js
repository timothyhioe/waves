import React from 'react';
import './input.css';

export const Input = React.forwardRef(({ 
  className = '',
  type = 'text',
  ...props 
}, ref) => {
  return (
    <input
      ref={ref}
      type={type}
      className={`ui-input ${className}`}
      {...props}
    />
  );
});

Input.displayName = 'Input';
