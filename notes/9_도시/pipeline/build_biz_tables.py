"""소상공인365 업종·매출·지역현황 원자료(txt) 정리 + F/G/H 유동인구를 JSON에 병합.

입력: archive/C_data/raw/sbiz365_biz_20260920.txt, sbiz365_footfall_20260920.json
출력: archive/C_data/processed/biz_sbiz365_{count_monthly,sales_monthly,sales_pattern}.csv
      archive/90_derived/biz_sbiz365_summary.csv (구역×업종 요약, 대체매출 플래그)
      archive/90_derived/facilities_sbiz365.csv
"""
import json, csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'archive/C_data/raw'
PROC = ROOT / 'archive/C_data/processed'
DERIV = ROOT / 'archive/90_derived'
MONTHS = ['2025-06','2025-07','2025-08','2025-09','2025-10','2025-11','2025-12','2026-01','2026-02','2026-03','2026-04','2026-05','2026-06']
CDS = {'I21201':'카페','I20101':'백반/한정식','G20404':'슈퍼마켓','G20405':'편의점','S20701':'미용실','I10102':'여관/모텔','I10101':'호텔/리조트','I10103':'펜션','G20503':'정육점','G20509':'반찬/식료품','G21501':'약국'}
LIFE = {'G20404','G20405','S20701','G20503','G20509','G21501','I20101'}   # 생활업종 (백반 포함)
TOUR = {'I21201','I10102','I10101','I10103'}                              # 관광·체류업종
LABEL = {'A_hwango_grid32':'황오동 원도심(격자32)','B_haengbok_hwangchon_digitized':'행복황촌(근사)','C_zone_buffer300':'구역+300m','D_zone':'구역','E_center_r300':'구역중심 300m','F_cityhall_r500':'동천동 시청 500m','G_seongdong_market_r200':'성동시장 200m','H_hwangridan_r300':'황리단길 300m'}
AREA_HA = {'A_hwango_grid32':32.0,'B_haengbok_hwangchon_digitized':16.45,'C_zone_buffer300':106.7,'D_zone':15.9,'E_center_r300':28.3,'F_cityhall_r500':78.5,'G_seongdong_market_r200':12.6,'H_hwangridan_r300':28.3}

# ---- F/G/H 유동인구를 footfall JSON에 병합 (브라우저 추출값)
pop_new = {
 "F_cityhall_r500":{"analyNo":118324756,"note":"경주시청(동천동 800) 중심 반경 500m, 785,398㎡","monthly":{"months":["25.06","25.07","25.08","25.09","25.10","25.11","25.12","26.01","26.02","26.03","26.04","26.05","26.06"],"sel":["49,728","48,448","42,104","44,316","45,100","46,296","47,726","44,669","48,556","47,227","47,372","48,066","48,465"]},"daily_sex_age":{"cols":["일일","남","여","10대","20대","30대","40대","50대","60대+"],"sel":["48,465","28,398","20,067","2,407","3,213","5,169","9,414","12,654","15,607"],"sel_pct":["58.6","41.4","5.0","7.0","11.0","19.0","26.0","32.0"]},"weekday":{"cols":["주중","주말","월","화","수","목","금","토","일"],"sel":["50,074","43,882","50,740","50,631","48,883","49,379","50,742","46,573","41,193"],"sel_pct":["53.3","46.7","15.0","15.0","14.5","14.6","15.0","13.8","12.2"]},"hourly":{"cols":["05~09시","09~12시","12~14시","14~18시","18~23시","23~05시"],"sel":["5,829","7,517","5,806","13,142","13,192","2,976"],"sel_pct":["12.0","15.5","12.0","27.1","27.2","6.1"]},"resident":{"cols":["2025년 상반기","2025년 하반기","2026년 상반기"],"sel":["9,411","9,181","9,145"]},"resident_sex_age":{"sel":["9,144","4,558","4,586","340","760","982","946","1,187","1,850","3,079"]},"worker":{"cols":["2025년 상반기","2025년 하반기","2026년 상반기"],"sel":["8,446","8,565","8,374"]},"worker_sex_age":{"sel":["8,374","4,172","4,202","738","1,343","1,800","2,316","2,177"]}},
 "G_seongdong_market_r200":{"analyNo":118324758,"note":"경주성동시장(성동동 51-1) 중심 반경 200m, 125,664㎡","monthly":{"months":["25.06","25.07","25.08","25.09","25.10","25.11","25.12","26.01","26.02","26.03","26.04","26.05","26.06"],"sel":["14,322","14,706","16,785","13,840","14,788","14,649","14,766","13,247","15,516","14,271","15,330","15,337","14,331"]},"daily_sex_age":{"cols":["일일","남","여","10대","20대","30대","40대","50대","60대+"],"sel":["14,331","7,789","6,542","808","1,082","1,378","2,308","3,152","5,603"],"sel_pct":["54.3","45.7","6.0","8.0","10.0","16.0","22.0","39.0"]},"weekday":{"cols":["주중","주말","월","화","수","목","금","토","일"],"sel":["15,669","10,668","15,950","15,240","15,208","15,335","16,616","11,731","9,607"],"sel_pct":["59.5","40.5","16.0","15.3","15.3","15.4","16.7","11.8","9.6"]},"hourly":{"cols":["05~09시","09~12시","12~14시","14~18시","18~23시","23~05시"],"sel":["2,004","2,786","1,883","3,913","3,033","711"],"sel_pct":["14.0","19.4","13.1","27.3","21.2","5.0"]},"resident":{"cols":["2025년 상반기","2025년 하반기","2026년 상반기"],"sel":["231","224","219"]},"resident_sex_age":{"sel":["220","106","114","4","10","17","15","22","35","117"]},"worker":{"cols":["2025년 상반기","2025년 하반기","2026년 상반기"],"sel":["2,678","2,662","2,658"]},"worker_sex_age":{"sel":["2,658","786","1,872","216","402","528","627","885"]}},
 "H_hwangridan_r300":{"analyNo":118324760,"note":"황리단길 중심(129.2098, 35.8384) 반경 300m, 282,743㎡","monthly":{"months":["25.06","25.07","25.08","25.09","25.10","25.11","25.12","26.01","26.02","26.03","26.04","26.05","26.06"],"sel":["20,597","19,237","23,366","20,603","20,960","22,570","19,946","19,017","24,025","20,360","26,131","24,066","17,366"]},"daily_sex_age":{"cols":["일일","남","여","10대","20대","30대","40대","50대","60대+"],"sel":["17,366","9,051","8,315","1,013","1,801","2,025","2,832","3,355","6,340"],"sel_pct":["52.1","47.9","6.0","10.0","12.0","16.0","19.0","37.0"]},"weekday":{"cols":["주중","주말","월","화","수","목","금","토","일"],"sel":["14,603","25,141","14,479","13,314","14,744","14,169","16,310","27,556","22,728"],"sel_pct":["36.7","63.3","11.7","10.8","12.0","11.5","13.2","22.3","18.4"]},"hourly":{"cols":["05~09시","09~12시","12~14시","14~18시","18~23시","23~05시"],"sel":["1,852","3,454","2,688","4,762","3,652","956"],"sel_pct":["10.7","19.9","15.5","27.4","21.0","5.5"]},"resident":{"cols":["2025년 상반기","2025년 하반기","2026년 상반기"],"sel":["488","493","460"]},"resident_sex_age":{"sel":["459","230","229","6","15","19","25","41","74","279"]},"worker":{"cols":["2025년 상반기","2025년 하반기","2026년 상반기"],"sel":["1,047","1,061","1,061"]},"worker_sex_age":{"sel":["1,061","486","575","264","211","156","175","255"]}},
}
jp = RAW / 'sbiz365_footfall_20260920.json'
j = json.load(open(jp, encoding='utf-8'))
for k, v in pop_new.items():
    j[k] = v
json.dump(j, open(jp, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

# ---- 업종·매출 파싱
biz, ref, fac = {}, {}, {}
for line in open(RAW / 'sbiz365_biz_20260920.txt', encoding='utf-8'):
    line = line.strip()
    if not line or line.startswith('#'): continue
    parts = line.split('|')
    if parts[0] == 'REF':
        ref[parts[1]] = {p.split(':')[0]: [float(x) for x in p.split(':')[1].split()] for p in parts[2:]}
    elif parts[0] == 'FAC':
        fac[parts[1]] = [int(x) for x in parts[2].split()]
    else:
        k, cd = parts[0], parts[1]
        biz.setdefault(k, {})
        if parts[2] == '0':
            biz[k][cd] = None; continue
        rec = {p.split(':')[0]: [float(x) for x in p.split(':')[1].split()] for p in parts[2:]}
        biz[k][cd] = rec

def w(name, header, rows):
    with open(name, 'w', newline='', encoding='utf-8-sig') as f:
        c = csv.writer(f); c.writerow(header); c.writerows(rows)

# 업소수 월별 long
rows = []
for k, v in biz.items():
    for cd, rec in v.items():
        for i, m in enumerate(MONTHS):
            rows.append([k, LABEL[k], cd, CDS[cd], m, 0 if rec is None else int(rec['cnt'][i])])
for cd, r in ref.items():
    for i, m in enumerate(MONTHS):
        rows.append(['REF_hwango', '황오동(행정동)', cd, CDS[cd], m, int(r['cnt_hwango'][i])])
        rows.append(['REF_gyeongju', '경주시', cd, CDS[cd], m, int(r['cnt_gj'][i])])
w(PROC / 'biz_sbiz365_count_monthly.csv', ['area_id','area','tpbiz_cd','tpbiz','month','stores'], rows)

# 매출 월별 long (대체 플래그)
rows = []
for k, v in biz.items():
    for cd, rec in v.items():
        if rec is None: continue
        subst = (max(rec['cnt']) <= 3) or (rec['sales'] == ref[cd]['sales_hwango'])
        for i, m in enumerate(MONTHS):
            rows.append([k, LABEL[k], cd, CDS[cd], m, rec['sales'][i], rec['scnt'][i], 'Y' if subst else 'N'])
for cd, r in ref.items():
    for i, m in enumerate(MONTHS):
        rows.append(['REF_hwango', '황오동(행정동)', cd, CDS[cd], m, r['sales_hwango'][i], '', 'N'])
        rows.append(['REF_gyeongju', '경주시', cd, CDS[cd], m, r['sales_gj'][i], '', 'N'])
w(PROC / 'biz_sbiz365_sales_monthly.csv', ['area_id','area','tpbiz_cd','tpbiz','month','sales_per_store_10kwon','sales_cnt_per_store','substituted_by_dong'], rows)

# 매출 패턴 (요일·시간대·성연령)
rows = []
for k, v in biz.items():
    for cd, rec in v.items():
        if rec is None: continue
        subst = (max(rec['cnt']) <= 3) or (rec['sales'] == ref[cd]['sales_hwango'])
        wk, hr, sa = rec['wk'], rec['hr'], rec['sa']
        rows.append([k, LABEL[k], cd, CDS[cd], 'Y' if subst else 'N', wk[0], wk[1], *wk[2:], *hr, *sa])
w(PROC / 'biz_sbiz365_sales_pattern.csv',
  ['area_id','area','tpbiz_cd','tpbiz','substituted','weekday_pct','weekend_pct','mon','tue','wed','thu','fri','sat','sun',
   'h05_09','h09_12','h12_14','h14_18','h18_23','h23_05','sales_m','sales_f','age10','age20','age30','age40','age50','age60p'], rows)

# 요약: 구역×업종 (26.06 업소수, 13개월 업소수 변화, 업소당 매출 13개월 평균·전년동월비, 주말비율, 20-30대 매출비율)
rows = []
for k, v in biz.items():
    for cd, rec in v.items():
        if rec is None:
            rows.append([k, LABEL[k], cd, CDS[cd], 0, 0, '', '', '', '', '', '']); continue
        subst = (max(rec['cnt']) <= 3) or (rec['sales'] == ref[cd]['sales_hwango'])
        s = rec['sales']; avg = sum(s)/len(s); yoy = (s[-1]/s[0]-1)*100 if s[0] else None
        sa = rec['sa']; tot = sum(sa[2:]); young = (sa[3]+sa[4])/tot*100 if tot else None
        rows.append([k, LABEL[k], cd, CDS[cd], int(rec['cnt'][-1]), int(rec['cnt'][-1]-rec['cnt'][0]),
                     round(avg), None if yoy is None else round(yoy,1), 'Y' if subst else 'N', rec['wk'][1],
                     None if young is None else round(young,1), rec['hr'][4]])
w(DERIV / 'biz_sbiz365_summary.csv',
  ['area_id','area','tpbiz_cd','tpbiz','stores_2606','stores_chg_13mo','sales_per_store_avg','sales_yoy_pct','substituted','weekend_sales_pct','sales_age20_30_pct','sales_18_23_pct'], rows)

# 구역 요약: 생활/관광 업소수, 밀도
rows = []
for k, v in biz.items():
    life = sum(int(r['cnt'][-1]) for cd, r in v.items() if r and cd in LIFE)
    tour = sum(int(r['cnt'][-1]) for cd, r in v.items() if r and cd in TOUR)
    life0 = sum(int(r['cnt'][0]) for cd, r in v.items() if r and cd in LIFE)
    tour0 = sum(int(r['cnt'][0]) for cd, r in v.items() if r and cd in TOUR)
    f = fac.get(k, [None]*7)
    rows.append([k, LABEL[k], AREA_HA[k], life, tour, round(life/(life+tour)*100,1) if life+tour else None,
                 life-life0, tour-tour0, round((life+tour)/AREA_HA[k],1), *f])
w(DERIV / 'biz_sbiz365_area_summary.csv',
  ['area_id','area','area_ha','life_stores_2606','tour_stores_2606','life_share_pct','life_chg_13mo','tour_chg_13mo','stores_per_ha',
   'fac_public','fac_finance','fac_medical','fac_school','fac_bigretail','fac_culture','fac_lodging'], rows)
for r in rows: print(r)
