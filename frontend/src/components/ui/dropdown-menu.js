import React, { useState, useRef, useEffect } from 'react';
import './dropdown-menu.css';

export const DropdownMenu = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  return (
    <div className="dropdown-menu-container" ref={menuRef}>
      {React.Children.map(children, child => {
        if (child.type === DropdownMenuTrigger) {
          return React.cloneElement(child, { onClick: () => setIsOpen(!isOpen) });
        }
        if (child.type === DropdownMenuContent && isOpen) {
          return child;
        }
        return null;
      })}
    </div>
  );
};

export const DropdownMenuTrigger = ({ children, asChild, onClick }) => {
  if (asChild) {
    return React.cloneElement(React.Children.only(children), { onClick });
  }
  return <button onClick={onClick}>{children}</button>;
};

export const DropdownMenuContent = ({ children, align = 'start' }) => {
  return (
    <div className={`dropdown-menu-content dropdown-menu-${align}`}>
      {children}
    </div>
  );
};

export const DropdownMenuItem = ({ children, onClick, className = '' }) => {
  return (
    <div className={`dropdown-menu-item ${className}`} onClick={onClick}>
      {children}
    </div>
  );
};

export const DropdownMenuLabel = ({ children }) => {
  return <div className="dropdown-menu-label">{children}</div>;
};

export const DropdownMenuSeparator = () => {
  return <div className="dropdown-menu-separator"></div>;
};
