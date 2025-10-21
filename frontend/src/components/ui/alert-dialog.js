import React from 'react';
import './dialog.css';

export const AlertDialog = ({ open, onOpenChange, children }) => {
  if (!open) return null;

  return (
    <div className="dialog-overlay" onClick={() => onOpenChange(false)}>
      <div className="dialog-content" onClick={(e) => e.stopPropagation()}>
        {children}
      </div>
    </div>
  );
};

export const AlertDialogContent = ({ children }) => {
  return <div className="dialog-inner" style={{ maxWidth: '450px' }}>{children}</div>;
};

export const AlertDialogHeader = ({ children }) => {
  return <div className="dialog-header">{children}</div>;
};

export const AlertDialogTitle = ({ children }) => {
  return <h2 className="dialog-title">{children}</h2>;
};

export const AlertDialogDescription = ({ children }) => {
  return <p className="dialog-description">{children}</p>;
};

export const AlertDialogFooter = ({ children }) => {
  return <div className="dialog-footer">{children}</div>;
};

export const AlertDialogAction = ({ children, className = '', ...props }) => {
  return (
    <button
      className={`ui-button ui-button-default ${className}`}
      style={{ 
        background: className.includes('red') ? '#dc2626' : undefined,
        borderColor: className.includes('red') ? '#dc2626' : undefined 
      }}
      {...props}
    >
      {children}
    </button>
  );
};

export const AlertDialogCancel = ({ children, ...props }) => {
  return (
    <button className="ui-button ui-button-outline" {...props}>
      {children}
    </button>
  );
};
