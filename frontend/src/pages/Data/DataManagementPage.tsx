import React from 'react';
import { Database, Clock, Archive, ShieldCheck } from 'lucide-react';
import { Card, CardHeader, CardContent } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import './DataManagementPage.css';

export const DataManagementPage: React.FC = () => {
  const verifiedSymbols = [
    {
      symbol: 'RELIANCE',
      name: 'Reliance Industries Ltd.',
      sector: 'Energy / Conglomerate',
      rawCsv: 'data/raw/RELIANCE.csv',
      normCsv: 'data/normalized/RELIANCE.csv',
      leanZip: 'data/equity/india/daily/reliance.zip',
      report: 'data/metadata/RELIANCE_report.json',
      resolution: 'Daily',
      status: 'Ready',
    },
    {
      symbol: 'TCS',
      name: 'Tata Consultancy Services Ltd.',
      sector: 'IT Services',
      rawCsv: 'data/raw/TCS.csv',
      normCsv: 'data/normalized/TCS.csv',
      leanZip: 'data/equity/india/daily/tcs.zip',
      report: 'data/metadata/TCS_report.json',
      resolution: 'Daily',
      status: 'Ready',
    },
    {
      symbol: 'INFY',
      name: 'Infosys Ltd.',
      sector: 'IT Services',
      rawCsv: 'data/raw/INFY.csv',
      normCsv: 'data/normalized/INFY.csv',
      leanZip: 'data/equity/india/daily/infy.zip',
      report: 'data/metadata/INFY_report.json',
      resolution: 'Daily',
      status: 'Ready',
    },
    {
      symbol: 'HDFCBANK',
      name: 'HDFC Bank Ltd.',
      sector: 'Banking & Financial',
      rawCsv: 'data/raw/HDFCBANK.csv',
      normCsv: 'data/normalized/HDFCBANK.csv',
      leanZip: 'data/equity/india/daily/hdfcbank.zip',
      report: 'data/metadata/HDFCBANK_report.json',
      resolution: 'Daily',
      status: 'Ready',
    },
    {
      symbol: 'ICICIBANK',
      name: 'ICICI Bank Ltd.',
      sector: 'Banking & Financial',
      rawCsv: 'data/raw/ICICIBANK.csv',
      normCsv: 'data/normalized/ICICIBANK.csv',
      leanZip: 'data/equity/india/daily/icicibank.zip',
      report: 'data/metadata/ICICIBANK_report.json',
      resolution: 'Daily',
      status: 'Ready',
    },
    {
      symbol: 'WIPRO',
      name: 'Wipro Ltd.',
      sector: 'IT Services',
      rawCsv: 'data/raw/WIPRO.csv',
      normCsv: 'data/normalized/WIPRO.csv',
      leanZip: 'data/equity/india/daily/wipro.zip',
      report: 'Inline / metadata',
      resolution: 'Daily',
      status: 'Ready',
    },
  ];

  return (
    <div className="quant-data-view">
      <div className="quant-page-header">
        <div>
          <div className="quant-breadcrumb">
            <span className="caption-label">LEAN Quant Platform</span>
            <span className="quant-breadcrumb-sep">/</span>
            <span className="caption-label text-accent">Data Management</span>
          </div>
          <h1 className="heading-display">Indian Equity Data Catalog</h1>
          <p className="quant-page-desc">
            Verified historical daily bars, validation reports, and QuantConnect LEAN format ZIP archives for 6 Indian equities.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="profit" dot size="md">6 SYMBOLS READY</Badge>
          <Badge variant="neutral" size="md">Daily Resolution</Badge>
        </div>
      </div>

      {/* Market Spec Cards */}
      <div className="quant-market-specs-row">
        <div className="quant-spec-card">
          <Clock size={16} className="text-accent" />
          <div>
            <span className="caption-label">Trading Hours</span>
            <p className="font-mono text-sm font-bold text-primary">09:15 – 15:30 IST</p>
            <span className="meta-text">NSE / BSE Standard Equity</span>
          </div>
        </div>
        <div className="quant-spec-card">
          <Database size={16} className="text-accent" />
          <div>
            <span className="caption-label">LEAN Integer Scaling</span>
            <p className="font-mono text-sm font-bold text-primary">Price × 10,000</p>
            <span className="meta-text">Fixed point OHLC precision</span>
          </div>
        </div>
        <div className="quant-spec-card">
          <ShieldCheck size={16} className="text-profit" />
          <div>
            <span className="caption-label">Validation Status</span>
            <p className="font-mono text-sm font-bold text-profit">Zero Lookahead Bias</p>
            <span className="meta-text">Full provenance tracked</span>
          </div>
        </div>
      </div>

      {/* Symbols Table */}
      <Card variant="surface-1">
        <CardHeader
          title="Verified Symbol Registry"
          subtitle="All 6 equities verified with raw CSV, normalized CSV, and LEAN ZIP exports"
        />
        <CardContent>
          <div className="quant-table-wrap">
            <table className="quant-data-table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Company & Sector</th>
                  <th>Raw Source</th>
                  <th>Normalized CSV</th>
                  <th>LEAN Daily ZIP</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {verifiedSymbols.map((item) => (
                  <tr key={item.symbol}>
                    <td>
                      <div className="flex items-center gap-2">
                        <span className="quant-chip-dot" />
                        <span className="font-mono font-bold text-primary">{item.symbol}</span>
                      </div>
                    </td>
                    <td>
                      <div className="flex flex-col">
                        <span className="text-sm text-primary">{item.name}</span>
                        <span className="meta-text">{item.sector}</span>
                      </div>
                    </td>
                    <td>
                      <code className="font-mono text-xs text-muted">{item.rawCsv}</code>
                    </td>
                    <td>
                      <code className="font-mono text-xs text-accent">{item.normCsv}</code>
                    </td>
                    <td>
                      <div className="flex items-center gap-1 font-mono text-xs text-primary">
                        <Archive size={12} className="text-muted" />
                        <span>{item.leanZip}</span>
                      </div>
                    </td>
                    <td>
                      <Badge variant="profit" size="sm">{item.status}</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
