from pathlib import Path
root = Path(r"d:\LeanT\IndianTradingSystem\backend")
rels = [
    "models/schemas.py",
    "services/runtime_config_manager.py",
    "services/backtest_runner.py",
    "lean_runtime/runtime_algorithm.py",
    "_fix_encoding.py",
]
for rel in rels:
    p = root / rel
    if not p.exists():
        print("missing", rel)
        continue
    b = p.read_bytes()
    if b.count(b"\x00") == 0:
        print("ok", rel)
        continue
    if b[:2] == b"\xff\xfe":
        t = b.decode("utf-16")
    else:
        t = b.decode("utf-16-le")
    for a, c in [("\u2014", "-"), ("\u2013", "-"), ("\u2019", "'"), ("\u201c", '"'), ("\u201d", '"')]:
        t = t.replace(a, c)
    p.write_text(t, encoding="utf-8")
    print("fixed", rel, p.stat().st_size)