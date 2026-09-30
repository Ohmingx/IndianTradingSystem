/* ==========================================================================
   Backtesting Configuration Types
   Strictly typed configuration state for LEAN backtest engine
   ========================================================================== */

export interface IndianSymbol {
  symbol: string;         // e.g. "RELIANCE.NS"
  ticker: string;         // e.g. "RELIANCE"
  name: string;           // "Reliance Industries Ltd."
  sector: string;         // "Oil & Gas / Conglomerate"
  lotSize: number;
  availableFrom: string;  // "2018-01-01"
  availableTo: string;    // "2024-06-30"
  inLeanFormat: boolean;  // true
}

export interface StrategyDefinition {
  id: string;
  name: string;
  className: string;
  filePath: string;
  description: string;
  universeType: 'multi-asset' | 'single-asset';
  defaultSymbols: string[];
  supported: boolean;
  notes: string;
}

export interface BacktestConfig {
  strategy: string;
  symbols: string[];
  startDate: string;
  endDate: string;
  startingCapital: number;
  brokerage: string;
  fastPeriod: number;
  slowPeriod: number;
  positionWeight: number; // Decimal (0.18 = 18%)
}

export interface UnsupportedSettings {
  stopLossPercent?: number;
  takeProfitPercent?: number;
  slippageModel?: string;
  leverageRatio?: number;
  enableOptimization?: boolean;
  enableWalkForward?: boolean;
}

export const VERIFIED_INDIAN_SYMBOLS: IndianSymbol[] = [
  {
    symbol: 'RELIANCE.NS',
    ticker: 'RELIANCE',
    name: 'Reliance Industries Ltd.',
    sector: 'Conglomerate / Energy',
    lotSize: 1,
    availableFrom: '2015-01-01',
    availableTo: '2023-12-31',
    inLeanFormat: true,
  },
  {
    symbol: 'TCS.NS',
    ticker: 'TCS',
    name: 'Tata Consultancy Services Ltd.',
    sector: 'IT Services',
    lotSize: 1,
    availableFrom: '2015-01-01',
    availableTo: '2023-12-31',
    inLeanFormat: true,
  },
  {
    symbol: 'INFY.NS',
    ticker: 'INFY',
    name: 'Infosys Ltd.',
    sector: 'IT Services',
    lotSize: 1,
    availableFrom: '2015-01-01',
    availableTo: '2023-12-31',
    inLeanFormat: true,
  },
  {
    symbol: 'HDFCBANK.NS',
    ticker: 'HDFCBANK',
    name: 'HDFC Bank Ltd.',
    sector: 'Banking & Financial Services',
    lotSize: 1,
    availableFrom: '2015-01-01',
    availableTo: '2023-12-31',
    inLeanFormat: true,
  },
  {
    symbol: 'ICICIBANK.NS',
    ticker: 'ICICIBANK',
    name: 'ICICI Bank Ltd.',
    sector: 'Banking & Financial Services',
    lotSize: 1,
    availableFrom: '2015-01-01',
    availableTo: '2023-12-31',
    inLeanFormat: true,
  },
  {
    symbol: 'WIPRO.NS',
    ticker: 'WIPRO',
    name: 'Wipro Ltd.',
    sector: 'IT Services',
    lotSize: 1,
    availableFrom: '2015-01-01',
    availableTo: '2023-12-31',
    inLeanFormat: true,
  },
];

export const AVAILABLE_STRATEGIES: StrategyDefinition[] = [
  {
    id: 'sma_crossover',
    name: 'SMA Dual Crossover (5 Stocks)',
    className: 'SmaCrossoverAlgorithm',
    filePath: 'src/lean_integration/sma_crossover_algorithm.py',
    description:
      'Canonical multi-stock dual SMA crossover (SmaCrossoverAlgorithm). Default universe: RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK with equal 20% weights and Zerodha brokerage.',
    universeType: 'multi-asset',
    defaultSymbols: ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS'],
    supported: true,
    notes: 'Verified baseline — CAGR 7.58%, Sharpe 0.512',
  },
  {
    id: 'wipro_sma',
    name: 'WIPRO SMA (WiproSmaAlgorithm)',
    className: 'WiproSmaAlgorithm',
    filePath: 'src/lean_integration/wipro_sma_algorithm.py',
    description:
      'Separate single-stock algorithm class (WiproSmaAlgorithm), not a variant of SmaCrossoverAlgorithm. Dedicated WIPRO.NS SMA crossover with 100% position weight.',
    universeType: 'single-asset',
    defaultSymbols: ['WIPRO.NS'],
    supported: true,
    notes: 'Separate algorithm file — verified single-stock baseline',
  },
];

/** Matches verified LEAN defaults in sma_crossover_algorithm.py + config.yaml */
export const DEFAULT_BACKTEST_CONFIG: BacktestConfig = {
  strategy: 'sma_crossover',
  symbols: ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS'],
  startDate: '2015-01-01',
  endDate: '2023-12-31',
  startingCapital: 1000000, // ₹10,00,000 INR
  brokerage: 'zerodha',
  fastPeriod: 20,
  slowPeriod: 50,
  positionWeight: 0.2, // 20% per asset (5 × 20% = 100%)
};
