import React, { useState } from 'react';
import { GitBranch, Eye, BarChart2, Cpu } from 'lucide-react';
import { PlaceholderState } from '../../components/common/PlaceholderState';
import type { PlannedItem } from '../../components/common/PlaceholderState';
import './RegimeAnalysisPage.css';

type RegimeTab = 'detection' | 'classification' | 'strategy-response';

export const RegimeAnalysisPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<RegimeTab>('detection');

  const plannedItems: Record<RegimeTab, PlannedItem[]> = {
    detection: [
      {
        name: 'Gaussian Hidden Markov Models (HMM)',
        description: 'Multi-state unsupervised model detecting latent bull, bear, and chop market regimes.',
        status: 'Architecture Ready',
      },
      {
        name: 'GARCH / Realized Volatility Clustering',
        description: 'Conditional heteroskedasticity estimation identifying high vs low volatility clusters.',
        status: 'Planned',
      },
      {
        name: 'Trend Strength & ADX Filtering',
        description: 'Directional movement indexes classifying trending vs mean-reverting states.',
        status: 'Planned',
      },
    ],
    classification: [
      {
        name: 'Four-Quadrant Regime Taxonomy',
        description: 'Categorization into Bull Trending, Bear Trending, High Volatility Chop, Low Volatility Range.',
        status: 'Architecture Ready',
      },
      {
        name: 'Transition Probability Matrix',
        description: 'Empirical probabilities of switching from one market state to another across rolling windows.',
        status: 'Planned',
      },
      {
        name: 'NSE Index Macro Regime Overlay',
        description: 'Incorporating NIFTY 50 and India VIX broad-market indicators into stock-level models.',
        status: 'Planned',
      },
    ],
    'strategy-response': [
      {
        name: 'Dynamic Lookback Adaptation',
        description: 'Shorten SMA lookback during volatile transitions; lengthen during strong trends.',
        status: 'Planned',
      },
      {
        name: 'Regime-Conditional Position Sizing',
        description: 'Scale down leverage during high-volatility chop regimes; maximize in trending regimes.',
        status: 'Under Development',
      },
      {
        name: 'Capital Preservation Kill-Switch',
        description: 'Automatically move portfolio to cash when broad market enters extreme drawdown regime.',
        status: 'Architecture Ready',
      },
    ],
  };

  const architectureNotes: Record<RegimeTab, string[]> = {
    detection: [
      'Unsupervised training requires full historical data preprocessing to avoid look-ahead bias.',
      'Models will be evaluated using walk-forward out-of-sample validation.',
      'Zero synthetic charts: live regime graphs will be rendered once statistical estimators are compiled.',
    ],
    classification: [
      'Regime classification must be calculated strictly on closed bars prior to order generation.',
      'Integration with LEAN will occur via custom QCAlgorithm indicator extensions.',
      'All taxonomy labels will be deterministically derived from verified mathematical models.',
    ],
    'strategy-response': [
      'Adaptive strategy rules will be encapsulated in separate modular LEAN Execution Models.',
      'Non-mutating execution engine will pass regime parameters via isolated runtime configuration.',
      'Safety assertions will ensure portfolio risk never exceeds pre-configured limits.',
    ],
  };

  return (
    <div className="quant-regime-view">
      <div className="quant-page-header">
        <div>
          <div className="quant-breadcrumb">
            <span className="caption-label">LEAN Quant Platform</span>
            <span className="quant-breadcrumb-sep">/</span>
            <span className="caption-label text-accent">Regime Analysis</span>
          </div>
          <h1 className="heading-display">Market Regime Detection & Classification</h1>
          <p className="quant-page-desc">
            Statistical regime detection (HMM, volatility clustering) and regime-adaptive strategy parameterization.
          </p>
        </div>

        {/* Sub-navigation tabs */}
        <div className="quant-tab-strip">
          <button
            className={`quant-tab-btn ${activeTab === 'detection' ? 'is-active' : ''}`}
            onClick={() => setActiveTab('detection')}
          >
            <Eye size={15} />
            <span>1. Detection</span>
          </button>
          <button
            className={`quant-tab-btn ${activeTab === 'classification' ? 'is-active' : ''}`}
            onClick={() => setActiveTab('classification')}
          >
            <BarChart2 size={15} />
            <span>2. Classification</span>
          </button>
          <button
            className={`quant-tab-btn ${activeTab === 'strategy-response' ? 'is-active' : ''}`}
            onClick={() => setActiveTab('strategy-response')}
          >
            <Cpu size={15} />
            <span>3. Strategy Response</span>
          </button>
        </div>
      </div>

      <PlaceholderState
        title={
          activeTab === 'detection'
            ? 'Statistical Regime Detection Engine'
            : activeTab === 'classification'
            ? 'Market State Taxonomy & Transition Matrix'
            : 'Regime-Conditional Strategy Parameters'
        }
        phaseTag="Phase 8 Research & Dev"
        badgeText="Coming Soon"
        description="This module is planned for Phase 8. The mathematical foundations (HMM, GARCH, and volatility clustering) are defined, and will be integrated into the LEAN strategy pipeline with walk-forward testing."
        icon={<GitBranch size={24} />}
        plannedItems={plannedItems[activeTab]}
        architectureNotes={architectureNotes[activeTab]}
      />
    </div>
  );
};
