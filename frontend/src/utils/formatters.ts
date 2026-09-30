/* ==========================================================================
   Indian Currency and Number Formatting Utilities
   ========================================================================== */

export function formatINR(value: number, includeSymbol = true): string {
  if (isNaN(value)) return includeSymbol ? '₹0' : '0';

  // Indian number grouping (last 3 digits, then groups of 2)
  const isNegative = value < 0;
  const absVal = Math.abs(Math.round(value));
  const s = absVal.toString();

  let formatted = '';
  if (s.length <= 3) {
    formatted = s;
  } else {
    const lastThree = s.substring(s.length - 3);
    const otherNumbers = s.substring(0, s.length - 3);
    const restWithCommas = otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ',');
    formatted = `${restWithCommas},${lastThree}`;
  }

  const sign = isNegative ? '-' : '';
  return includeSymbol ? `${sign}₹${formatted}` : `${sign}${formatted}`;
}

export function getIndianDenominationWord(value: number): string {
  if (value >= 10000000) {
    const cr = (value / 10000000).toFixed(2);
    return `₹${cr} Crores`;
  }
  if (value >= 100000) {
    const lk = (value / 100000).toFixed(2);
    return `₹${lk} Lakhs`;
  }
  if (value >= 1000) {
    const k = (value / 1000).toFixed(1);
    return `₹${k} K`;
  }
  return `₹${value.toLocaleString('en-IN')}`;
}
