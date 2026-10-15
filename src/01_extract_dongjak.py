"""1단계: 전국횡단보도표준데이터에서 서울 동작구 신호 횡단보도를 추출한다.
입력: data/전국횡단보도표준데이터.csv (공공데이터포털에서 내려받은 원본, CP949 인코딩)
출력: output/dongjak_valid.csv"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
raw = pd.read_csv(ROOT / "data" / "전국횡단보도표준데이터.csv", encoding="cp949", low_memory=False)

dj = raw[(raw["시도명"] == "서울특별시") & (raw["시군구명"].str.contains("동작", na=False))].copy()
dj["L"] = pd.to_numeric(dj["횡단보도연장"], errors="coerce")   # 횡단보도 길이(m)
dj["G"] = pd.to_numeric(dj["녹색신호시간"], errors="coerce")   # 보행 녹색신호시간(초)

sig = dj[dj["보행자신호등유무"] == "Y"]
valid = sig[(sig["L"] > 0) & (sig["G"] > 0)].copy()
print(f"동작구 전체 {len(dj)}곳 / 신호 횡단보도 {len(sig)}곳 / 분석 대상 {len(valid)}곳")
(ROOT / "output").mkdir(exist_ok=True)
valid.to_csv(ROOT / "output" / "dongjak_valid.csv", index=False, encoding="utf-8-sig")
