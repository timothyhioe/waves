import React, { useState } from 'react';
import './select.css';

export const Select = ({ children, value, onValueChange }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="select-container">
      {React.Children.map(children, child => {
        if (child.type === SelectTrigger) {
          return React.cloneElement(child, { onClick: () => setIsOpen(!isOpen), value });
        }
        if (child.type === SelectContent && isOpen) {
          return React.cloneElement(child, { 
            onSelect: (val) => {
              onValueChange(val);
              setIsOpen(false);
            }
          });
        }
        return null;
      })}
    </div>
  );
};

export const SelectTrigger = ({ children, onClick, value, className = '', id }) => {
  return (
    <button
      id={id}
      type="button"
      className={`select-trigger ${className}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
};

export const SelectValue = ({ placeholder }) => {
  return <span>{placeholder}</span>;
};

export const SelectContent = ({ children, onSelect }) => {
  return (
    <div className="select-content">
      {React.Children.map(children, child => {
        if (child.type === SelectItem) {
          return React.cloneElement(child, { onSelect });
        }
        return child;
      })}
    </div>
  );
};

export const SelectItem = ({ children, value, onSelect }) => {
  return (
    <div
      className="select-item"
      onClick={() => onSelect && onSelect(value)}
    >
      {children}
    </div>
  );
};
