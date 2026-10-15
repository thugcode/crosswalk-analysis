"""4단계: 가상 노인 관측자료 회귀분석 (SPSS와 동일한 추정: 로지스틱=최대우도, 선형=OLS).
SPSS로 재현하려면 spss/analysis.sps 를 사용한다."""
from pathlib import Path
import numpy as np, pandas as pd, statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
s = pd.read_csv(ROOT / "output" / "동작구_가상노인_관측자료_SPSS용.csv")

X = sm.add_constant(s[["연장", "녹색시간", "이동제약"]]); y = s["여유완주"]
lg = sm.Logit(y, X).fit(disp=0)
n = len(y); cs = 1 - np.exp(2 * (lg.llnull - lg.llf) / n); nk = cs / (1 - np.exp(2 * lg.llnull / n))
acc = ((lg.predict(X) >= 0.5) == y).mean()
tab = pd.DataFrame({"B": lg.params, "SE": lg.bse, "Exp(B)": np.exp(lg.params),
                    "CI_low": np.exp(lg.conf_int()[0]), "CI_high": np.exp(lg.conf_int()[1]), "p": lg.pvalues}).round(3)
print("[이항 로지스틱] 여유완주 ~ 연장 + 녹색시간 + 이동제약"); print(tab)
print(f"Nagelkerke R2 = {nk:.3f}, 분류 정확도 = {acc:.1%}")

s["연장x이동제약"] = s["연장"] * s["이동제약"]
ols = sm.OLS(s["횡단시간"], sm.add_constant(s[["연장", "이동제약", "연장x이동제약"]])).fit()
print("\n[선형회귀] 횡단시간 ~ 연장 + 이동제약 + 연장x이동제약"); print(ols.params.round(3)); print(f"R2 = {ols.rsquared:.3f}")
b = ols.params
print(f"일반 노인: 1m당 {b['연장']:.2f}초 (≈{1 / b['연장']:.2f}m/s), 이동제약 노인: 1m당 {b['연장'] + b['연장x이동제약']:.2f}초 (≈{1 / (b['연장'] + b['연장x이동제약']):.2f}m/s)")
tab.to_csv(ROOT / "output" / "logit_result.csv", encoding="utf-8-sig")
