import csv, math, os
from datetime import datetime
from math import erf, sqrt, log, exp

# ---- 简单的 BS + 二分法反推 IV（稳健、零依赖） ----
def _Phi(x): return 0.5*(1.0 + erf(x/sqrt(2.0)))
def bs_price(S,K,T,r,q,sigma,typ='C'):
    if T<=0: return max(0.0,S-K) if typ.upper()=='C' else max(0.0,K-S)
    if sigma<=0:
        F = S*exp((r-q)*T); df = exp(-r*T)
        return df*max(0.0,F-K) if typ.upper()=='C' else df*max(0.0,K-F)
    d1 = (log(S/K)+(r-q+0.5*sigma*sigma)*T)/(sigma*sqrt(T))
    d2 = d1 - sigma*sqrt(T)
    df_r = exp(-r*T); df_q = exp(-q*T)
    return df_q*S*_Phi(d1)-df_r*K*_Phi(d2) if typ.upper()=='C' else df_r*K*_Phi(-d2)-df_q*S*_Phi(-d1)

def implied_vol_bs(price,S,K,T,r,q,typ='C',tol=1e-8,max_iter=200,lo=1e-4,hi=5.0):
    df_r = exp(-r*T); df_q = exp(-q*T)
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

IN_CSV = "data/sample_options_chain.csv"        # 你可以稍后替换为自己的文件
OUT_CSV = "data/sample_with_iv.csv"

def compute_T(dte: int) -> float:
    return max(1.0/365.0, dte/365.0)

def main():
    rows_out = []
    if not os.path.exists(IN_CSV):
        print("提示：找不到", IN_CSV, "可以先用 scripts/normalize_cboe.py 处理 Cboe CSV 后再跑。")
        return
    with open(IN_CSV,"r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bid = float(row["bid"]); ask = float(row["ask"])
            if not (bid > 0.0 and ask > bid):
                continue
           mid = (bid + ask)/2.0 if "mid" not in row else float(row.get("mid", (bid+ask)/2.0))
           S = float(row["S"]); K = float(row["K"])
           r = float(row.get("r", 0.03)); q = float(row.get("q", 0.0))
           T = compute_T(int(row["dte"]))
           typ = row["type"]

          # --- 关键护栏：跳过不可用行 ---
           if (S <= 0) or (K <= 0) or (mid <= 0) or (ask <= bid):
               continue

           iv = implied_vol_bs(mid, S, K, T, r, q, typ)

           # --- F 加下限，防止 0/负值 ---
           F = S * exp((r - q) * T)
           F = max(F, 1e-12)
           k = math.log(K / F)

            row_out = dict(row)
            row_out["T"] = f"{T:.6f}"
            row_out["iv"] = f"{iv:.6f}" if iv == iv else ""
            row_out["k"] = f"{k:.6f}"
            rows_out.append(row_out)

    with open(OUT_CSV,"w",newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        writer.writeheader(); writer.writerows(rows_out)

    ivs = [float(r["iv"]) for r in rows_out if r.get("iv")]
    ks  = [float(r["k"])  for r in rows_out if r.get("iv")]
    Ts  = [float(r["T"])  for r in rows_out if r.get("iv")]
    if ivs:
        print(f"IV coverage: {len(ivs)} pts, min={min(ivs):.4f}, max={max(ivs):.4f}, mean={sum(ivs)/len(ivs):.4f}")
        print(f"k range: [{min(ks):.3f}, {max(ks):.3f}]")
        print(f"T range: [{min(Ts):.3f}, {max(Ts):.3f}]")
    print('Saved:', OUT_CSV)

if __name__ == "__main__":
    main()

