import pandas as pd, numpy as np, argparse
from datetime import datetime
import math, os

def _Phi(x): 
    return 0.5*(1.0+math.erf(x/math.sqrt(2.0)))
def bs_price(S,K,T,r,q,sigma,typ='C'):
    if T<=0: return max(0.0,S-K) if typ.upper()=='C' else max(0.0,K-S)
    if sigma<=0: 
        F = S*math.exp((r-q)*T); df = math.exp(-r*T)
        return df*max(0.0,F-K) if typ.upper()=='C' else df*max(0.0,K-F)
    d1 = (math.log(S/K)+(r-q+0.5*sigma*sigma)*T)/(sigma*math.sqrt(T))
    d2 = d1 - sigma*math.sqrt(T)
    df_r = math.exp(-r*T); df_q = math.exp(-q*T)
    return df_q*S*_Phi(d1)-df_r*K*_Phi(d2) if typ.upper()=='C' else df_r*K*_Phi(-d2)-df_q*S*_Phi(-d1)
def implied_vol_bs(price,S,K,T,r,q,typ='C',tol=1e-8,max_iter=200,lo=1e-4,hi=5.0):
    df_r = math.exp(-r*T); df_q = math.exp(-q*T)
    lower = max(0.0, df_q*S - df_r*K) if typ.upper()=='C' else max(0.0, df_r*K - df_q*S)
    upper = df_q*S if typ.upper()=='C' else df_r*K
    if price < lower-1e-12 or price > upper+1e-12: return float('nan')
    a,b=lo,hi
    fa = bs_price(S,K,T,r,q,a,typ)-price
    fb = bs_price(S,K,T,r,q,b,typ)-price
    if fa==0: return a
    if fb==0: return b
    if fa*fb>0:
        b*=2.0; fb = bs_price(S,K,T,r,q,b,typ)-price
        if fa*fb>0: return float('nan')
    for _ in range(max_iter):
        m=0.5*(a+b); fm = bs_price(S,K,T,r,q,m,typ)-price
        if abs(fm)<tol or (b-a)<tol: return max(lo,min(m,b))
        if fa*fm<=0: b,fb=m,fm
        else: a,fa=m,fm
    return 0.5*(a+b)

def parse_date(s):
    for fmt in ("%Y-%m-%d","%m/%d/%Y","%Y/%m/%d"):
        try: return datetime.strptime(str(s), fmt).date()
        except: pass
    return None

def main(in_csv, snapshot="1545", r=0.03, q=0.0, out_csv="data/cboe_normalized.csv"):
    df = pd.read_csv(in_csv)
    iv_col = f"implied_volatility_{snapshot}" if f"implied_volatility_{snapshot}" in df.columns else None
    S_col  = f"active_underlying_price_{snapshot}" if f"active_underlying_price_{snapshot}" in df.columns else None

    df["bid_eod"] = pd.to_numeric(df["bid_eod"], errors="coerce")
    df["ask_eod"] = pd.to_numeric(df["ask_eod"], errors="coerce")
    df["mid"] = (df["bid_eod"] + df["ask_eod"]) / 2.0

    df["quote_date_dt"] = df["quote_date"].apply(parse_date)
    df["expiration_dt"] = df["expiration"].apply(parse_date)
    dte = (pd.to_datetime(df["expiration_dt"]) - pd.to_datetime(df["quote_date_dt"])).dt.days
    df["T"] = np.maximum(dte/365.0, 1.0/365.0)

    if S_col and S_col in df.columns:
        S = pd.to_numeric(df[S_col], errors="coerce")
    else:
        ub = pd.to_numeric(df.get("underlying_bid_eod", np.nan), errors="coerce")
        ua = pd.to_numeric(df.get("underlying_ask_eod", np.nan), errors="coerce")
        S = (ub + ua) / 2.0
    df["S"] = S
    df["r"] = r; df["q"] = q

    F = df["S"] * np.exp((df["r"] - df["q"]) * df["T"])
    df["k"] = np.log(df["strike"] / F)

    def solve(row):
        if any(pd.isna([row["S"],row["strike"],row["T"],row["mid"]])): return np.nan
        return implied_vol_bs(row["mid"], float(row["S"]), float(row["strike"]), float(row["T"]), float(row["r"]), float(row["q"]), row["option_type"])
    df["iv"] = df.apply(solve, axis=1)
    if iv_col: df["iv_vendor"] = pd.to_numeric(df[iv_col], errors="coerce")

    out_cols = [c for c in [
        "quote_date","underlying_symbol","root","expiration","strike","option_type",
        "bid_eod","ask_eod","mid","trade_volume","open_interest",
        "S","r","q","T","k","iv","iv_vendor"
    ] if c in df.columns or c in ["mid","S","r","q","T","k","iv","iv_vendor"]]
    out = df[out_cols].copy()
    out = out[(out["bid_eod"]>0) & (out["ask_eod"]>out["bid_eod"])]
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    out.to_csv(out_csv, index=False)
    print("Saved:", out_csv, "Rows:", len(out))

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_csv", required=True)
    ap.add_argument("--snapshot", default="1545")
    ap.add_argument("--r", type=float, default=0.03)
    ap.add_argument("--q", type=float, default=0.0)
    ap.add_argument("--out_csv", default="data/cboe_normalized.csv")
    args = ap.parse_args()
    main(args.in_csv, args.snapshot, args.r, args.q, args.out_csv)

