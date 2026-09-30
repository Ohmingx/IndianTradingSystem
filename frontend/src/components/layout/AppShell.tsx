import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import './AppShell.css';

export const AppShell: React.FC = () => {
  return (
    <div className="quant-app-shell">
      <Sidebar />
      <div className="quant-app-main">
        <TopBar />
        <main className="quant-app-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
