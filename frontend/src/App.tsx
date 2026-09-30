import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { DashboardPage } from './pages/Dashboard/DashboardPage';
import { BacktestingPage } from './pages/Backtesting/BacktestingPage';
import { StrategiesPage } from './pages/Strategies/StrategiesPage';
import { DataManagementPage } from './pages/Data/DataManagementPage';
import { AnalyticsPage } from './pages/Analytics/AnalyticsPage';
import { LiveTestingPage } from './pages/LiveTrading/LiveTestingPage';
import { RegimeAnalysisPage } from './pages/Regime/RegimeAnalysisPage';
import { SettingsPage } from './pages/Settings/SettingsPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppShell />}>
          {/* Exactly 8 Primary Navigation Routes */}
          <Route index element={<DashboardPage />} />
          <Route path="backtesting/*" element={<BacktestingPage />} />
          <Route path="strategies" element={<StrategiesPage />} />
          <Route path="data" element={<DataManagementPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="live-testing/*" element={<LiveTestingPage />} />
          <Route path="regime-analysis/*" element={<RegimeAnalysisPage />} />
          <Route path="settings" element={<SettingsPage />} />

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
