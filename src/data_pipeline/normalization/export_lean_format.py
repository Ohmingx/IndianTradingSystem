import os
import sys
import zipfile
import csv
from datetime import datetime

def export_to_lean_format(symbol, data_dir=None):
    """
    Reads the normalized CSV for `symbol` and exports it to LEAN's native Equity ZIP format.
    """
    if data_dir is None:
        data_dir = os.environ.get("INDIAN_TRADING_SYSTEM_DATA_DIR", os.path.join(os.getcwd(), "data"))
        
    normalized_file = os.path.join(data_dir, "normalized", f"{symbol}.csv")
    if not os.path.exists(normalized_file):
        print(f"Error: Normalized file not found at {normalized_file}")
        sys.exit(1)
        
    # LEAN format paths
    # data/equity/india/daily/reliance.zip containing reliance.csv
    lean_symbol = symbol.lower() # e.g. reliance.ns
    lean_market = "india"
    lean_resolution = "daily"
    
    out_dir = os.path.join(data_dir, "equity", lean_market, lean_resolution)
    os.makedirs(out_dir, exist_ok=True)
    
    zip_path = os.path.join(out_dir, f"{lean_symbol}.zip")
    csv_filename = f"{lean_symbol}.csv"
    
    # We will write the lines to a string/memory and then put in zip
    lean_lines = []
    
    with open(normalized_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # timestamp format: "2015-01-01 00:00:00+05:30"
            ts_str = row["timestamp"]
            if "+" in ts_str:
                ts_str = ts_str.split("+")[0]
            ts_str = ts_str[:19].strip()
            
            dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            # LEAN expects YYYYMMDD 00:00
            lean_time_str = f"{dt.strftime('%Y%m%d')} 00:00"
            
            # Scale prices by 10000, keep volume as is
            # Rounding to nearest integer after scaling
            o = int(round(float(row["open"]) * 10000))
            h = int(round(float(row["high"]) * 10000))
            l = int(round(float(row["low"]) * 10000))
            c = int(round(float(row["close"]) * 10000))
            v = int(round(float(row["volume"])))
            
            lean_lines.append(f"{lean_time_str},{o},{h},{l},{c},{v}")
            
    # Write to ZIP
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(csv_filename, "\n".join(lean_lines) + "\n")
        
    print(f"Successfully exported {len(lean_lines)} rows to {zip_path}")


if __name__ == "__main__":
    import yaml  # PyYAML
    import pathlib

    # Locate config.yaml relative to this file's project root
    # This file lives at:  <project_root>/src/data_pipeline/normalization/export_lean_format.py
    _this_file = pathlib.Path(__file__).resolve()
    _project_root = _this_file.parent.parent.parent.parent  # up 4 levels to project root
    _config_path = _project_root / "config" / "config.yaml"

    with open(_config_path, "r") as _f:
        _cfg = yaml.safe_load(_f)

    _symbols = _cfg["symbols"]  # e.g. ['RELIANCE.NS', 'TCS.NS', ...]
    print(f"Exporting {len(_symbols)} symbols: {_symbols}")

    for _sym in _symbols:
        export_to_lean_format(_sym)
