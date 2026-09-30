fills = [
    (1011, 197.0387, 37.69),
    (155, 1299.95, 38.04),
    (800, 249.50, 37.96),
]
for qty, price, fee in fills:
    trade_value = qty * price
    print(f"trade_value=₹{trade_value:,.2f}  fee=₹{fee:,.2f}  fee_pct={fee/trade_value*100:.4f}%")