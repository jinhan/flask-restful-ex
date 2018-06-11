from orm import *
import datetime
from sqlalchemy.sql import func, and_
import pandas as pd
from templates import text_templates, background_variations
from queries import NoTextError, josaPick
from collections import Counter

with session_scope() as sess:
	t = '20180614040000'
	time = datetime.datetime.strptime(t, '%Y%m%d%H%M%S')
	index = 0
	regions = [1100]
	order = 0

	try:
		region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.townCode==regions[index]).first()
	except TypeError:
		raise NoTextError

	subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.townCode).filter(OpenProgress.datatime<=time, OpenProgress.gusigun!='합계', OpenProgress.electionCode==4, OpenProgress.sido==region1).subquery()

	sub_r = sess.query(OpenProgress.gusigun, OpenProgress.tooTotal, OpenProgress.n_total, OpenProgress.invalid).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxtime))
	map_data = []
	for r, tooTotal, n_total, invalid in sub_r.all():
		if invalid == None:
			invalid = 0
		v = (n_total + invalid) / tooTotal
		map_data.append({'name':r, 'value':v})
	map_data = list({v['name']:v for v in map_data}.values())
	# print(map_data)

	parties = [1]
	party = sess.query(PartyCode.jdName).filter(PartyCode.pOrder==parties[index]).scalar()
		
	# 시도지사
	subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.gusigun=='합계').subquery()

	sub_ranks = sess.query(OpenProgress3).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))

	ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
	if len(ranksDf) == 0:
		raise NoTextError
	ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)
	ranks_ttl = []
	for i, ranks in ranks_vote.iterrows():
		ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])

	ranking = []
	for idx, ranks in enumerate(ranks_ttl):
		for i, r in enumerate(ranks):
			ranking.append({
				'idx': idx,
				'rank': i,
				'jdName':ranksDf.loc[idx, r+'_jdName'],
				'name': ranksDf.loc[idx, r+'_name'],
				'percent': ranksDf.loc[idx, r+'_percent'],
				})
	rank1_count = Counter([r['jdName'] for r in ranking if r['rank']==0]).most_common()
	# print(rank1_count)

	subq_g = sess.query(func.max(OpenProgress4.serial).label('maxserial'), func.max(OpenProgress4.datatime).label('maxtime')).group_by(OpenProgress4.gusigun).filter(OpenProgress4.datatime<=time).subquery()

	sub_ranks_g = sess.query(OpenProgress4).join(subq_g, and_(OpenProgress4.serial==subq_g.c.maxserial, OpenProgress4.datatime==subq_g.c.maxtime))

	ranksDf_g = pd.read_sql(sub_ranks_g.statement, sub_ranks_g.session.bind)
	ranks_vote_g = ranksDf_g.filter(regex="n*_percent").dropna(axis=1)
	ranks_ttl_g = []
	for i, ranks in ranks_vote_g.iterrows():
		ranks_ttl_g.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])

	ranking_g = []
	for idx, ranks in enumerate(ranks_ttl_g):
		for i, r in enumerate(ranks):
			ranking_g.append({
				'idx': idx,
				'rank': i,
				'jdName':ranksDf_g.loc[idx, r+'_jdName'],
				'name': ranksDf_g.loc[idx, r+'_name'],
				'percent': ranksDf_g.loc[idx, r+'_percent'],
				})
	rank1_count_g = Counter([r['jdName'] for r in ranking_g if r['rank']==0]).most_common()

	my_party_rank1_sido_num = [v for r, v in rank1_count if r == party]
	my_party_rank1_gusigun_num = [v for r, v in rank1_count_g if r == party]
	party_rank1_sido_num = rank1_count[0][1]
	party_rank1_sido_name = rank1_count[0][0]
	party_rank2_sido_num = rank1_count[1][1]
	party_rank2_sido_name = rank1_count[1][0]
	try:
		party_rank3_sido_num = rank1_count[2][1]
		party_rank3_sido_name = rank1_count[2][0]
	except IndexError:
		raise NoTextError

	party_rank1_gusigun_num = rank1_count_g[0][1]
	party_rank123_gusigun_name = ', '.join([r[0] for r in rank1_count_g])

	confirms = []
	for idx, rank in enumerate(ranks_ttl):
		rank1_cnt = ranksDf.loc[idx, rank[0]+'_vote']
		rank2_cnt = ranksDf.loc[idx, rank[1]+'_vote']
		yet_cnt = ranksDf.loc[idx, 'tooTotal'] - ranksDf.loc[idx, 'n_total'] - ranksDf.loc[idx, 'invalid']
		confirm = 1 if (rank1_cnt-rank2_cnt) > yet_cnt else 0
		if confirm:
			confirms.append(ranksDf.loc[idx, rank[0]+'_jdName'])
	confirms_count = Counter(confirms).most_common()

	confirms_g = []
	for idx, rank in enumerate(ranks_ttl_g):
		rank1_cnt = ranksDf_g.loc[idx, rank[0]+'_vote']
		rank2_cnt = ranksDf_g.loc[idx, rank[1]+'_vote']
		yet_cnt = ranksDf_g.loc[idx, 'tooTotal'] - ranksDf_g.loc[idx, 'n_total'] - ranksDf_g.loc[idx, 'invalid']
		confirm = 1 if (rank1_cnt-rank2_cnt) > yet_cnt else 0
		if confirm:
			confirms_g.append(ranksDf_g.loc[idx, rank[0]+'_jdName'])
	confirms_count_g = Counter(confirms_g).most_common()
	
	data = {
		'party': party,
		'my_party_rank1_sido_num': my_party_rank1_sido_num,
		'my_party_rank1_gusigun_num': my_party_rank1_gusigun_num,
		'party_rank1_sido_num': party_rank1_sido_num,
		'party_rank1_sido_name': party_rank1_sido_name,
		'party_rank2_sido_num': party_rank2_sido_num,
		'party_rank2_sido_name': party_rank2_sido_name,
		'party_rank3_sido_name': party_rank3_sido_name,
		'josa': josaPick(party_rank3_sido_name, '이'),
		'party_rank3_sido_num': party_rank3_sido_num,
		'party_rank1_gusigun_num': party_rank1_gusigun_num,
		'party_rank123_gusigun_name': party_rank123_gusigun_name,
	}
			
	compare_data = []
	for r in rank1_count:
		compare_data.append({
			'party': r[0],
			'value': float(r[1] / len(ranking[0])),
			'unit': '개',
		})
	
	print(rank1_count)
	print(len(rank1_count))
	sido_total = sum([r[1] for r in rank1_count])
	# rank1_percent = 
	# rank2_percent
	# rank1_rank2_diff_ratio = 

	if abs(party_rank1_sido_num - party_rank2_sido_num) / sido_total < 0.05: # 1,2위 경합
		card_num = '18-1'
		graph = True

	elif abs(party_rank2_sido_num - party_rank3_sido_num) / sido_total < 0.05: # 2,3위 경합
		card_num = '18-2'
		graph = True
	
	elif (abs(party_rank1_sido_num - party_rank2_sido_num) / sido_total < 0.05) and (abs(party_rank2_sido_num - party_rank3_sido_num) / sido_total < 0.05): # 1,2,3위 경합
		card_num = '18-3'
		graph = True

	elif (party == party_rank1_sido_name) and (abs(party_rank1_sido_num - party_rank2_sido_num) / sido_total > 15): # 내가 선택한 정당이 1위일때, 1위와 2위의 격차가 15% 이상
		card_num = '18-4'
		graph = True
	
	elif (party == party_rank2_sido_name) and (abs(party_rank1_sido_num - party_rank2_sido_num) / sido_total > 15): # 내가 선택한 정당이 2위일때, 1위와 2위의 격차가 15% 이상
		card_num = '18-5'
		graph = True

	elif confirms_count[0][0] == party:
		data['party_rank1_sido_num_confirm'] = confirms_count[0][1],
		data['party_rank1_gusigun_num_confirm'] = [v for r, v in confirms_count_g if r == party][0],
		card_num = '18-6'
		graph = False
		win_data = [{
			'name': '시도지사 선거',
			'value': data['party_rank1_sido_num_confirm'],
			'total': 17,
		},{
			'name': '시군구청장 선거',
			'value': data['party_rank1_gusigun_num_confirm'],
			'total': 226,
		}]

	elif confirms_count[1][0] == party:
		data['party_rank1_sido_num_confirm'] = confirms_count[1][1],
		data['party_rank1_gusigun_num_confirm'] = [v for r, v in confirms_count_g if r == party][0],
		card_num = '18-7'
		graph = False
		win_data = [{
			'name': '시도지사 선거',
			'value': data['party_rank1_sido_num_confirm'],
			'total': 17,
		},{
			'name': '시군구청장 선거',
			'value': data['party_rank1_gusigun_num_confirm'],
			'total': 226,
		}]

	else:
		card_num = '18'
		graph = False
		
	text = text_templates[card_num].format(**data)
	if graph:
		meta_card = {
			'order': order,
			'type': 'compare',
			'party': party,
			'data': {
				'compare_data': {
					'type': 'party',
					'data': compare_data,
				},
				'text': text,
			},
			'debugging': card_num,
		}
	else:
		meta_card = {
			'order': order,
			'type': 'wins',
			'party': party,
			'data': {
				'win_data': win_data, 
				'text': text,
				'title': party + ' 득표율 1위 지역',
			},
			'debugging': card_num,
		}


	openrate_rank1_region = sess.query(OpenProgress11.sido).filter(OpenProgress11.datatime<=time, OpenProgress11.gusigun=='합계').order_by(func.max(OpenProgress11.openPercent).desc(), func.max(OpenProgress11.n_total).desc()).scalar()
			
	subq = sess.query(func.max(OpenProgress11.serial).label('maxserial'), func.max(OpenProgress11.datatime).label('maxtime')).group_by(OpenProgress11.sido).filter(OpenProgress11.datatime<=time, OpenProgress11.gusigun=='합계').subquery()

	sub_ranks = sess.query(OpenProgress11).join(subq, and_(OpenProgress11.serial==subq.c.maxserial, OpenProgress11.datatime==subq.c.maxtime))
			
	# print("ddd", openrate_rank1_region)
	if openrate_rank1_region == None:
		raise NoTextError

	ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
	ranksDf = ranksDf.sort_values(by=['openPercent', 'n_total'], ascending=False)
	print(ranksDf)
	# if polls[index] == 2: # 국회의원
	# 	poll, poll_num_sunname = sess.query(SgTypecode.sgName, func.count(PrecinctCode.sgg)).join(PrecinctCode, PrecinctCode.electionCode==SgTypecode.sgTypecode).filter(SgTypecode.sgTypecode==polls[index]).first()

	# 	subq = sess.query(func.max(OpenProgress2.serial).label('maxserial'), func.max(OpenProgress2.datatime).label('maxtime')).group_by(OpenProgress2.sgg).filter(OpenProgress2.datatime<=time).subquery()

	# 	sub = sess.query(OpenProgress2.sgg, OpenProgress2.tooTotal, OpenProgress2.n_total, OpenProgress2.invalid).join(subq, and_(OpenProgress2.serial==subq.c.maxserial, OpenProgress2.datatime==subq.c.maxtime))

	# 	tooTotal, n_total, invalid = sess.query(func.sum(OpenProgress2.tooTotal), func.sum(OpenProgress2.n_total), func.sum(OpenProgress2.invalid)).join(subq, and_(OpenProgress2.serial==subq.c.maxserial, OpenProgress2.datatime==subq.c.maxtime)).first()

	# elif polls[index] == 3:
	# 	poll, poll_num_sunname = sess.query(SgTypecode.sgName, func.count(PrecinctCode.cityCode)).join(PrecinctCode, PrecinctCode.electionCode==SgTypecode.sgTypecode).filter(SgTypecode.sgTypecode==polls[index]).first()

	# 	subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.gusigun=='합계').subquery()

	# 	sub = sess.query(OpenProgress3.sido, OpenProgress3.tooTotal, OpenProgress3.n_total, OpenProgress3.invalid).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))

	# 	tooTotal, n_total, invalid = sess.query(func.sum(OpenProgress3.tooTotal), func.sum(OpenProgress3.n_total), func.sum(OpenProgress3.invalid)).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime)).first()

	# elif polls[index] == 4:
	# 	poll, poll_num_sunname = sess.query(SgTypecode.sgName, func.count(PrecinctCode.gusigun)).join(PrecinctCode, PrecinctCode.electionCode==SgTypecode.sgTypecode).filter(SgTypecode.sgTypecode==polls[index]).first()

	# 	subq = sess.query(func.max(OpenProgress4.serial).label('maxserial'), func.max(OpenProgress4.datatime).label('maxtime')).group_by(OpenProgress4.townCode).filter(OpenProgress4.datatime<=time).subquery()

	# 	sub = sess.query(OpenProgress4.sido, OpenProgress4.tooTotal, OpenProgress4.n_total, OpenProgress4.invalid).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime))

	# 	tooTotal, n_total, invalid = sess.query(func.sum(OpenProgress4.tooTotal), func.sum(OpenProgress4.n_total), func.sum(OpenProgress4.invalid)).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime)).first()

	# elif polls[index] == 11:
	# 	poll, poll_num_sunname = sess.query(SgTypecode.sgName, func.count(PrecinctCode.cityCode)).join(PrecinctCode, PrecinctCode.electionCode==SgTypecode.sgTypecode).filter(SgTypecode.sgTypecode==polls[index]).first()

	# 	subq = sess.query(func.max(OpenProgress11.serial).label('maxserial'), func.max(OpenProgress11.datatime).label('maxtime')).group_by(OpenProgress11.sido).filter(OpenProgress11.datatime<=time, OpenProgress11.gusigun=='합계').subquery()

	# 	sub = sess.query(OpenProgress11.sido, OpenProgress11.tooTotal, OpenProgress11.n_total, OpenProgress11.invalid).join(subq, and_(OpenProgress11.serial==subq.c.maxserial, OpenProgress11.datatime==subq.c.maxtime))

	# 	tooTotal, n_total, invalid = sess.query(func.sum(OpenProgress11.tooTotal), func.sum(OpenProgress11.n_total), func.sum(OpenProgress11.invalid)).join(subq, and_(OpenProgress11.serial==subq.c.maxserial, OpenProgress11.datatime==subq.c.maxtime)).first()

	# else:
	# 	raise NoTextError

	# poll_openrate_ranks = []
	# if invalid == None:
	# 	invalid = 0

	# try:
	# 	poll_openrate_nat_avg = (n_total + invalid) / tooTotal * 100
		
	# 	for r, tooTotal, n_total, invalid in sub.all():
	# 		if invalid == None:
	# 			invalid = 0
	# 		v = (n_total + invalid) / tooTotal
	# 		poll_openrate_ranks.append({'name':r, 'value':v})
		
	# 	poll_openrate_ranks = sorted(poll_openrate_ranks, key=lambda x: x['value'], reverse=True)
	# 	# print(poll_openrate_ranks)
	# 	poll_openrate_ranks = list({v['name']:v for v in poll_openrate_ranks}.values())
	# 	print(poll_openrate_ranks)

	# 	if poll_openrate_nat_avg >= 100:
	# 		data = {
	# 			'hour': hourConverter(time.hour),
	# 			'poll': poll,
	# 		}
	# 		card_num = '11-2'
	# 		text = text_templates[card_num].format(**data)
	# 		meta_card = {
	# 			'order': order,
	# 			'type': 'rate',
	# 			'party': 'default',
	# 			'data': {
	# 				'title': poll + ', 개표 완료',
	# 				'rate': 100,
	# 				'text': text,
	# 			},
	# 			'debugging': card_num,
	# 		}
	# 	else:
	# 		data = {
	# 			'poll_num_sunname': poll_num_sunname,
	# 			'poll': poll,
	# 			'poll_openrate_rank1': poll_openrate_ranks[0]['name'],
	# 			'poll_openrate_rank1_rate': round(poll_openrate_ranks[0]['value'] * 100, 2),
	# 			'poll_openrate_rank2': poll_openrate_ranks[1]['name'],
	# 			'poll_openrate_rank2_rate': round(poll_openrate_ranks[1]['value'] * 100, 2),
	# 			'poll': poll, 
	# 			'poll_openrate_nat_avg': round(poll_openrate_nat_avg, 2),
	# 		}
	# 		card_num = '11'
	# 		text = text_templates[card_num].format(**data)
			
	# 		meta_card = {
	# 			'order': order,
	# 			'type': 'graph',
	# 			'party': 'default',
	# 			'data': {
	# 				'graph_data': {
	# 					'type': 'region',
	# 					'data': poll_openrate_ranks[:10],
	# 				},
	# 				'text': text,
	# 			}, 
	# 			'debugging': card_num,
	# 		}
	# except TypeError:
	# 	if tooTotal == None:
	# 		data = {
	# 			'hour': hourConverter(time.hour),
	# 			'poll': poll,
	# 			'josa': josaPick(poll, '은'),
	# 		}
	# 		card_num = '11-1'
	# 		text = text_templates[card_num].format(**data)
	# 		meta_card = {
	# 			'order': order,
	# 			'type': 'rate',
	# 			'party': 'default',
	# 			'data': {
	# 				'title': poll + ' 개표 준비중',
	# 				'rate': 0,
	# 				'text': text,
	# 			},
	# 			'debugging': card_num,
	# 		}
	# 	else:
	# 		raise NoTextError
	
	# # print(meta_card)