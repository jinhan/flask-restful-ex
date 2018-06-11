from orm import *
import datetime
from sqlalchemy.sql import func, and_
import pandas as pd
from templates import text_templates, background_variations
from queries import NoTextError, josaPick, regionPoll
from collections import Counter
from random import choice

with session_scope() as sess:
	t = '20180614050000'
	time = datetime.datetime.strptime(t, '%Y%m%d%H%M%S')
	# index = 0
	# regions = [1100]
	order = 0

	meta_cards = []
	subq_g = sess.query(func.max(OpenProgress4.serial).label('maxserial'), func.max(OpenProgress4.datatime).label('maxtime')).group_by(OpenProgress4.gusigun).filter(OpenProgress4.datatime<=time).subquery()

	sub_ranks_g = sess.query(OpenProgress4).join(subq_g, and_(OpenProgress4.serial==subq_g.c.maxserial, OpenProgress4.datatime==subq_g.c.maxtime))

	ranksDf_g = pd.read_sql(sub_ranks_g.statement, sub_ranks_g.session.bind)
	ranks_vote_g = ranksDf_g.filter(regex="n*_percent").dropna(axis=1)	
	ranks_ttl_g = [] # one line
	for i, ranks in ranks_vote_g.iterrows():
		ranks_ttl_g.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])
	
	for idx, ranks in enumerate(ranks_ttl_g): # 지역마다
		yet_cnt = ranksDf_g.loc[idx, 'tooTotal'] - ranksDf_g.loc[idx, 'n_total'] - ranksDf_g.loc[idx, 'invalid']
		rank1_cnt = ranksDf_g.loc[idx, ranks[0]+'_vote']
		rank2_cnt = ranksDf_g.loc[idx, ranks[1]+'_vote']
		confirm = True if (rank1_cnt-rank2_cnt) > yet_cnt else False

		open_finished = True if ranksDf_g.loc[idx,'openPercent'] == 100 else False
		ranking_g = []
		if confirm or open_finished:
			rank1_candidate_g = {
						'idx': idx,
						'rank': 0,
						'gusigun': ranksDf_g.loc[idx, 'gusigun'],
						'huboid': ranksDf_g.loc[idx, ranks[0]+'_huboid'],
						'name': ranksDf_g.loc[idx, ranks[0]+'_name'],
						'current': sess.query(CandidateInfo.current).filter(CandidateInfo.huboid==int(ranksDf_g.loc[idx, ranks[0]+'_huboid'])).scalar(),
						'percent': ranksDf_g.loc[idx, ranks[0]+'_percent'],
					}
			rank2_candidate_g = {
						'idx': idx,
						'rank': 1,
						'gusigun': ranksDf_g.loc[idx, 'gusigun'],
						'huboid': ranksDf_g.loc[idx, ranks[1]+'_huboid'],
						'name': ranksDf_g.loc[idx, ranks[1]+'_name'],
						'current': sess.query(CandidateInfo.current).filter(CandidateInfo.huboid==int(ranksDf_g.loc[idx, ranks[1]+'_huboid'])).scalar(),
						'percent': ranksDf_g.loc[idx, ranks[1]+'_percent'],
					}
			for i, r in enumerate(ranks): # 한 지역
				if sess.query(CandidateInfo.current).filter(CandidateInfo.huboid==int(ranksDf_g.loc[idx, r+'_huboid'])).scalar() == 1:
					current_candidate_g = {
						'idx': idx,
						'rank': i,
						'gusigun': ranksDf_g.loc[idx, 'gusigun'],
						'huboid': ranksDf_g.loc[idx, r+'_huboid'],
						'name': ranksDf_g.loc[idx, r+'_name'],
						'current': 1,
						'percent': ranksDf_g.loc[idx, r+'_percent'],
					}
				else:
					pass
		try:
			if rank1_candidate_g['huboid'] == current_candidate_g['huboid']:
				# current = rank1
				data = {
					'region': rank1_candidate_g['gusigun'],
					'poll': regionPoll(rank1_candidate_g['gusigun'], 4),
					'current_name': rank1_candidate_g['name'],
					'rank2_name': rank2_candidate_g['name'],
					'diff_percent': round(abs(rank1_candidate_g['percent']-rank2_candidate_g['percent']), 2),
				}
				card_num = '20-2'
				text = text_templates[card_num].format(**data)
				meta_card = {
					'debugging': '20_2',
					'type': 'difference',
					'order': order,
					'party': 'default',
					'data': {
						'difference_data': {
							'first': rank1_candidate_g['name'],
							'second': rank2_candidate_g['name'],
							'difference': round(abs(rank1_candidate_g['percent']-rank2_candidate_g['percent']), 2)
						},
						'text': text,
						'title': rank1_candidate_g['gusigun'] + ' 시군구청장 결과'
					}
				}
			else:
				data = {
					'region': rank1_candidate_g['gusigun'],
					'poll': regionPoll(rank1_candidate_g['gusigun'], 4),
					'current_name': current_candidate_g['name'],
					'rank1_name': rank1_candidate_g['name'],
					'diff_percent': round(abs(rank1_candidate_g['percent']-current_candidate_g['percent']), 2),
				}
				card_num = '20-1'
				text = text_templates[card_num].format(**data)
				meta_card = {
					'debugging': '20_1',
					'type': 'difference',
					'order': order,
					'party': 'default',
					'data': {
						'difference_data': {
							'first': rank1_candidate_g['name'],
							'second': rank2_candidate_g['name'],
							'difference': round(abs(rank1_candidate_g['percent']-rank2_candidate_g['percent']), 2)
						},
						'text': text,
						'title': rank1_candidate_g['gusigun'] + ' 시군구청장 결과'
					}
				}
		except TypeError:
			pass
		meta_cards.append(meta_card)
	meta_cards = list({v['data']['difference_data']['first']:v for v in meta_cards}.values())
	print(choice(meta_cards))