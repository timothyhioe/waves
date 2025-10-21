import React from 'react';
import './label.css';

export const Label = React.forwardRef(({ 
  className = '',
  children,
  ...props 
}, ref) => {
  return (
    <label
      ref={ref}
      className={`ui-label ${className}`}
      {...props}
    >
      {children}
    </label>
  );
});

Label.displayName = 'Label';
