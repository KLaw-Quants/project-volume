# scripts/build_simple_chain.py
import pandas as pd
import sys

IN = sys.argv[1] if len(sys.argv) > 1 else "data/cboe_20230825_norm.csv"
OUT = sys.argv[2] if len(sys.argv) > 2 else "data/sample_options_chain.csv"

df = pd.read_csv(IN)

# 预过滤，避免 S/K/mid 为 0 或 NaN
for c in ["S","strike","mid","bid_eod","ask_eod"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")
df = df[
    (df["S"].notna()) & (df["S"] > 0) &
    (df["strike"].notna()) & (df["strike"] > 0) &
    (df["mid"].notna()) & (df["mid"] > 0) &
    (df["ask_eod"] > df["bid_eod"])
].copy()

dte = (pd.to_datetime(df["expiration"]) - pd.to_datetime(df["quote_date"])).dt.days.clip(lower=1)

out = pd.DataFrame({
  "date": df["quote_date"],
  "underlying": df["underlying_symbol"],
  "S": df["S"],
  "r": df.get("r", 0.03).fillna(0.03),
  "q": df.get("q", 0.0).fillna(0.0),
  "expiry": df["expiration"],
  "dte": dte,
  "K": df["strike"],
  "type": df["option_type"].str.upper().map({"C":"C","P":"P"}),
  "bid": df["bid_eod"],
  "ask": df["ask_eod"],
  "mid": df["mid"],
  "volume": df.get("trade_volume", 0).fillna(0),
  "openInterest": df.get("open_interest", 0).fillna(0)
})
out.to_csv(OUT, index=False)
print(f"Prepared: {OUT}, rows: {len(out)}")
