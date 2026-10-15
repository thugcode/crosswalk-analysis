"""3단계: 동작구 횡단보도 가상 노인 보행자 시뮬레이션 (몬테카를로)
모든 가정은 PARAMS에 모여 있음. 값을 바꾸고 다시 실행하면 결과가 재현됨."""
import pandas as pd, numpy as np, sys
PARAMS = dict(
    seed=2026,
    n_virtual=10000,            # 가상 노인 수
    # 일반 노인: 15퍼센타일 0.85m/s (한음 외 2020) 가 되도록 평균 설정, 표준편차는 가정값
    general_p15=0.85, sd=0.20,
    # 이동제약 노인: 평균 0.77m/s (Western & Stathi, Age and Ageing)
    limited_mean=0.77,
    limited_share=0.20,         # 이동제약 노인 비율 (가정값, 민감도 분석 대상)
    delay_min=1.0, delay_max=3.0,  # 녹색 점등 후 출발 지연(초), 균등분포 가정
    min_speed=0.30,
    relaxed_margin=3.0,         # '여유롭게' = 녹색 종료 3초 전까지 도착
    spss_per_crosswalk=20,      # SPSS용 표본: 횡단보도당 가상 보행자 수
)
P = PARAMS; rng = np.random.default_rng(P['seed'])
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; OUT = ROOT / "output"
cw = pd.read_csv(OUT / "dongjak_valid.csv")
cw = cw[['횡단보도관리번호','도로명','소재지지번주소','L','G','차로수','교통섬유무']].reset_index(drop=True)
z15 = 1.0364  # 표준정규 85퍼센타일
gen_mean = P['general_p15'] + z15 * P['sd']

def make_people(n):
    limited = rng.random(n) < P['limited_share']
    v = np.where(limited, rng.normal(P['limited_mean'], P['sd'], n), rng.normal(gen_mean, P['sd'], n))
    v = np.clip(v, P['min_speed'], None)
    d = rng.uniform(P['delay_min'], P['delay_max'], n)
    return limited, v, d

lim, v, d = make_people(P['n_virtual'])
need = d[None, :] + cw.L.values[:, None] / v[None, :]          # 횡단보도 x 사람
def coverage(G):
    G = np.asarray(G)[:, None]
    return (need <= G).mean(1), (need <= G - P['relaxed_margin']).mean(1), ((need <= G) & lim[None,:]).sum(1) / lim.sum()

scen = {
    '현행': cw.G.values,
    'A안_0.85': np.maximum(cw.G.values, np.ceil(7 + cw.L.values/0.85)),
    'B안_0.70': np.maximum(cw.G.values, np.ceil(7 + cw.L.values/0.70)),
}
rows = []
for k, G in scen.items():
    c, r, cl = coverage(G)
    cw[f'{k}_녹색'] = G; cw[f'{k}_완주율'] = c.round(3); cw[f'{k}_여유율'] = r.round(3); cw[f'{k}_이동제약완주율'] = cl.round(3)
    rows.append(dict(시나리오=k, 연장된곳=int((G > cw.G.values).sum()), 추가시간합계_초=int((G - cw.G.values).sum()),
        평균완주율=c.mean(), 평균여유율=r.mean(), 이동제약_평균완주율=cl.mean(),
        완주율85미만_곳=int((c < .85).sum()), 여유율85미만_곳=int((r < .85).sum())))
summ = pd.DataFrame(rows)
cw['연장구간'] = pd.cut(cw.L, [0,10,15,20,30,100], labels=['10m이하','10-15m','15-20m','20-30m','30m초과'])
bylen = cw.groupby('연장구간', observed=True).agg(곳=('L','size'), 현행_완주율=('현행_완주율','mean'), 현행_여유율=('현행_여유율','mean'), A안_여유율=('A안_0.85_여유율','mean'), B안_여유율=('B안_0.70_여유율','mean'))

# SPSS용 개별 관측 파일 (현행 신호 기준)
k = P['spss_per_crosswalk']; idx = np.repeat(np.arange(len(cw)), k)
l2, v2, d2 = make_people(len(idx))
t = d2 + cw.L.values[idx] / v2
spss = pd.DataFrame(dict(횡단보도관리번호=cw['횡단보도관리번호'].values[idx], 연장=cw.L.values[idx], 녹색시간=cw.G.values[idx],
    차로수=cw['차로수'].values[idx], 교통섬=(cw['교통섬유무'].values[idx]=='Y').astype(int), 이동제약=l2.astype(int),
    보행속도=v2.round(3), 출발지연=d2.round(2), 횡단시간=t.round(2),
    완주=(t <= cw.G.values[idx]).astype(int), 여유완주=(t <= cw.G.values[idx]-P['relaxed_margin']).astype(int)))

pd.set_option('display.width', 200)
print('일반 노인 평균속도(유도값)', round(gen_mean,3)); print(summ.round(3).to_string(index=False)); print(bylen.round(3).to_string())
worst = cw.sort_values('현행_여유율').head(10)[['도로명','소재지지번주소','L','G','현행_여유율','A안_0.85_녹색','A안_0.85_여유율']]
print(worst.to_string(index=False))
print('virtual speed p15/mean', np.percentile(v,15).round(3), v.mean().round(3))
cw.to_csv(OUT / '동작구_횡단보도별_시뮬레이션결과.csv', index=False, encoding='utf-8-sig')
spss.to_csv(OUT / '동작구_가상노인_관측자료_SPSS용.csv', index=False, encoding='utf-8-sig')
summ.to_csv(OUT / '시나리오_요약.csv', index=False, encoding='utf-8-sig')
