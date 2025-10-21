import React from 'react';
import { Search, User, Settings, LogOut } from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import './TopBar.css';

export function TopBar({ searchQuery, onSearchChange, onLogout }) {
  // Get user from localStorage
  const userStr = localStorage.getItem('user');
  const user = userStr ? JSON.parse(userStr) : { username: 'User' };
  
  const initials = user.username 
    ? user.username.substring(0, 2).toUpperCase() 
    : 'U';

  return (
    <header className="topbar">
      {/* Search Bar */}
      <div className="topbar-search-container">
        <div className="topbar-search">
          <Search className="topbar-search-icon" size={20} />
          <input
            type="text"
            placeholder="Search for songs, artists, albums..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="topbar-search-input"
          />
        </div>
      </div>

      {/* User Profile */}
      <div className="topbar-user">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="topbar-avatar-button">
              <Avatar className="topbar-avatar">
                <AvatarImage src="" alt="User" />
                <AvatarFallback className="topbar-avatar-fallback">
                  {initials}
                </AvatarFallback>
              </Avatar>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="topbar-dropdown">
            <DropdownMenuLabel>{user.username}</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <User className="mr-2" size={16} />
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Settings className="mr-2" size={16} />
              Settings
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-red-600" onClick={onLogout}>
              <LogOut className="mr-2" size={16} />
              Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
