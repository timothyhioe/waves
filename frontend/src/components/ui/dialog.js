import React from 'react';
import './dialog.css';

export const Dialog = ({ open, onOpenChange, children }) => {
  if (!open) return null;

  return (
    <div className="dialog-overlay" onClick={() => onOpenChange(false)}>
      <div className="dialog-content" onClick={(e) => e.stopPropagation()}>
        {children}
      </div>
    </div>
  );
};

export const DialogContent = ({ children, className = '' }) => {
  return <div className={`dialog-inner ${className}`}>{children}</div>;
};

export const DialogHeader = ({ children }) => {
  return <div className="dialog-header">{children}</div>;
};

export const DialogTitle = ({ children }) => {
  return <h2 className="dialog-title">{children}</h2>;
};

export const DialogDescription = ({ children }) => {
  return <p className="dialog-description">{children}</p>;
};

export const DialogFooter = ({ children }) => {
  return <div className="dialog-footer">{children}</div>;
};
