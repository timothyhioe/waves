import React from 'react';
import './table.css';

export const Table = ({ children }) => {
  return (
    <table className="ui-table">
      {children}
    </table>
  );
};

export const TableHeader = ({ children, className = '' }) => {
  return <thead className={`ui-table-header ${className}`}>{children}</thead>;
};

export const TableBody = ({ children }) => {
  return <tbody className="ui-table-body">{children}</tbody>;
};

export const TableRow = ({ children, className = '' }) => {
  return <tr className={`ui-table-row ${className}`}>{children}</tr>;
};

export const TableHead = ({ children, className = '' }) => {
  return <th className={`ui-table-head ${className}`}>{children}</th>;
};

export const TableCell = ({ children, className = '', colSpan }) => {
  return <td className={`ui-table-cell ${className}`} colSpan={colSpan}>{children}</td>;
};
