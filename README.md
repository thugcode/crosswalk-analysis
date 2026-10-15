# 동작구 횡단보도 보행신호 노인 기준 진단

「AI와 함께하는 교통문제 해결을 위한 데이터 분석 공모전」 분석보고서의 분석 코드입니다.
서울 동작구 신호 횡단보도의 녹색신호시간이 노인 보행속도 기준으로 충분한지 진단하고,
가상 노인 보행자 시뮬레이션으로 보행시간 산정식 수정안을 비교합니다.

## 실행 방법

1. 저장소 내려받기

```bash
git clone https://github.com/thugcode/crosswalk-analysis.git
cd crosswalk-analysis
```

2. 라이브러리 설치 (Python 3.9 이상)

```bash
pip install -r requirements.txt
```

3. 전체 분석 실행 (Mac/Linux)

```bash
sh run_all.sh
```

Windows에서는 아래 네 줄을 순서대로 실행합니다.

```bash
python src/01_extract_dongjak.py
python src/02_deficit_analysis.py
python src/03_simulation.py
python src/04_regression.py
```

결과 파일은 `output/` 폴더에 저장되며, 실행 시간은 1분 이내입니다.

## 분석 단계

| 파일 | 내용 | 주요 결과 |
|---|---|---|
| `src/01_extract_dongjak.py` | 원본에서 동작구 신호 횡단보도 추출, 결측 제거 | 분석 대상 횡단보도 |
| `src/02_deficit_analysis.py` | 노인 기준(0.85m/s) 적자 판정, 우선 점검 대상(5초 이상 부족) 선정 | 적자 71곳, 우선 점검 23곳 |
| `src/03_simulation.py` | 가상 노인 1만 명 몬테카를로 시뮬레이션, 산정식(현행·0.85·0.7) 비교 | 횡단보도별 완주율·여유율 |
| `src/04_regression.py` | 가상 관측자료 로지스틱·선형 회귀 | 회귀계수, 집단별 보행속도 |
| `spss/analysis.sps` | 4단계를 SPSS로 재현하는 신택스 | |

## 데이터

- `data/전국횡단보도표준데이터.csv`: 공공데이터포털 전국횡단보도표준데이터 (https://www.data.go.kr/data/15028201/standard.do), CP949 인코딩. 동작구 기준일 2026-08-26.
- 가상 노인 보행속도 모수
  - 일반 노인 15퍼센타일 0.85m/s: 한음 외(2020), 한국ITS학회논문지 19(4)
  - 이동제약 노인 평균 0.77m/s: Western 외(2025), Age and Ageing 54(12)

## 주의

- 시뮬레이션과 회귀분석의 보행자 자료는 선행연구 수치로 생성한 **가상 자료이며 실측이 아닙니다.**
- 근거가 없는 가정값(이동제약 노인 비율 20%, 보행속도 표준편차 0.20, 출발지연 1~3초)은 `src/03_simulation.py`의 `PARAMS`에 모아 두었습니다. 값을 바꾸고 다시 실행하면 민감도를 확인할 수 있습니다.
- 난수 시드(2026)를 고정해 같은 결과가 재현됩니다.
