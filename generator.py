# from string import Formatter
import datetime
from templates import text_templates, seq2type
from orm import *
from sqlalchemy.sql import func
from random import randint
from graph import generateMap, generateGraph
import tossi
import pandas as pd
from timeit import default_timer as timer


def generateMeta(args):
	polls = args['type']
	regions = sess.query(District.sun_name1, District.sun_name2).filter(District.suncode.in_(args['region'])).all()
	# parties = args['party']
	parties = idx2party(args['party'])
	print(parties)
	candidates = args['candidate']
	# time = datetime.datetime.now()
	time = datetime.datetime(2017, 5, 9, 23, 10, 56, 970686)

	card_seqs = getCardSeqs(polls, regions, parties, candidates, time)
	# card_seqs = [2,3,4,6,7,8,9,10,11,12,13,14,16]
	# print(card_seqs)

	meta = {}
	meta['card_count'] = len(card_seqs)
	meta['design_variation'] = randint(0,3)
	meta_cards = []
	index = 0
	for i, card_seq in enumerate(card_seqs):
		if card_seqs[i-1] is card_seq:
			index += 1
		else:
			index = 0

		meta_card = {}
		meta_card['order'] = i+1

		img_type, img_party, data = generateTextsImgsViss(index, polls, regions, parties, candidates, time, card_seq)

		meta_card['type'] = img_type
		meta_card['party'] = img_party
		meta_card['data'] = data
		meta_card['debug'] = card_seq

		meta_cards.append(meta_card)
	meta['cards'] = meta_cards

	sess.close()
	return meta


def getCardSeqs(polls, regions, parties, candidates, time):
	card_seqs = []

	each_openrate = sess.query(func.max(OpenSido.openrate).label('max')).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name1).subquery()

	openrate = sess.query(func.avg(each_openrate.c.max)).scalar()
	# print(openrate)

	if time.hour < 19: # 투표중
		card_seqs.extend([1, 2, 3, 6, 23]) # 6 특이사항
		card_seqs.extend([4] * len(regions))
		card_seqs.extend([5] * len(candidates))
		card_seqs.sort()

	elif time.hour > 19 and openrate < 10: # 투표마감이후
		card_seqs.extend([1, 2, 3, 6, 22, 23]) # 6 특이사항
		card_seqs.extend([4] * len(regions))
		card_seqs.extend([5] * len(candidates))
		card_seqs.sort()
	
	elif time.hour > 19 and openrate >= 10 and openrate < 30: # 개표율 10% 이상
		card_seqs.extend([1, 2, 3, 6, 7, 8, 9, 13, 23]) # 6, 13, 20 특이사항
		card_seqs.extend([4] * len(regions))
		card_seqs.extend([5] * len(candidates))
		card_seqs.extend([10] * len(regions))
		card_seqs.extend([11] * len(polls))
		card_seqs.extend([12] * len(candidates))
		card_seqs.extend([17] * len(regions))
		card_seqs.extend([18] * len(candidates))
		card_seqs.extend([19] * len(parties))
		card_seqs.sort()

	elif time.hour > 19 and openrate >= 30: # 개표율 30% 이상
		card_seqs.extend([1, 2, 7, 8, 9, 13, 14, 16, 20, 23]) # 13, 20 특이사항
		card_seqs.extend([10] * len(regions))
		card_seqs.extend([11] * len(polls))
		card_seqs.extend([12] * len(candidates))
		# TODO: 15번 
		card_seqs.extend([16] * len(regions))
		card_seqs.extend([17] * len(candidates))
		card_seqs.extend([18] * len(parties))
		card_seqs.extend([19] * len(polls))
		card_seqs.sort()

	# card_seqs = [1,2,3,4,5,6,7,8,9,10,11]
	# card_seqs = [4]
	return card_seqs


# each by card
def generateTextsImgsViss(index, polls, regions, parties, candidates, time, card_seq):
	index = 0
	# db queries
	# print(card_seq)
	start = timer()
	text, RANK1, title, rate, name, graph, map = query_card_data(index, polls, regions, parties, candidates, time, card_seq)
	end = timer()
	print(card_seq, ":  ", end-start)
	# img template gen
	img_type = seq2type[card_seq]
	img_party = RANK1

	data = {'title': title, 'rate': rate, 'name': name, 'text': text, 'graph': graph, 'map': map} #'raw': raw_data
	return img_type, img_party, data


def hourConverter(h):
	if h < 12:
		return '오전 ' + str(h) + '시'
	elif h == 12:
		return '오후 ' + str(h) + '시'
	else:
		return '오후 ' + str(h - 12) + '시'

def josaPick(word, josa):
	return tossi.pick(word, josa)

def regionPoll(r):
	if r.endswith('시'):
		poll = '시장'
	elif r.endswith('도'):
		poll = '도지사'
	elif r.endswith('구'):
		poll = '구청장'
	elif r.endswith('군'):
		poll = '군수'
	else:
		poll = None
	return poll

def idx2poll(idx):
	# dic = {0: "시도지사", 1: "시군구청장", 2:"교육감", 3:"국회의원"}
	return [r for (r, ) in sess.query(SgCode.sgName).filter(SgCode.sgTypecode.in_(idx)).all()]

def idx2party(idx):
	# dic = {0:'더불어민주당', 1:'자유한국당', 2:'바른미래당', 3:'정의당', 99:'무소속'}
	return [r for (r, ) in sess.query(PartyCode.jdName).filter(PartyCode.pOrder.in_(idx)).all()]

def idx2candidate(idx):
	dic = {0:'박원순', 1:'배현진'}
	return [dic[i] for i in idx]


def query_card_data(index, polls, regions, parties, candidates, time, card_seq):
	if card_seq is 1:
		# TODO: 파라미터 선택하지 않았을 때
		customs = []
		customs.append(' #'.join([a + ' ' + b for a,b in regions]))
		# customs.append(' #'.join(idx2poll(polls)))
		customs.append(' #'.join(idx2party(parties)))
		customs.append(' #'.join(idx2candidate(candidates)))
		
		text = text_templates[card_seq].format('#' + ' #'.join(customs))
		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		map = None

	elif card_seq is 2:
		each_toorate = sess.query(func.max(CurrentVote.toorate).label('max')).filter(CurrentVote.tootime<=time.hour).group_by(CurrentVote.sun_name1).subquery()
		toorate_avg_nat = sess.query(func.avg(each_toorate.c.max)).scalar()

		data = {
			'toorate_avg_nat': round(toorate_avg_nat, 2),
		}
		if time.hour > 18:
			text = text_templates[card_seq].format(**data)
			title = '최종 투표율'
		else:
			data['hour'] = hourConverter(time.hour)
			text = text_templates['2-1'].format(**data)
			title = hourConverter(time.hour) + ', 현재 투표율'

		RANK1 = 'default'
		rate = round(toorate_avg_nat)
		name = None
		graph = None
		map = None

	elif card_seq is 3:
		past = sess.query(func.max(PastVote.toorate).label('max')).filter(PastVote.tootime <= time.hour).group_by(PastVote.sun_name1).subquery()
		past_toorate = sess.query(func.avg(past.c.max)).scalar()

		current = sess.query(func.max(CurrentVote.toorate).label('max')).filter(CurrentVote.tootime <= time.hour).group_by(CurrentVote.sun_name1).subquery()
		current_toorate = sess.query(func.avg(current.c.max)).scalar()
		current_toorate_past_toorate = current_toorate - past_toorate

		toorate_compare = '높은' if current_toorate_past_toorate > 0 else '낮은'

		ranks = sess.query(func.max(CurrentVote.toorate).label('max'), CurrentVote.sun_name1).filter(CurrentVote.tootime <= time.hour).group_by(CurrentVote.sun_name1).order_by(func.max(CurrentVote.toorate).desc()).all()

		toorate_rank1 = ranks[0][1]
		toorate_rank = ', '.join(rank[1] for rank in ranks[1:5])

		data = {
			'past_toorate': round(past_toorate, 2),
			'current_toorate_past_toorate': round(current_toorate_past_toorate, 2),
			'toorate_compare': toorate_compare,
			'toorate_rank1': toorate_rank1,
			'toorate_rank': toorate_rank,
			'josa': josaPick(toorate_rank[-1], '이')
		}

		if time.hour > 18:
			text = text_templates[card_seq].format(**data)
		else:
			text = text_templates['3-1'].format(**data)

		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		map = generateMap('전국', ranks)
		# map = None

	elif card_seq is 4:
		# print(index)
		# index = 0
		region1 = regions[index][0]
		# print(regions[index])

		# 서울, 서울
		toorate_region1 = sess.query(func.max(CurrentVote.toorate)).filter(CurrentVote.tootime<=time.hour, CurrentVote.sun_name1==region1).scalar()

		each_toorate = sess.query(func.max(CurrentVote.toorate).label('max'), CurrentVote.sun_name1).filter(CurrentVote.tootime<=time.hour).group_by(CurrentVote.sun_name1)

		toorate_avg_nat = sess.query(func.avg(each_toorate.subquery().c.max)).scalar()
		toorate_region1_toorate_avg_nat = toorate_region1 - toorate_avg_nat

		toorate_compare1 = '높은' if toorate_region1_toorate_avg_nat > 0 else '낮은'

		data = {
			'region1': region1,
			'toorate_region1': round(toorate_region1, 2),
			'toorate_region1_toorate_avg_nat': round(abs(toorate_region1_toorate_avg_nat),2),
			'toorate_compare1': toorate_compare1,
		}

		if time.hour > 18:
			text = text_templates[card_seq].format(**data)
		else:
			text = text_templates['4-1'].format(**data)

		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		# map = generateMap(region1, toorate_region1_sub)
		map = None

	elif card_seq is 5:
		# 5/25까지 후보자 등록기간
		# candidate = candidates[index]

		text = None
		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		map = None
		
		## candidate query
		# pass
		# if time.hour > 18:
		# 	data = {
		# 		'candidate': candidate,
		# 		'candidate_region': candidate_region,
		# 		'candidate_region_toorate': ,
		# 	}
		# 	text = text_templates[card_seq].format(**data)
		# else:
		# 	data = {
		# 		'candidate':,
		# 		'candidate_region':,
		# 		'hour': hourConverter(time.hour),
		# 		'candidate_region_toorate':,
		# 	}
		# 	text = text_templates['5-1'].format(**data)

		# RANK1 = 'default'
		# title = None
		# rate = None
		# name = None
		# graph = None
		# map = generateMap(region2, each_toorate.all())

	elif card_seq is 6:
		past = sess.query(func.max(PastVote.toorate).label('max')).filter(PastVote.tootime <= time.hour).group_by(PastVote.sun_name1).order_by(PastVote.sun_name1)
		past_toorate = sess.query(func.avg(past.subquery().c.max)).scalar()

		current = sess.query(func.max(CurrentVote.toorate).label('max')).filter(CurrentVote.tootime <= time.hour).group_by(CurrentVote.sun_name1).order_by(CurrentVote.sun_name1)
		current_toorate = sess.query(func.avg(current.subquery().c.max)).scalar()
		current_toorate_past_toorate = current_toorate - past_toorate

		if time.hour > 18:
			text = text_templates[card_seq] if current_toorate_past_toorate > 0 else text_templates['6-0']
		else:
			ratio = sum([1 for s in np.subtract(current.all(), past.all()) if s > 0]) / len(current.all())
			if current_toorate_past_toorate >= 5:
				text = text_templates['6-1']
			elif ratio >= 0.8:
				text = text_templates['6-2']
			else:
				text = None

		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		map = None

	elif card_seq is 7:
		each_openrate = sess.query(func.max(OpenSido.openrate).label('max')).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name1).subquery()
		openrate_avg_nat = sess.query(func.avg(each_openrate.c.max)).scalar()

		data = {
			'hour': hourConverter(time.hour),
			'openrate_avg_nat': round(openrate_avg_nat, 2),
		}

		text = text_templates[card_seq].format(**data)
		RANK1 = 'default'
		title = hourConverter(time.hour) + ', 평균 개표율'
		rate = round(openrate_avg_nat)
		name = None
		graph = None
		map = None

	elif card_seq is 8:
		openrate_sunname1_ranks = sess.query(func.max(OpenSido.openrate).label('max'), OpenSido.sun_name1).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name1).order_by(func.max(OpenSido.openrate).desc()).all()
		# TODO: find openrat == 100
		openDf = pd.DataFrame(openrate_sunname1_ranks)
		if len(openDf.loc[openDf['max']==100,'sun_name1']):
			open_finished = ', '.join(openDf.loc[openDf['max']==100,'sun_name1'])
			openrate_sunname1_rank1 = openDf.loc[openDf['max']!=100,].iloc[0]
			data = {
				'hour': hourConverter(time.hour),
				'open_finished': open_finished,
				'openrate_sunname1_rank1': openrate_sunname1_rank1['sun_name1'],
				'openrate_sunname1_rank1_rate': openrate_sunname1_rank1['max'],
			}
			text = text_templates['8-1'].format(**data)
		else:
			data = {
				'hour': hourConverter(time.hour),
				'openrate_sunname1_rank1': openrate_sunname1_ranks[0][1],
				'openrate_sunname1_rank1_rate': round(openrate_sunname1_ranks[0][0], 2),
				'openrate_sunname1_rank2': openrate_sunname1_ranks[1][1],
				'openrate_sunname1_rank2_rate': round(openrate_sunname1_ranks[1][0], 2),
			}
			text = text_templates[card_seq].format(**data)

		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		# map = None ## 
		map = generateMap('전국', openrate_sunname1_ranks)

	elif card_seq is 9:
		openrate_sunname2_ranks = sess.query(func.max(OpenSido.openrate).label('max'), OpenSido.sun_name2, OpenSido.sun_name1).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name2).order_by(func.max(OpenSido.openrate).desc()).all()

		openDf = pd.DataFrame(openrate_sunname2_ranks)
		if len(openDf.loc[openDf['max']==100,'sun_name2']):
			open_finished = ', '.join(openDf.loc[openDf['max']==100,'sun_name2'])
			openrate_sunname2_rank1 = openDf.loc[openDf['max']!=100,].iloc[0]
			data = {
				'hour': hourConverter(time.hour),
				'open_finished': open_finished,
				'openrate_sunname2_rank1': openrate_sunname2_rank1['sun_name2'],
				'openrate_sunname2_rank1_rate': openrate_sunname2_rank1['max'],
			}
			text = text_templates['9-1'].format(**data)
		else:
			data = {
				'hour': hourConverter(time.hour),
				'openrate_sunname2_rank1': openrate_sunname2_ranks[0][1],
				'openrate_sunname2_rank1_rate': round(openrate_sunname2_ranks[0][0], 2),
				'openrate_sunname2_rank2': openrate_sunname2_ranks[1][1],
				'openrate_sunname2_rank2_rate': round(openrate_sunname2_ranks[1][0], 2),
			}
			text = text_templates[card_seq].format(**data)

		RANK1 = 'default'
		title = None
		rate = None
		name = None
		# graph = generateGraph(openrate_sunname2_ranks)
		graph = None
		map = None

	elif card_seq is 10:
		region1 = regions[index][0]
		
		each_openrate = sess.query(func.max(OpenSido.openrate).label('max'), OpenSido.sun_name1.label('name')).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name1).subquery()
		openrate_region1 = sess.query(each_openrate.c.max).filter(each_openrate.c.name==region1).scalar()

		data = {
			'hour': hourConverter(time.hour),
			'region1': region1,
		}
		if openrate_region1 == 0:
			text = text_templates['10-1'].format(**data)
			map = None
		elif openrate_region1 == 100:
			text = text_templates['10-2'].format(**data)
			map = None
		else:
			openrate_avg_nat = sess.query(func.avg(each_openrate.c.max)).scalar()

			openrate_region1_openrate_avg_nat = openrate_region1 - openrate_avg_nat
			compare_region1 = '높은' if openrate_region1_openrate_avg_nat > 0 else '낮은'

			data['openrate_region1'] = round(openrate_region1, 2)
			data['openrate_region1_openrate_avg_nat'] = round(abs(openrate_region1_openrate_avg_nat), 2)
			data['compare_region1'] = compare_region1
			
			text = text_templates[card_seq].format(**data)

			openrate_region1_sub = sess.query(func.max(OpenSido.openrate), OpenSido.sun_name1).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name1).all()
			map = generateMap('전국', openrate_region1_sub)
			# map = None
	
		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None

	elif card_seq is 11:
		# poll 종류
		poll = polls[index]
		poll_num_sunname = 100
		# poll 종류에 대해 달라져야함
		each_openrate = sess.query(func.max(OpenSido.openrate).label('max'), OpenSido.sun_name1).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name1).order_by(func.max(OpenSido.openrate).desc()).subquery()
		poll_openrate_nat_avg = sess.query(func.avg(each_openrate.c.max)).scalar()
		poll_openrate_ranks = sess.query(each_openrate).all()

		if poll_openrate_nat_avg == 0:
			data = {
				'hour': hourConverter(time.hour),
				'poll': poll,
				'josa': josaPick(poll, '은'),
			}
			text = text_templates['11-1'].format(**data)
		elif poll_openrate_nat_avg == 100:
			data = {
				'hour': hourConverter(time.hour),
				'poll': poll,
			}
			text = text_templates['11-2'].format(**data)
		else:
			data = {
				'poll_num_sunname': poll_num_sunname,
				'poll': poll,
				'poll_openrate_rank1': poll_openrate_ranks[0][1],
				'poll_openrate_rank1_rate': round(poll_openrate_ranks[0][0], 2),
				'poll_openrate_rank2': poll_openrate_ranks[1][1],
				'poll_openrate_rank2_rate': round(poll_openrate_ranks[1][0], 2),
				'poll': poll, 
				'poll_openrate_nat_avg': round(poll_openrate_nat_avg, 2),
			}
			text = text_templates[card_seq].format(**data)

		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		map = generateMap('전국', poll_openrate_ranks)
		# map = None

	elif card_seq is 12:
		# candidate = candidates[index]
		
		text = None
		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		map = None
		# openrate_region1 = sess.query(func.max(OpenSido.openrate)).filter(OpenSido.sendtime<=time, OpenSido.sun_name1==region1).first()
		
		# data = {
		# 	'candidate': candidate,
		# 	'candidate_region': candidate_region,
		# 	'candidate_poll': candidate_poll,
		# }
		
		# if candidate_poll_openrate[0] == 0:
		# 	text = text_templates['12-1'].format(**data)
		# else:
		# 	data['candidate_poll_openrate'] = round(candidate_poll_openrate[0], 2)
		# 	text = text_templates[card_seq].format(**data)

		# RANK1 = 'default'
		# title = None
		# rate = None
		# name = None
		# graph = None
		# map = generateMap(region1, openrate_region1_sub)

	elif card_seq is 13:
		each_openrate = sess.query(func.max(OpenSido.openrate).label('max')).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name1).subquery()
		openrate_avg_nat = sess.query(func.avg(each_openrate.c.max)).scalar()

		if openrate_avg_nat < 100:
			openrate_sido = sess.query(OpenSido.sun_name1).filter(OpenSido.openrate==100).order_by(OpenSido.sendtime.asc()).all()
			if len(openrate_sido) > 0:
				data = {
					'hour': hourConverter(time.hour),
					'open_finished_sido': openrate_sido[0],
				}
				text = text_templates[card_seq].format(**data)
			else:
				text = ''

			openrate_gusigun = sess.query(OpenGusigun.sun_name2).filter(OpenGusigun.openrate==100).order_by(OpenGusigun.sendtime.asc()).all()
			if len(openrate_gusigun) > 0:
				data = {
					'hour': hourConverter(time.hour),
					'open_finished_gusigun': openrate_gusigun[0],
				}
				text += text_templates['13-1'].format(**data)
			else:
				text += ''
		else:
			text = text_templates['13-2'].format(hourConverter(time.hour))

		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		map = None

	elif card_seq is 14:
		sub_ranks = sess.query(OpenViewSido.rank01.label('rank01'), OpenViewSido.sun_name1).filter(OpenViewSido.sendtime<=time, OpenViewSido.rank01!=0).group_by(OpenViewSido.sun_name1).subquery()
		ranks = sess.query(func.count(sub_ranks.c.rank01), sub_ranks.c.rank01).group_by(sub_ranks.c.rank01).order_by(func.count(sub_ranks.c.rank01).desc()).all()
		rank1_party = sess.query(Candidate.affiliation).filter(Candidate.number==ranks[0][1]).scalar()
		rank1_party_num = ranks[0][0]

		data = {
			'hour': hourConverter(time.hour),
			'rank1_party': rank1_party,
			'josa1': josaPick(rank1_party, '이'),
			'josa2': josaPick(rank1_party, '은'),
			'rank1_party_num': rank1_party_num,
		}
		text = text_templates[card_seq].format(**data)

		RANK1 = rank1_party
		title = rank1_party
		rate = None
		name = rank1_party
		graph = None
		map = None

	elif card_seq is 15:
		# if len(regions) is 0:
		# TODO: implement customParams
		sgcode = customParams()
		if sgcode is 3: # 시도지사
			sub_ranks = sess.query(OpenViewSido.rank01.label('rank01'), OpenViewSido.sun_name1).filter(OpenViewSido.sendtime<=time, OpenViewSido.rank01!=0).group_by(OpenViewSido.sun_name1).subquery()
			ranks = sess.query(func.count(sub_ranks.c.rank01), sub_ranks.c.rank01).group_by(sub_ranks.c.rank01).order_by(func.count(sub_ranks.c.rank01).desc()).all()
			rank1_party = sess.query(Candidate.affiliation).filter(Candidate.number==ranks[0][1]).scalar()
			rank1_party_num = ranks[0][0]
			ranks_party = ', '.join(rank[1] for rank in ranks[1:5])
			data = {
				'hour': hourConverter(time.hour),
				'rank1_party': rank1_party, 
				'josa1': josaPick(rank1_party, '이'),
				'rank1_party_num': rank1_party_num,
				'ranks_party': ranks_party,
				'josa2': josaPick(ranks_party[-1], '이'),
			}
			text = text_templates[card_seq].format(**data)
		
		elif sgcode is 4: # 시군구청장
			sub_ranks = sess.query(OpenViewGusigun.rank01.label('rank01'), OpenViewGusigun.sun_name2).filter(OpenViewGusigun.sendtime<=time, OpenViewGusigun.rank01!=0).group_by(OpenViewGusigun.sun_name2).subquery()
			ranks = sess.query(func.count(sub_ranks.c.rank01), sub_ranks.c.rank01).group_by(sub_ranks.c.rank01).order_by(func.count(sub_ranks.c.rank01).desc()).all()
			rank1_party = sess.query(Candidate.affiliation).filter(Candidate.number==ranks[0][1]).scalar()
			rank1_party_num = ranks[0][0]
			ranks_party = ', '.join(rank[1] for rank in ranks[1:5])
			data = {
				'hour': hourConverter(time.hour),
				'rank1_party': rank1_party,
				'josa1': josaPick(rank1_party, '이'),
				'rank1_party_num': rank1_party_num,
				'ranks_party': ranks_party, 
				'josa2': josaPick(ranks_party[-1], '이'),
			}
			text = text_templates['15-1'].format(**data)

		elif sgcode is 2: # 국회의원
			data = {
				'hour': hourConverter(time.hour),
				'rank1_party': rank1_party, 
				'josa1': josaPick(rank1_party, '이'),
				'rank1_party_num': rank1_party_num,
				'ranks_party': ranks_party, 
				'josa2': josaPick(ranks_party[-1], '이'),
			}
			text = text_templates['15-2'].format(**data)

		elif sgcode is 11: # 교육감
			# TODO:
			text = text_templates['15-3'].format(**data)


		RANK1 = rank1_party
		title = hourConverter(time.hour) + ', ' + str(rank1_party_num) + '개 선거구 1위'
		rate = None
		name = rank1_party
		graph = None
		map = None

	elif card_seq is 16:
		region1 = regions[index][0]
		region1_poll = regionPoll(region1)

		region1_openrate = sess.query(func.max(OpenSido.openrate)).filter(OpenSido.sendtime<=time, OpenSido.sun_name1==region1, OpenSido.sun_name2==region1).scalar()

		region1_ranks = sess.query(OpenViewSido.rank01.label('rank01'), OpenViewSido.rate01.label('rate01'), OpenViewSido.rank02.label('rank02'), OpenViewSido.rate02.label('rate02'), OpenViewSido.toocnt, OpenViewSido.opencnt).filter(OpenViewSido.sendtime<=time, OpenViewSido.sun_name1==region1, OpenViewSido.sun_name2==region1).order_by(OpenViewSido.sendtime.desc()).first()

		region1_rank1 = sess.query(Candidate.affiliation, Candidate.name).filter(Candidate.number==region1_ranks.rank01).first()
		region1_rank1_party = region1_rank1[0]
		region1_rank1_name = region1_rank1[1]
		region1_rank1_rate = region1_ranks.rate01

		region1_rank2 = sess.query(Candidate.affiliation, Candidate.name).filter(Candidate.number==region1_ranks.rank02).first()
		region1_rank2_party = region1_rank2[0]
		region1_rank2_name = region1_rank2[1]
		region1_rank2_rate = region1_ranks.rate02

		data = {
			'hour': hourConverter(time.hour),
			'region1': region1,
			'region1_poll': region1_poll,
			'region1_openrate': region1_openrate,
			'region1_rank1_party': region1_rank1_party,
			'region1_rank1_name': region1_rank1_name,
			'region1_rank1_rate': region1_rank1_rate,
			'region1_rank2_party': region1_rank2_party,
			'region1_rank2_name': region1_rank2_name,
			'region1_rank2_rate': region1_rank2_rate,
		}

		rank1_cnt = region1_ranks.opencnt * region1_ranks.rank01 * 0.01
		rank2_cnt = region1_ranks.opencnt * region1_ranks.rank02 * 0.01
		yet_cnt = region1_ranks.toocnt - region1_ranks.opencnt
		confirm = True if (rank1_cnt-rank2_cnt) > yet_cnt else False

		if confirm:
			text = text_templates['16-3'].format(**data)
		else:
			if (region1_rank1_rate - region1_rank2_rate) >= 15:
				text = text_templates['16-2'].format(**data)
			elif (region1_rank1_rate - region1_rank2_rate) < 5:
				text = text_templates['16-1'].format(**data)
			else:
				text = text_templates[16].format(**data)
		
		RANK1 = region1_rank1_party
		title = None
		rate = None
		name = None
		graph_data = [(region1_rank1_rate, region1_rank1_party + ' ' + region1_rank1_name), (region1_rank2_rate, region1_rank2_party + ' ' + region1_rank2_name)]
		graph = generateGraph(graph_data)
		# graph = None
		map = None

	elif card_seq is 17:
		text = None
		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		map = None
		

	elif card_seq is 18:
		# candidate = candidates[index]
		
		text = None
		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		map = None

		
		# data = {
		# 	'hour': hourConverter(time.hour),
		# 	'candidate':
		# 	'candidate_region':
		# 	'candidate_poll':
		# 	'candidate_poll_rank1_candidate':
		# 	'candidate_poll_rank1_rate':
		# 	'candidate_poll_rank2_candidate':
		# 	'candidate_poll_rank2_rate':
		# }
		# if confirm:
		# 	text = text_templates['18-1'].format(**data)
		# else:
		# 	text = text_templates[card_seq].format(**data)
		
		# RANK1 = region2_rank1_party
		# title = None
		# rate = None
		# name = None
		# graph = generateGraph(region2_rank)
		# map = None

	elif card_seq is 19:
		# confirm = False
		# if confirm:
		# 	text = text_templates['19-1'].format(**data)
		# else:
		# 	text = text_templates[card_seq].format(**data)
		
		text = None
		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		map = None


	elif card_seq is 20:
		pass

	elif card_seq is 21:
		text = text_templates[card_seq].format(hourConverter(time.hour))
		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		map = None

	elif card_seq in [22, 23]:
		text = text_templates[card_seq]
		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		map = None

	return text, RANK1, title, rate, name, graph, map
