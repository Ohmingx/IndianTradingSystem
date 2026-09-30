import React from 'react';
import { Badge } from './Badge';
import { Card, CardHeader, CardContent } from './Card';
import './PlaceholderState.css';

export interface PlannedItem {
  name: string;
  description: string;
  status: 'Planned' | 'Architecture Ready' | 'Awaiting Engine API' | 'Under Development';
}

interface PlaceholderStateProps {
  title: string;
  phaseTag: string;
  badgeText?: string;
  description: string;
  icon?: React.ReactNode;
  architectureNotes?: string[];
  plannedItems?: PlannedItem[];
}

export const PlaceholderState: React.FC<PlaceholderStateProps> = ({
  title,
  phaseTag,
  badgeText = 'Coming Soon',
  description,
  icon,
  architectureNotes = [],
  plannedItems = [],
}) => {
  return (
    <div className="quant-placeholder">
      <div className="quant-placeholder-banner">
        <div className="quant-placeholder-header">
          {icon && <div className="quant-placeholder-icon-wrap">{icon}</div>}
          <div className="quant-placeholder-titles">
            <div className="quant-placeholder-badges">
              <Badge variant="coming-soon">{badgeText}</Badge>
              <Badge variant="outline">{phaseTag}</Badge>
            </div>
            <h1 className="quant-placeholder-title">{title}</h1>
            <p className="quant-placeholder-desc">{description}</p>
          </div>
        </div>
      </div>

      <div className="quant-placeholder-grid">
        {plannedItems.length > 0 && (
          <Card variant="surface-1" className="quant-placeholder-card">
            <CardHeader
              title="Planned Core Capabilities"
              subtitle="Scheduled for downstream integration phases"
            />
            <CardContent>
              <div className="quant-planned-list">
                {plannedItems.map((item, idx) => (
                  <div key={idx} className="quant-planned-item">
                    <div className="quant-planned-info">
                      <span className="quant-planned-name">{item.name}</span>
                      <span className="quant-planned-desc">{item.description}</span>
                    </div>
                    <Badge
                      size="sm"
                      variant={
                        item.status === 'Architecture Ready'
                          ? 'info'
                          : item.status === 'Under Development'
                          ? 'warning'
                          : 'neutral'
                      }
                    >
                      {item.status}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {architectureNotes.length > 0 && (
          <Card variant="surface-1" className="quant-placeholder-card">
            <CardHeader
              title="Implementation Prerequisites & Architecture"
              subtitle="Technical constraints before activation"
            />
            <CardContent>
              <ul className="quant-arch-notes">
                {architectureNotes.map((note, idx) => (
                  <li key={idx} className="quant-arch-note">
                    <span className="quant-arch-bullet">0{idx + 1}</span>
                    <span className="quant-arch-text">{note}</span>
                  </li>
                ))}
              </ul>
              <div className="quant-arch-callout">
                <span className="quant-callout-icon">ℹ</span>
                <p>
                  <strong>No Synthetic Data Policy:</strong> This module remains in a structured
                  unimplemented state until verified backend pipelines and engine endpoints are
                  connected. No simulated or fabricated numbers are displayed.
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};
