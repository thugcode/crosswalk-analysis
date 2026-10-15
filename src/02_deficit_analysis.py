"""2단계: 노인 기준(0.85m/s) 적자 횡단보도 판정과 우선 점검 대상 선정.
필요시간 = 7초 + 연장 / 보행속도, 부족시간 = 필요시간 - 녹색신호시간"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
v = pd.read_csv(ROOT / "output" / "dongjak_valid.csv")

for speed in [1.0, 0.85, 0.8, 0.7]:
    need = 7 + v["L"] / speed
    n = int((v["G"] < need).sum())
    print(f"보행속도 {speed}m/s 기준 적자: {n}곳 ({n / len(v):.1%})")

v["부족_0.85"] = (7 + v["L"] / 0.85 - v["G"]).round(1)
v["부족_0.70"] = (7 + v["L"] / 0.70 - v["G"]).round(1)
v["연장구간"] = pd.cut(v["L"], [0, 10, 15, 20, 30, 1000], labels=["10m이하", "10-15m", "15-20m", "20-30m", "30m초과"])
print(v.assign(적자=v["부족_0.85"] > 0).groupby("연장구간", observed=True)["적자"].agg(["size", "mean"]).round(2))

prio = v[v["부족_0.85"] >= 5].sort_values("부족_0.85", ascending=False)
cols = ["횡단보도관리번호", "도로명", "소재지지번주소", "차로수", "L", "G", "부족_0.85", "부족_0.70", "교통섬유무"]
prio[cols].to_csv(ROOT / "output" / "priority_list.csv", index=False, encoding="utf-8-sig")
print(f"우선 점검(5초 이상 부족): {len(prio)}곳, 필요 연장 합계 {prio['부족_0.85'].sum():.0f}초")
