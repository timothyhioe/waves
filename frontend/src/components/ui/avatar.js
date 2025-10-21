import React from 'react';
import './avatar.css';

export const Avatar = ({ children, className = '' }) => {
  return <div className={`ui-avatar ${className}`}>{children}</div>;
};

export const AvatarImage = ({ src, alt }) => {
  if (!src) return null;
  return <img src={src} alt={alt} className="ui-avatar-image" />;
};

export const AvatarFallback = ({ children, className = '' }) => {
  return <div className={`ui-avatar-fallback ${className}`}>{children}</div>;
};
