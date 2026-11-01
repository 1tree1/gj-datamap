from pathlib import Path
import csv,json,statistics,hashlib
B=Path(__file__).parent;R=B.parents[2]
D=json.loads((B/'tourists_live_data.json').read_text(encoding='utf8'))
wd=statistics.mean(r[1] for r in D['dow'][:5]);we=statistics.mean(r[1] for r in D['dow'][5:])
nights=statistics.mean(v[1] for k,v in D['uniq'].items() if k!='note')
rows=list(csv.DictReader((R/'work/20261008_presentation_front/research/data_series/S14_417쪽연구_시민설문_문항별_응답수.csv').open(encoding='utf-8-sig')))
cit=[r for r in rows if r['문항']=='원도심에 필요한 시설(복수)']
names=['쇼핑·여가','대중교통','문화·예술','의료·보건','하천·정보','학교·교육','관광시설','편의시설','주차']
data=dict(tourist=dict(url='https://1tree1.github.io/gj-datamap/tourists.html',retrieved='2026-10-11',htmlSha256=hashlib.sha256((B/'tourists_live.html').read_bytes()).hexdigest(),dow=dict(categories=[r[0] for r in D['dow']],values=[round(r[1]/wd*100,1) for r in D['dow']],raw_daily_visits=[r[1] for r in D['dow']],weekday_average=wd,weekend_ratio=round(we/wd,2),period='2024.09–2026.08',unit='월–금 평균=100'),stay=dict(categories=['데이터랩','관광설문'],day=[round(100-nights,1),44.7],overnight=[round(nights,1),55.3],telecom_period='2025.09–2026.08',survey_year=2024,survey_n=3009,method='데이터랩은 월별 숙박자 비율의 단순평균. 외지인 월별 순방문자와 관광실태조사 내국인 표본은 모집단·집계방식이 다름.'),mode=dict(categories=D['survey']['modes'],values=D['survey']['trend'][-1][2],n=D['survey']['trend'][-1][1],year=2024)),citizen=dict(categories=names,counts=[int(r['건수']) for r in cit],n=52,total_mentions=sum(int(r['건수']) for r in cit),survey_dates=['2025-03-16','2025-04-24'],sample_total=65,sample_valid=63,method='네이버폼·대면 인터뷰. 문항별 응답자52명, 복수응답. 시민 전체의 대표비율로 일반화하지 않음. 하천·정보는 원문 분류명.',source=str(R/'#경주시 원도심 미래구상 기획 연구 0804 최종본.pdf'),pages_print=[33,63,64,68]),cases=[dict(name='Delft',url='https://www.mecanoo.nl/Projects/project/52/Delft-Railway-Station-and-City-Hall?d=0&t=20',observed='철도 고가를 대체한 터널 위에 역·시청을 결합하고 역에서 시청 공공홀로 직접 연결',application='통합 청사와 시민 접근 동선의 결합'),dict(name='King’s Cross',url='https://www.kingscross.co.uk/about-the-development',observed='철도·산업부지 재생에 대학·주거·업무·상업과 가로·광장·공원을 함께 배치',application='일자리·주거·문화 기능을 공공공간으로 연결')])
assert data['citizen']['counts']==[26,24,24,8,6,5,2,1,1]
assert sum(data['tourist']['mode']['values'])==100
assert data['tourist']['stay']['day']==[83.1,44.7]
(B/'revision5_evidence.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'dow':data['tourist']['dow']['values'],'weekend_ratio':data['tourist']['dow']['weekend_ratio'],'citizen_counts':data['citizen']['counts'],'mentions':data['citizen']['total_mentions']},ensure_ascii=False))
