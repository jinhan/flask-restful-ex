from orm import *
import datetime
from sqlalchemy.sql import func, and_, label
import pandas as pd
from templates import text_templates, background_variations
from queries import NoTextError, josaPick, regionPoll, regionCodeCheck, query_card_data
from collections import Counter
from random import choice

with session_scope() as sess:
	t = '20180614100000'
	time = datetime.datetime.strptime(t, '%Y%m%d%H%M%S')
# 	# time = datetime.datetime.now()
	index = 2
	regions = [3101]
# 	order = 0
	# candidates = [100131357]
	polls = [3]
	parties = [1,2,3]

	party = sess.query(PartyCode.jdName).filter(PartyCode.pOrder==parties[index]).scalar()
		
	# 시도지사
	subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sido).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계').subquery()

	sub_ranks = sess.query(OpenProgress).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxtime))
	
	print(sub_ranks)
	if sub_ranks == None:
		raise NoTextError

	ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
	ranksDf = ranksDf.reset_index(drop=True)

	print(ranksDf)
	if len(ranksDf) == 0:
		raise NoTextError

	ranks_vote = ranksDf.filter(regex="n*_percent")
	ranks_ttl = []
	for i, ranks in ranks_vote.iterrows():
		ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])

	ranking = []
	for idx, ranks in enumerate(ranks_ttl):
		for i, r in enumerate(ranks):
			if ranksDf.loc[idx, r+'_jdName'] != None:
				ranking.append({
					'idx': idx,
					'rank': i,
					'jdName':ranksDf.loc[idx, r+'_jdName'],
					'name': ranksDf.loc[idx, r+'_name'],
					'percent': ranksDf.loc[idx, r+'_percent'],
					})
	rank1_count = Counter([r['jdName'] for r in ranking if r['rank']==0]).most_common()
	
	# 구시군청장
	subq_g = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sggCityCode).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==4, OpenProgress.sggCityCode!=None).subquery()


	sub_ranks_g = sess.query(OpenProgress).join(subq_g, and_(OpenProgress.serial==subq_g.c.maxserial, OpenProgress.datatime==subq_g.c.maxtime))

	ranksDf_g = pd.read_sql(sub_ranks_g.statement, sub_ranks_g.session.bind)
	ranks_vote_g = ranksDf_g.filter(regex="n*_percent")
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

	# 
	try:
		my_party_rank1_sido_num = [v for r, v in rank1_count if r == party][0]
	except IndexError:
		my_party_rank1_sido_num = 0

	try:
		my_party_rank1_gusigun_num = [v for r, v in rank1_count_g if r == party][0]
	except IndexError:
		my_party_rank1_gusigun_num = 0

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
	print(confirms_count)
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
	
	sido_total = sum([r[1] for r in rank1_count])
	try:
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
			data = {
				'party': party,
				'party_rank1_sido_num_confirm': confirms_count[0][1],
				'party_rank1_gusigun_num_confirm': [v for r, v in confirms_count_g if r == party][0],
			}
			card_num = '18-6'
			graph = False
			win_data = [{
				'name': '시도지사 선거',
				'value': confirms_count[0][1],
				'total': 17,
			},{
				'name': '시군구청장 선거',
				'value': [v for r, v in confirms_count_g if r == party][0],
				'total': 226,
			}]

		elif confirms_count[1][0] == party:
			data = {
				'party': party,
				'party_rank1_sido_num_confirm': confirms_count[1][1],
				'party_rank1_gusigun_num_confirm': [v for r, v in confirms_count_g if r == party][0],
			}
			card_num = '18-7'
			graph = False
			win_data = [{
				'name': '시도지사 선거',
				'value': confirms_count[1][1],
				'total': 17,
			},{
				'name': '시군구청장 선거',
				'value': [v for r, v in confirms_count_g if r == party][0],
				'total': 226,
			}]

		else:
			card_num = '18'
			graph = False
			win_data = [{
				'name': '시도지사 선거',
				'value': my_party_rank1_sido_num,
				'total': 17,
			},{
				'name': '시군구청장 선거',
				'value': my_party_rank1_gusigun_num,
				'total': 226,
			}]
	except IndexError:
		raise NoTextError
		
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
	print(meta_card)