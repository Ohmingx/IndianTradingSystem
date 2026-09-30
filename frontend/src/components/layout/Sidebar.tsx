import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  PlayCircle,
  Cpu,
  Database,
  BarChart3,
  Radio,
  GitBranch,
  Settings,
  ChevronRight,
  TrendingUp,
} from 'lucide-react';
import { Badge } from '../common/Badge';
import './Sidebar.css';

interface NavItem {
  id: string;
  name: string;
  path: string;
  icon: React.ReactNode;
  badge?: string;
  badgeVariant?: 'coming-soon' | 'neutral' | 'profit';
}

const PRIMARY_NAV_ITEMS: NavItem[] = [
  {
    id: 'dashboard',
    name: 'Dashboard',
    path: '/',
    icon: <LayoutDashboard size={18} />,
  },
  {
    id: 'backtesting',
    name: 'Backtesting',
    path: '/backtesting',
    icon: <PlayCircle size={18} />,
  },
  {
    id: 'strategies',
    name: 'Strategies',
    path: '/strategies',
    icon: <Cpu size={18} />,
  },
  {
    id: 'data',
    name: 'Data Management',
    path: '/data',
    icon: <Database size={18} />,
  },
  {
    id: 'analytics',
    name: 'Analytics',
    path: '/analytics',
    icon: <BarChart3 size={18} />,
  },
  {
    id: 'live-testing',
    name: 'Live Testing',
    path: '/live-testing',
    icon: <Radio size={18} />,
    badge: 'Soon',
    badgeVariant: 'coming-soon',
  },
  {
    id: 'regime-analysis',
    name: 'Regime Analysis',
    path: '/regime-analysis',
    icon: <GitBranch size={18} />,
    badge: 'Soon',
    badgeVariant: 'coming-soon',
  },
  {
    id: 'settings',
    name: 'Settings',
    path: '/settings',
    icon: <Settings size={18} />,
  },
];

interface SidebarProps {
  collapsed?: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed = false }) => {
  return (
    <aside className={`quant-sidebar ${collapsed ? 'is-collapsed' : ''}`}>
      {/* Brand Header */}
      <div className="quant-sidebar-brand">
        <div className="quant-brand-icon">
          <TrendingUp size={20} />
        </div>
        <div className="quant-brand-info">
          <span className="quant-brand-name">LEAN QUANT</span>
          <span className="quant-brand-market">NSE / BSE · India</span>
        </div>
      </div>

      {/* Navigation Section */}
      <div className="quant-sidebar-nav-container">
        <div className="quant-nav-header">
          <span className="caption-label">Core Platform</span>
        </div>

        <nav className="quant-nav-list">
          {PRIMARY_NAV_ITEMS.map((item) => (
            <NavLink
              key={item.id}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                `quant-nav-link ${isActive ? 'is-active' : ''}`
              }
            >
              <span className="quant-nav-icon">{item.icon}</span>
              <span className="quant-nav-label">{item.name}</span>
              {item.badge && (
                <Badge
                  variant={item.badgeVariant || 'neutral'}
                  size="sm"
                  className="quant-nav-badge"
                >
                  {item.badge}
                </Badge>
              )}
              <ChevronRight size={14} className="quant-nav-chevron" />
            </NavLink>
          ))}
        </nav>
      </div>

      {/* System Status Footer */}
      <div className="quant-sidebar-footer">
        <div className="quant-engine-pill">
          <div className="quant-engine-status-dot" />
          <div className="quant-engine-text">
            <span className="quant-engine-label">LEAN Engine v2.5</span>
            <span className="quant-engine-sub">CLR / PythonNet 3.x</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
