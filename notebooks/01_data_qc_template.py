import csv
import math
from math import erf, sqrt, log, exp
import os

# ---------- Black–Scholes + 二分法（稳健、零依赖） ----------
def _Phi(x):
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))

def bs_price(S, K, T, r, q, sigma, typ="C"):
    if T <= 0.0:
        return max(0.0, S - K) if typ.upper() == "C" else max(0.0, K - S)
    if sigma <= 0.0:
        F = S * exp((r - q) * T)
        df = exp(-r * T)
        return df * max(0.0, F - K) if typ.upper() == "C" else df * max(0.0, K - F)
    d1 = (log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    df_r = exp(-r * T)
    df_q = exp(-q * T)
    if typ.upper() == "C":
        return df_q * S * _Phi(d1) - df_r * K * _Phi(d2)
    else:
        return df_r * K * _Phi(-d2) - df_q * S * _Phi(-d1)

def implied_vol_bs(price, S, K, T, r, q, typ="C", tol=1e-8, max_iter=200, lo=1e-4, hi=5.0):
    df_r = exp(-r * T)
    df_q = exp(-q * T)
    lower = max(0.0, df_q * S - df_r * K) if typ.upper() == "C" else max(0.0, df_r * K - df_q * S)
    upper = df_q * S if typ.upper() == "C" else df_r * K
    if price < lower - 1e-12 or price > upper + 1e-12:
        return float("nan")

    a, b = lo, hi
    def f(sig): return bs_price(S, K, T, r, q, sig, typ) - price
    fa, fb = f(a), f(b)
    if fa == 0.0: return a
    if fb == 0.0: return b
    if fa * fb > 0.0:
        b *= 2.0
        fb = f(b)
        if fa * fb > 0.0:
            return float("nan")

    for _ in range(max_iter):
        m = 0.5 * (a + b)
        fm = f(m)
        if abs(fm) < tol or (b - a) < tol:
            return max(lo, min(m, b))
        if fa * fm <= 0.0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    return 0.5 * (a + b)

# ---------- Week1 I/O ----------
IN_CSV = "data/sample_options_chain.csv"   # 由 workflow 的 build_simple_chain.py 生成
OUT_CSV = "data/sample_with_iv.csv"

def compute_T(dte: int) -> float:
    return max(1.0 / 365.0, dte / 365.0)

def main():
    if not os.path.exists(IN_CSV):
        print("提示：找不到", IN_CSV, "请先确认 workflow 已生成该文件。")
        return

    rows_out = []
    with open(IN_CSV, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 基础字段
            try:
                bid = float(row["bid"])
                ask = float(row["ask"])
                S   = float(row["S"])
                K   = float(row["K"])
                r   = float(row.get("r", 0.03))
                q   = float(row.get("q", 0.0))
                T   = compute_T(int(row["dte"]))
                typ = row["type"]
            except Exception:
                # 字段缺失/不可解析 -> 跳过
                continue

            # 护栏：去掉明显坏行
            if not (bid > 0.0 and ask > bid):
                continue
            mid = float(row.get("mid", (bid + ask) / 2.0))
            if (S <= 0.0) or (K <= 0.0) or (mid <= 0.0):
                continue

            # 反推 IV
            iv = implied_vol_bs(mid, S, K, T, r, q, typ)

            # moneyness（给 F 一个极小下限，避免 0）
            F = S * exp((r - q) * T)
            if F <= 0.0:
                continue
            k = log(K / F)

            row_out = dict(row)
            row_out["T"]  = f"{T:.6f}"
            row_out["iv"] = f"{iv:.6f}" if iv == iv else ""  # NaN -> 空
            row_out["k"]  = f"{k:.6f}"
            rows_out.append(row_out)

    if not rows_out:
        print("警告：没有可用行，请检查输入过滤或数据内容。")
        return

    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        writer.writeheader()
        writer.writerows(rows_out)

    ivs = [float(r["iv"]) for r in rows_out if r.get("iv")]
    ks  = [float(r["k"])  for r in rows_out if r.get("iv")]
    Ts  = [float(r["T"])  for r in rows_out if r.get("iv")]
    if ivs:
        print(f"IV coverage: {len(ivs)} pts, min={min(ivs):.4f}, max={max(ivs):.4f}, mean={sum(ivs)/len(ivs):.4f}")
        print(f"k range: [{min(ks):.3f}, {max(ks):.3f}]")
        print(f"T range: [{min(Ts):.3f}, {max(Ts):.3f}]")
    print("Saved:", OUT_CSV)

if __name__ == "__main__":
    main()
