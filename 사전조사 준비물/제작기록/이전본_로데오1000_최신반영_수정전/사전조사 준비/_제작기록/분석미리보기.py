# -*- coding: utf-8 -*-
"""분석 방법 미리보기 · 가상 데이터로 여섯 가지 분석을 돌려 결과와 그래프를 만든다.
여기서 나온 숫자는 모두 가상이며 실제 조사 결과가 아니다."""
import json
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import MaxNLocator
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.proportion import proportion_confint
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from sklearn.cluster import HDBSCAN
from scipy.spatial import ConvexHull

HERE = Path(__file__).resolve().parent
FIG = HERE / "그래프"; FIG.mkdir(exist_ok=True)
SEED = 20260912
rng = np.random.default_rng(SEED)

# ── 서체 · 색 (dataviz 기본 팔레트 1~3번 · 흰 바탕에서 all-pairs 검증)
FD = Path("/Users/chokogamja/Library/Fonts")
for f in ["Paperlogy-4Regular.ttf", "Paperlogy-6SemiBold.ttf"]:
    fm.fontManager.addfont(str(FD / f))
REG = FontProperties(fname=str(FD / "Paperlogy-4Regular.ttf"))
BOLD = FontProperties(fname=str(FD / "Paperlogy-6SemiBold.ttf"))
plt.rcParams.update({"font.family": REG.get_name(), "axes.unicode_minus": False,
                     "figure.dpi": 200, "savefig.dpi": 200})
ROUND = ["사전", "1차", "2차"]
COL = {"사전": "#2a78d6", "1차": "#eb6834", "2차": "#1baf7a"}
INK, INK2, MUTED, GRID, BASE, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#ffffff"
NAVY = "#153C68"


def tint(h, t=0.22):
    """막대 옅은 칸: 투명도 대신 흰색과 섞은 단색(격자선이 비치지 않게)"""
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(255 - (255 - v) * t):02x}" for v in c)


def frame(w=6.3, h=3.0):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(BASE); ax.spines["bottom"].set_linewidth(1)
    ax.tick_params(colors=MUTED, labelsize=8.5, length=0)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8); ax.set_axisbelow(True)
    return fig, ax


def finish(fig, name):
    fig.text(0.995, 0.01, "가상 데이터 · 실제 결과 아님", ha="right", va="bottom", color=MUTED, fontsize=7.5)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIG / name, facecolor=SURF); plt.close(fig)
    return str(FIG / name)


R = {"seed": SEED}

# ════════════════════ 1. 윌슨 신뢰구간 · 약산초 인지율
n = np.array([48, 50, 49]); p_true = np.array([0.25, 0.52, 0.66])
k = rng.binomial(n, p_true)
rows = []
for r_, kk, nn in zip(ROUND, k, n):
    wl, wh = proportion_confint(kk, nn, alpha=0.05, method="wilson")
    nl, nh = proportion_confint(kk, nn, alpha=0.05, method="normal")
    rows.append({"회차": r_, "봤다": int(kk), "응답": int(nn), "비율": kk / nn,
                 "윌슨_하한": wl, "윌슨_상한": wh, "왈드_하한": max(nl, 0), "왈드_상한": min(nh, 1)})
R["wilson"] = rows
# 로데오 부스 이용률 (2차 보조 예시)
kb, nb = int(rng.binomial(58, 0.55)), 58
R["wilson_rodeo"] = {"부스안": kb, "전체": nb, "비율": kb / nb,
                     "하한": proportion_confint(kb, nb, method="wilson")[0],
                     "상한": proportion_confint(kb, nb, method="wilson")[1]}
fig, ax = frame(6.3, 3.0)
for i, r in enumerate(rows):
    c = COL[r["회차"]]
    ax.plot([i, i], [r["윌슨_하한"] * 100, r["윌슨_상한"] * 100], color=c, lw=2, solid_capstyle="round")
    ax.plot(i, r["비율"] * 100, "o", ms=9, color=c, mec=SURF, mew=2, zorder=3)
    ax.text(i + 0.09, r["비율"] * 100, f"{r['비율']*100:.0f}%", va="center", fontsize=9, color=INK)
ax.set_xticks(range(3)); ax.set_xticklabels([f"{r['회차']}\n{r['봤다']}/{r['응답']}명" for r in rows], color=INK2, fontsize=9)
ax.set_ylim(0, 100); ax.set_xlim(-0.5, 2.6); ax.set_ylabel("표시를 봤다고 답한 비율(%)", color=INK2, fontsize=8.5)
R["fig_wilson"] = finish(fig, "01_윌슨_약산초인지율.png")

# ════════════════════ 2. 카이제곱 · 로데오 꽁초 처리 위치 × 회차
nrod = [62, 58, 64]; pbin = [0.35, 0.60, 0.72]
bin_ = rng.binomial(nrod, pbin)
tab = np.array([bin_, np.array(nrod) - bin_])  # 행: 수거함, 바닥
chi2, p, dof, exp = stats.chi2_contingency(tab, correction=False)
V = np.sqrt(chi2 / (tab.sum() * (min(tab.shape) - 1)))
R["chi"] = {"표": {"수거함": tab[0].tolist(), "바닥": tab[1].tolist()}, "chi2": chi2, "p": p, "dof": int(dof),
            "V": V, "기대빈도_최소": float(exp.min()), "못봄_제외": [9, 11, 8]}
# 차이나타운 1차 vs 2차 인지 2×2 (표본이 작을 때 Fisher)
t22 = np.array([[26, 14], [18, 20]])
c2, p2, _, e2 = stats.chi2_contingency(t22, correction=False)
_, pf = stats.fisher_exact(t22)
R["chi_china"] = {"표": {"1차": [26, 14], "2차": [18, 20]}, "chi2": c2, "p": p2, "fisher_p": pf, "기대빈도_최소": float(e2.min())}
fig, ax = frame(6.3, 2.6); ax.yaxis.grid(False); ax.xaxis.grid(True, color=GRID, lw=0.8)
ax.spines["bottom"].set_visible(False); ax.spines["left"].set_visible(True); ax.spines["left"].set_color(BASE)
for i, r_ in enumerate(ROUND):
    tot = tab[:, i].sum(); a = tab[0, i] / tot * 100
    y = 2 - i
    ax.barh(y, a, height=0.5, color=COL[r_], edgecolor=SURF, linewidth=1)
    ax.barh(y, 100 - a, left=a, height=0.5, color=tint(COL[r_]), edgecolor=SURF, linewidth=1)
    ax.text(a - 1.5, y, f"수거함 {a:.0f}%", ha="right", va="center", color="#ffffff", fontsize=8.5, fontproperties=BOLD)
    ax.text(a + 1.5, y, f"바닥 {100-a:.0f}%", ha="left", va="center", color=INK, fontsize=8.5)
ax.set_yticks([2, 1, 0]); ax.set_yticklabels([f"{r} (n={tab[:, i].sum()})" for i, r in enumerate(ROUND)], color=INK2, fontsize=9)
ax.set_xlim(0, 100); ax.set_xlabel("처리 끝까지 본 흡연 건 중 비율(%)  ·  진한 칸 = 수거함, 옅은 칸 = 바닥", color=INK2, fontsize=8)
R["fig_chi"] = finish(fig, "02_카이제곱_로데오꽁초.png")

# ════════════════════ 3. t 검정 · 차이나타운 찾기 쉬움 1차 vs 2차 (+선인재단 통과시간)
g1 = rng.choice([1, 2, 3, 4, 5], size=26, p=[0.05, 0.12, 0.30, 0.35, 0.18])
g2 = rng.choice([1, 2, 3, 4, 5], size=18, p=[0.10, 0.20, 0.30, 0.25, 0.15])
t, pt = stats.ttest_ind(g1, g2, equal_var=False)
sp = np.sqrt(((len(g1) - 1) * g1.var(ddof=1) + (len(g2) - 1) * g2.var(ddof=1)) / (len(g1) + len(g2) - 2))
d = (g1.mean() - g2.mean()) / sp
U, pu = stats.mannwhitneyu(g1, g2, alternative="two-sided")
R["t"] = {"1차": {"n": len(g1), "평균": g1.mean(), "표준편차": g1.std(ddof=1), "분포": np.bincount(g1, minlength=6)[1:].tolist()},
          "2차": {"n": len(g2), "평균": g2.mean(), "표준편차": g2.std(ddof=1), "분포": np.bincount(g2, minlength=6)[1:].tolist()},
          "t": t, "p": pt, "d": d, "U": U, "p_mw": pu}
s1 = rng.normal(78, 12, 10).round(); s2 = rng.normal(88, 14, 10).round()
ts, pts = stats.ttest_ind(s1, s2, equal_var=False)
R["t_seonin"] = {"1차": s1.tolist(), "2차": s2.tolist(), "평균1": s1.mean(), "평균2": s2.mean(), "t": ts, "p": pts}
fig, ax = frame(6.3, 2.9)
x = np.arange(1, 6); w = 0.34
for off, lab, g in [(-w / 2 - 0.01, "1차", g1), (w / 2 + 0.01, "2차", g2)]:
    pct = np.bincount(g, minlength=6)[1:] / len(g) * 100
    ax.bar(x + off, pct, width=w, color=COL[lab], edgecolor=SURF, linewidth=1, label=f"{lab} (n={len(g)}, 평균 {g.mean():.2f})")
ax.set_xticks(x); ax.set_xticklabels(["1\n전혀 아니다", "2", "3\n보통", "4", "5\n매우 그렇다"], color=INK2, fontsize=8.5)
ax.set_ylabel("응답 비율(%)", color=INK2, fontsize=8.5)
leg = ax.legend(frameon=False, fontsize=8.5, loc="upper left")
for tx in leg.get_texts(): tx.set_color(INK)
R["fig_t"] = finish(fig, "03_t검정_차이나타운찾기쉬움.png")

# ════════════════════ 4. 일원배치 분산분석 · 굴포천 매력 스티커 사전·1차·2차
probs = {"사전": [0.12, 0.22, 0.36, 0.22, 0.08], "1차": [0.05, 0.14, 0.28, 0.37, 0.16], "2차": [0.03, 0.09, 0.22, 0.40, 0.26]}
ns = {"사전": 41, "1차": 43, "2차": 45}
cnt = {r: rng.multinomial(ns[r], probs[r]).tolist() for r in ROUND}
scores = {r: np.repeat(np.arange(1, 6), cnt[r]) for r in ROUND}
F, pF = stats.f_oneway(*scores.values())
allv = np.concatenate(list(scores.values())); grand = allv.mean()
ssb = sum(len(v) * (v.mean() - grand) ** 2 for v in scores.values()); sst = ((allv - grand) ** 2).sum()
H, pH = stats.kruskal(*scores.values())
lev = stats.levene(*scores.values())
tk = pairwise_tukeyhsd(allv, np.concatenate([[r] * len(scores[r]) for r in ROUND]))
tkt = [{"비교": f"{a} vs {b}", "차이": float(md), "하한": float(lo), "상한": float(hi), "p": float(pa), "유의": bool(rj)}
       for a, b, md, pa, lo, hi, rj in zip(tk.groupsunique[tk._multicomp.pairindices[0]], tk.groupsunique[tk._multicomp.pairindices[1]],
                                            tk.meandiffs, tk.pvalues, tk.confint[:, 0], tk.confint[:, 1], tk.reject)]
R["anova"] = {"스티커": cnt, "평균": {r: float(scores[r].mean()) for r in ROUND},
              "표준편차": {r: float(scores[r].std(ddof=1)) for r in ROUND}, "n": ns,
              "F": F, "p": pF, "eta2": ssb / sst, "H": H, "p_kw": pH, "levene_p": lev.pvalue, "tukey": tkt}
fig, ax = frame(6.3, 3.0)
for i, r_ in enumerate(ROUND):
    v = scores[r_]; m = v.mean(); se = v.std(ddof=1) / np.sqrt(len(v)); ci = stats.t.ppf(0.975, len(v) - 1) * se
    ax.plot([i, i], [m - ci, m + ci], color=COL[r_], lw=2, solid_capstyle="round")
    ax.plot(i, m, "o", ms=9, color=COL[r_], mec=SURF, mew=2, zorder=3)
    ax.text(i + 0.09, m, f"{m:.2f}", va="center", fontsize=9, color=INK)
ax.set_xticks(range(3)); ax.set_xticklabels([f"{r}\nn={ns[r]}" for r in ROUND], color=INK2, fontsize=9)
ax.set_ylim(1, 5); ax.set_yticks([1, 2, 3, 4, 5]); ax.set_xlim(-0.5, 2.6)
ax.set_ylabel("매력 점수 평균과 95% 신뢰구간", color=INK2, fontsize=8.5)
R["fig_anova"] = finish(fig, "04_분산분석_굴포천매력.png")

# ════════════════════ 5. 회귀분석 · 터미널 2층 쉬는 사람 ~ 회차 + 1층 기다리는 사람
recs = []
eff = {"사전": 0, "1차": 4, "2차": 7}
for r_ in ROUND:
    for day in range(4):
        base = rng.integers(20, 70)
        for tm in ["13:00", "13:30", "14:00"]:
            w1 = max(5, int(base + rng.normal(0, 8)))
            y = max(0, round(2 + 0.12 * w1 + eff[r_] + rng.normal(0, 2.5)))
            recs.append({"회차": r_, "날": f"{r_}-{day+1}", "시각": tm, "일층": w1, "이층": y})
df = pd.DataFrame(recs)
m = smf.ols("이층 ~ C(회차, Treatment('사전')) + 일층", data=df).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(df["날"])[0]})
names = {"Intercept": "절편", "C(회차, Treatment('사전'))[T.1차]": "1차 (사전 대비)",
         "C(회차, Treatment('사전'))[T.2차]": "2차 (사전 대비)", "일층": "1층 기다리는 사람 1명당"}
ci = m.conf_int()
R["reg"] = {"n": int(m.nobs), "days": int(df["날"].nunique()), "r2": m.rsquared, "r2adj": m.rsquared_adj,
            "coef": [{"항목": names[k2], "계수": float(m.params[k2]), "하한": float(ci.loc[k2, 0]), "상한": float(ci.loc[k2, 1]),
                      "p": float(m.pvalues[k2])} for k2 in m.params.index],
            "평균": df.groupby("회차")[["일층", "이층"]].mean().reindex(ROUND).round(1).to_dict()}
fig, ax = frame(6.3, 3.2); ax.xaxis.grid(True, color=GRID, lw=0.8)
xs = np.linspace(df["일층"].min(), df["일층"].max(), 20)
for r_ in ROUND:
    sub = df[df["회차"] == r_]
    ax.plot(sub["일층"], sub["이층"], "o", ms=7, color=COL[r_], mec=SURF, mew=1.5, label=r_, alpha=0.95)
    pred = m.params["Intercept"] + m.params["일층"] * xs + (m.params.get(f"C(회차, Treatment('사전'))[T.{r_}]", 0))
    ax.plot(xs, pred, color=COL[r_], lw=2)
ax.set_xlabel("같은 시각 1층에서 기다리는 사람(명)", color=INK2, fontsize=8.5)
ax.set_ylabel("2층에서 쉬는 사람(명)", color=INK2, fontsize=8.5)
ax.yaxis.set_major_locator(MaxNLocator(integer=True))
leg = ax.legend(frameon=False, fontsize=8.5, loc="upper left", title="회차", title_fontsize=8.5)
for tx in leg.get_texts(): tx.set_color(INK)
R["fig_reg"] = finish(fig, "05_회귀_터미널2층.png")

# ════════════════════ 6. HDBSCAN · 약산초 워크숍 제안 위치
cent = {"A": ((50, 22), 16, 3.5), "B": ((24, 62), 12, 4.0), "C": ((75, 70), 10, 4.0)}
pts, true = [], []
for kx, ((cx, cy), nn, sd) in cent.items():
    pts += list(zip(rng.normal(cx, sd, nn), rng.normal(cy, sd, nn))); true += [kx] * nn
pts += list(zip(rng.uniform(5, 95, 8), rng.uniform(5, 95, 8))); true += ["-"] * 8
X = np.array(pts)
lab = HDBSCAN(min_cluster_size=5, min_samples=3).fit_predict(X)
sens = {int(mc): int(len(set(HDBSCAN(min_cluster_size=mc, min_samples=3).fit_predict(X)) - {-1})) for mc in [3, 5, 8, 12]}
order = sorted(set(lab) - {-1}, key=lambda c: -np.sum(lab == c))
letters = {c: "ABCDEFG"[i] for i, c in enumerate(order)}
reasons = {"A": "학교 앞이라 모두 지나가요", "B": "갈림길에서 헷갈려요", "C": "편의점 앞이 밝아요"}
R["hdb"] = {"n": len(X), "군집수": len(order), "잡음": int(np.sum(lab == -1)), "민감도": sens,
            "군집": [{"이름": letters[c], "제안수": int(np.sum(lab == c)),
                      "중심": [float(X[lab == c, 0].mean()), float(X[lab == c, 1].mean())],
                      "대표이유": reasons.get(letters[c], "")} for c in order]}
fig, ax = plt.subplots(figsize=(5.4, 5.0)); fig.patch.set_facecolor(SURF); ax.set_facecolor("#fbfbfa")
for s in ax.spines.values(): s.set_visible(False)
ax.set_xticks([]); ax.set_yticks([])
for xx, yy in [([0, 100], [40, 40]), ([0, 100], [80, 80]), ([35, 35], [0, 100]), ([62, 62], [0, 100])]:
    ax.plot(xx, yy, color="#e6e4dd", lw=9, solid_capstyle="butt", zorder=0)
ax.add_patch(plt.Rectangle((40, 2), 22, 12, color="#d9d7cf", zorder=0)); ax.text(51, 8, "학교", ha="center", va="center", color=INK2, fontsize=8.5)
for c in order:
    P = X[lab == c]
    if len(P) >= 3:
        hull = ConvexHull(P); hp = P[hull.vertices]
        ax.fill(hp[:, 0], hp[:, 1], color=NAVY, alpha=0.10, zorder=1)
    ax.plot(P[:, 0], P[:, 1], "o", ms=7, color=NAVY, mec=SURF, mew=1.5, zorder=3)
    cx, cy = P.mean(0)
    ax.text(cx, cy + 9, f"{letters[c]}  {len(P)}건", ha="center", color=INK, fontsize=9.5, fontproperties=BOLD, zorder=4)
N = X[lab == -1]
ax.plot(N[:, 0], N[:, 1], "o", ms=6, mfc="none", mec=MUTED, mew=1.2, zorder=2, label="어느 군집에도 속하지 않음")
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.set_aspect("equal")
leg = ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.01))
for tx in leg.get_texts(): tx.set_color(INK2)
R["fig_hdb"] = finish(fig, "06_HDBSCAN_약산초제안위치.png")

(HERE / "분석결과.json").write_text(json.dumps(R, ensure_ascii=False, indent=1, default=float))
print(json.dumps({k: v for k, v in R.items() if not k.startswith("fig")}, ensure_ascii=False, indent=1, default=lambda o: round(float(o), 4))[:6000])
