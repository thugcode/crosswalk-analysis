* 동작구 가상 노인 보행자 시뮬레이션 자료 분석 (SPSS 신택스).
* 사용법: [파일] > [데이터 가져오기] > [CSV]로 '동작구_가상노인_관측자료_SPSS용.csv'를 연 뒤(인코딩 UTF-8), 아래를 전체 선택해 실행.

* 1) 이항 로지스틱 회귀: 여유완주.
LOGISTIC REGRESSION VARIABLES 여유완주
  /METHOD=ENTER 연장 녹색시간 이동제약
  /CLASSPLOT
  /PRINT=GOODFIT CI(95)
  /CRITERIA=PIN(0.05) POUT(0.10) ITERATE(20) CUT(0.5).

* 2) 선형회귀 모형 1: 횡단시간.
REGRESSION
  /STATISTICS COEFF OUTS CI(95) R ANOVA
  /DEPENDENT 횡단시간
  /METHOD=ENTER 연장 이동제약.

* 3) 선형회귀 모형 2: 상호작용(집단별 기울기).
COMPUTE 연장x이동제약 = 연장 * 이동제약.
EXECUTE.
REGRESSION
  /STATISTICS COEFF OUTS CI(95) R ANOVA
  /DEPENDENT 횡단시간
  /METHOD=ENTER 연장 이동제약 연장x이동제약.
