# from string import Formatter
import datetime
from templates import text_templates, seq2type
from orm import *
from sqlalchemy.sql import func
from random import randint
from graph import generateMap, generateGraph
import tossi


def generateMeta(args):
	polls = args['type']
	regions = sess.query(District.sun_name1, District.sun_name2).filter(District.suncode.in_(args['region'])).all()
	parties = args['party']
	candidates = args['candidate']
	# time = datetime.datetime.now()
	time = datetime.datetime(2017, 5, 9, 23, 10, 56, 970686)

	card_seqs = getCardSeqs(polls, regions, parties, candidates, time)
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

	each_openrate = sess.query(func.max(OpenSido.openrate).label('max')).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name1)
	openrate = sess.query(func.avg(each_openrate.subquery().columns.max)).first()[0]
	# print(openrate)

	if time.hour < 19: # 투표중
		card_seqs.extend([1, 2, 3, 23]) # 6 특이사항
		card_seqs.extend([4] * len(regions))
		card_seqs.extend([5] * len(candidates))
		card_seqs.sort()

	elif time.hour > 19 and openrate < 10: # 투표마감이후
		card_seqs.extend([1, 2, 3, 22, 23]) # 6 특이사항
		card_seqs.extend([4] * len(regions))
		card_seqs.extend([5] * len(candidates))
		card_seqs.sort()
	
	elif time.hour > 19 and openrate >= 10 and openrate < 30: # 개표율 10% 이상
		card_seqs.extend([1, 2, 3, 7, 8, 9, 23]) # 6, 13, 20 특이사항
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
		card_seqs.extend([1, 2, 7, 8, 9, 14, 15, 16, 23]) # 13, 20 특이사항
		card_seqs.extend([10] * len(regions))
		card_seqs.extend([11] * len(polls))
		card_seqs.extend([12] * len(candidates))
		card_seqs.extend([17] * len(regions))
		card_seqs.extend([18] * len(candidates))
		card_seqs.extend([19] * len(parties))
		card_seqs.sort()

	# card_seqs = [1,2,3,4,5,6,7,8,9,10,11]
	# card_seqs = [3, 7]
	return card_seqs


# each by card
def generateTextsImgsViss(index, polls, regions, parties, candidates, time, card_seq):
	# db queries
	# print(card_seq)
	text, RANK1, title, rate, name, graph, map = query_card_data(index, polls, regions, parties, candidates, time, card_seq)

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
	return r

def idx2poll(idx):
	dic = {0: "시도지사", 1: "시군구청장"}
	return [dic[i] for i in idx]

def idx2party(idx):
	dic = {0:'더불어민주당', 1:'자유한국당', 2:'바른미래당', 3:'정의당', 99:'무소속'}
	return [dic[i] for i in idx]

def query_card_data(index, polls, regions, parties, candidates, time, card_seq):
	# 같은 card_seq에서 순서를 가져야, parameter랑 매치가 됨
	if card_seq is 1:
		# 관심 지역이 2개 이상일때 cover에 어떻게 표기?
		data = {
			'custom1': ', '.join([a + ' ' + b for a,b in regions]),
			'custom2': ', '.join(idx2party(parties)),
			'custom3': '시도지사',
		}
		text = text_templates[card_seq].format(**data)
		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		map = None

	elif card_seq is 2:
		each_toorate = sess.query(func.max(CurrentVote.toorate).label('max')).filter(CurrentVote.tootime<=time.hour).group_by(CurrentVote.sun_name1)
		toorate_avg_nat = sess.query(func.avg(each_toorate.subquery().columns.max)).first()

		if time.hour > 18:
			data = {
				'toorate_avg_nat': round(toorate_avg_nat[0], 2),
			}
			text = text_templates[card_seq].format(**data)
			title = '최종 투표율'
		else:
			data = {
				'hour': hourConverter(time.hour),
				'toorate_avg_nat': round(toorate_avg_nat[0], 2),
			}
			text = text_templates['2-1'].format(**data)
			title = hourConverter(time.hour) + ', 현재 투표율'

		RANK1 = 'default'
		# title = '최종 투표율'
		rate = round(toorate_avg_nat[0])
		name = None
		graph = None
		map = None

	elif card_seq is 3:
		past = sess.query(func.max(PastVote.toorate).label('max')).filter(PastVote.tootime <= time.hour).group_by(PastVote.sun_name1).subquery()
		past_toorate = sess.query(func.avg(past.c.max)).first()

		current = sess.query(func.max(CurrentVote.toorate).label('max')).filter(CurrentVote.tootime <= time.hour).group_by(CurrentVote.sun_name1).subquery()
		current_toorate = sess.query(func.avg(current.c.max)).first()
		current_toorate_past_toorate = current_toorate[0] - past_toorate[0]

		toorate_compare = '높은' if current_toorate_past_toorate > 0 else '낮은'

		ranks = sess.query(func.max(CurrentVote.toorate).label('max'), CurrentVote.sun_name1).filter(CurrentVote.tootime <= time.hour).group_by(CurrentVote.sun_name1).order_by(func.max(CurrentVote.toorate).desc()).all()
		toorate_rank1 = ranks[0][1]
		toorate_rank = ', '.join(rank[1] for rank in ranks[1:5])

		data = {
			'past_toorate': round(past_toorate[0], 2),
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

	elif card_seq is 4:
		region1 = regions[index][0]

		toorate_region1 = sess.query(func.max(CurrentVote.toorate)).filter(CurrentVote.tootime<=time.hour, CurrentVote.sun_name1==region1).first()

		each_toorate = sess.query(func.max(CurrentVote.toorate).label('max'), CurrentVote.sun_name1).filter(CurrentVote.tootime<=time.hour).group_by(CurrentVote.sun_name1)

		toorate_avg_nat = sess.query(func.avg(each_toorate.subquery().columns.max)).first()
		toorate_region1_toorate_avg_nat = toorate_region1[0] - toorate_avg_nat[0]

		toorate_compare1 = '높은' if toorate_region1_toorate_avg_nat > 0 else '낮은'

		region2 = regions[index][1]

		# TODO: _vote table에 sun_name2 없음
		# toorate_region2 = sess.query(func.max(CurrentVote.toorate)).filter(CurrentVote.tootime<=time.hour, CurrentVote.sun_name2==region2).first()
		toorate_region2 = sess.query(func.max(CurrentVote.toorate)).filter(CurrentVote.tootime<=time.hour, CurrentVote.sun_name1==region1).first()
		toorate_region2_toorate_avg_nat = toorate_region2[0] - toorate_avg_nat[0]

		toorate_compare2 = '높은' if (toorate_region2[0] - toorate_avg_nat[0]) > 0 else '낮은'

		data = {
			'region1': region1,
			'toorate_region1': round(toorate_region1[0], 2),
			'toorate_region1_toorate_avg_nat': round(abs(toorate_region1_toorate_avg_nat),2),
			'toorate_compare1': toorate_compare1,
			'region2': region2,
			'josa': josaPick(region2, '이'),
			'toorate_region2': round(toorate_region2[0],2),
			'toorate_region2_toorate_avg_nat': round(abs(toorate_region2_toorate_avg_nat),2),
			'toorate_compare2': toorate_compare2,
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
		map = generateMap(region2, each_toorate.all())

	elif card_seq is 5:
		candidate = candidates[index]

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
		pass

	elif card_seq is 7:
		each_openrate = sess.query(func.max(OpenSido.openrate).label('max')).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name1)
		openrate_avg_nat = sess.query(func.avg(each_openrate.subquery().columns.max)).first()

		past = sess.query(func.max(OpenViewSido.openrate).label('max')).group_by(OpenViewSido.sun_name1).subquery()
		past_openrate_avg_nat = sess.query(func.avg(past.c.max)).first()
		
		openrate_compare = '빠른' if (openrate_avg_nat[0] - past_openrate_avg_nat[0]) > 0 else '느린'
		openrate_compare_plus = '이른' if (openrate_avg_nat[0] - past_openrate_avg_nat[0]) > 0 else '늦은'

		data = {
			'hour': hourConverter(time.hour),
			'openrate_avg_nat': round(openrate_avg_nat[0], 2),
			'openrate_compare': openrate_compare,
			'openrate_compare_plus': openrate_compare_plus,
		}

		text = text_templates[card_seq].format(**data)
		RANK1 = 'default'
		title = hourConverter(time.hour) + ', 평균 개표율'
		rate = round(openrate_avg_nat[0])
		name = None
		graph = None
		map = None

	elif card_seq is 8:
		openrate_sunname1_ranks = sess.query(func.max(OpenSido.openrate).label('max'), OpenSido.sun_name1).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name1).order_by(func.max(OpenSido.openrate).desc()).all()

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
		# graph = generateGraph(openrate_sunname1_ranks)
		graph = None
		map = None

	elif card_seq is 9:
		openrate_sunname2_ranks = sess.query(func.max(OpenSido.openrate).label('max'), OpenSido.sun_name2, OpenSido.sun_name1).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name2).order_by(func.max(OpenSido.openrate).desc()).all()

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

		openrate_region1 = sess.query(func.max(OpenSido.openrate)).filter(OpenSido.sendtime<=time, OpenSido.sun_name1==region1).first()

		if openrate_region1[0] == 0:
			data = {
				'hour': hourConverter(time.hour),
				'region1': region1,
			}
			text = text_templates['10-1'].format(**data)
			map = None
		else:
			each_openrate = sess.query(func.max(OpenSido.openrate).label('max'), OpenSido.sun_name1.label('name')).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name1).subquery()
			openrate_avg_nat = sess.query(func.avg(each_openrate.c.max)).first()

			openrate_region1_openrate_avg_nat = openrate_region1[0] - openrate_avg_nat[0]
			compare_region1 = '높은' if openrate_region1_openrate_avg_nat > 0 else '낮은'

			# openrate_sido_rank1 = sess.query(each_openrate).order_by(each_openrate.c.max.desc()).first()
			openrate_region1_sub =  sess.query(func.max(OpenSido.openrate), OpenSido.sun_name2).filter(OpenSido.sendtime<=time, OpenSido.sun_name1==region1).group_by(OpenSido.sun_name2).order_by(func.max(OpenSido.openrate).desc()).all()

			region2 = regions[index][1]

			openrate_region2 = sess.query(func.max(OpenSido.openrate)).filter(OpenSido.sendtime<=time, OpenSido.sun_name2==region2).first()

			compare_region2 = '높은' if (openrate_region2[0] - openrate_avg_nat[0]) > 0 else '낮은'

			# each_openrate_region1 = sess.query(func.max(OpenSido.openrate).label('max'), OpenSido.sun_name2.label('name')).filter(OpenSido.sendtime<=time, OpenSido.sun_name1==region1).group_by(OpenSido.sun_name2).subquery()
			# openrate_region1_rank1 = sess.query(each_openrate_region1).order_by(each_openrate_region1.c.max.desc()).first()


			data = {
				'hour': hourConverter(time.hour),
				'region1': region1,
				'openrate_region1': round(openrate_region1[0], 2),
				'openrate_region1_openrate_avg_nat': round(abs(openrate_region1_openrate_avg_nat),2),
				'compare_region1': compare_region1,
				'region1': region1,
				'openrate_region1_region2_rank1': openrate_region1_sub[0][1],
				'josa1': josaPick(openrate_region1_sub[0][1], '로'),
				'openrate_region1_region2_rank1_rate': round(openrate_region1_sub[0][0], 2),
				'region2': region2,
				'josa2': josaPick(region2, '은'),
				'openrate_region2': round(openrate_region2[0], 2),
				'compare_region2': compare_region2,
			}
			text = text_templates[card_seq].format(**data)
			map = generateMap(region1, openrate_region1_sub)
	
		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		# map = generateMap(region1, openrate_region1_sub)

	elif card_seq is 11:
		# poll 종류
		poll = idx2poll(polls[index])
		poll_num_sunname = 100
		# poll 종류에 대해 달라져야함
		each_openrate = sess.query(func.max(OpenSido.openrate).label('max'), OpenSido.sun_name1).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name1).order_by(func.max(OpenSido.openrate).desc())
		poll_openrate_nat_avg = sess.query(func.avg(each_openrate.subquery().c.max)).first()

		poll_openrate_ranks = sess.query(each_openrate.subquery()).all()

		if poll_openrate_nat_avg[0] == 0:
			data = {
				'hour': hourConverter(time.hour),
				'poll': poll,
				'josa': josaPick(poll, '은'),
			}
			text = text_templates['11-1'].format(**data)
		else:
			data = {
				'poll_num_sunname': poll_num_sunname,
				'poll': poll,
				'poll_openrate_rank1': poll_openrate_ranks[0][1],
				'poll_openrate_rank1_rate': round(poll_openrate_ranks[0][0], 2),
				'poll_openrate_rank2': poll_openrate_ranks[1][1],
				'poll_openrate_rank2_rate': round(poll_openrate_ranks[1][0], 2),
				'poll': poll, 
				'poll_openrate_nat_avg': round(poll_openrate_nat_avg[0], 2),
			}
			text = text_templates[card_seq].format(**data)

		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		map = generateMap('전국', poll_openrate_ranks)

	elif card_seq is 12:
		candidate = candidates[index]
		
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
		pass

	elif card_seq is 14:
		sub_ranks = sess.query(OpenViewSido.rank01.label('rank01'), OpenViewSido.sun_name1).filter(OpenViewSido.sendtime<=time, OpenViewSido.rank01!=0).group_by(OpenViewSido.sun_name1).subquery()
		ranks = sess.query(func.count(sub_ranks.c.rank01), sub_ranks.c.rank01).group_by(sub_ranks.c.rank01).order_by(func.count(sub_ranks.c.rank01).desc()).all()
		rank1_party = sess.query(Candidate.affiliation).filter(Candidate.number==ranks[0][1]).first()[0]

		data = {
			'hour': hourConverter(time.hour),
			'rank1_party': rank1_party,
			'josa': josaPick(rank1_party, '이'),
		}
		text = text_templates[card_seq].format(**data)

		RANK1 = rank1_party
		title = rank1_party
		rate = None
		name = rank1_party
		graph = None
		map = None

	elif card_seq is 15:
		sub_ranks = sess.query(OpenViewSido.rank01.label('rank01'), OpenViewSido.sun_name1).filter(OpenViewSido.sendtime<=time, OpenViewSido.rank01!=0).group_by(OpenViewSido.sun_name1).subquery()
		ranks = sess.query(func.count(sub_ranks.c.rank01), sub_ranks.c.rank01).group_by(sub_ranks.c.rank01).order_by(func.count(sub_ranks.c.rank01).desc()).all()
		rank1_party = sess.query(Candidate.affiliation).filter(Candidate.number==ranks[0][1]).first()[0]

		data = {
			'hour': hourConverter(time.hour),
			'rank1_party': rank1_party,
			'josa1': josaPick(rank1_party, '이'),
			'rank1_party_num': rank1_party_num,
			'ranks_party': ranks_party,
			'josa2': josaPick(rank1_party[-1], '이')
		}
		text = text_templates[card_seq].format(**data)

		RANK1 = rank1_party
		title = hourConverter(time.hour) + ', ' + str(rank1_party_num) + '개 시도지사 선거구 1위'
		rate = None
		name = rank1_party
		graph = None
		map = None

	elif card_seq is 16:
		sub_ranks = sess.query(OpenViewGusigun.rank01.label('rank01'), OpenViewGusigun.sun_name2).filter(OpenViewGusigun.sendtime<=time, OpenViewGusigun.rank01!=0).group_by(OpenViewGusigun.sun_name2).subquery()
		ranks = sess.query(func.count(sub_ranks.c.rank01), sub_ranks.c.rank01).group_by(sub_ranks.c.rank01).order_by(func.count(sub_ranks.c.rank01).desc()).all()
		rank1_party = sess.query(Candidate.affiliation).filter(Candidate.number==ranks[0][1]).first()[0]

		data = {
			'hour': hourConverter(time.hour),
			'rank1_party': rank1_party,
			'josa1': josaPick(rank1_party, '이'),
			'rank1_party_num': rank1_party_num,
			'ranks_party': ranks_party, 
			'josa2': josaPick(ranks_party[-1], '이'),
		}
		text = text_templates[card_seq].format(**data)

		RANK1 = rank1_party
		title = hourConverter(time.hour) + ', ' + str(rank1_party_num) + '개 시군구청장 선거구 1위'
		rate = None
		name = rank1_party
		graph = None
		map = None

	elif card_seq is 17:
		region1 = regions[index][0]
		region1_poll = regionPoll(region1)

		region1_openrate = sess.query(func.max(OpenSido.openrate)).filter(OpenSido.sendtime<=time, OpenSido.sun_name1==region1).first()

		region1_ranks = sess.query(OpenViewSido.rank01.label('rank01'), OpenViewSido.rate01.label('rate01'), OpenViewSido.rank02.label('rank02'), OpenViewSido.rate02.label('rate02')).filter(OpenViewSido.sendtime<=time, OpenViewSido.sun_name1==region1).order_by(OpenViewSido.sendtime.desc()).first()

		region1_rank1 = sess.query(Candidate.affiliation, Candidate.name).filter(Candidate.number==region1_ranks.rank01).first()
		region1_rank1_party = region1_rank1[0]
		region1_rank1_name = region1_rank1[1]
		region1_rank1_rate = region1_ranks.rate01

		region1_rank2 = sess.query(Candidate.affiliation, Candidate.name).filter(Candidate.number==region1_ranks.rank02).first()
		region1_rank2_party = region1_rank2[0]
		region1_rank2_name = region1_rank2[1]
		region1_rank2_rate = region1_ranks.rate02

		# confirm = checkConfirm()
		confirm = False
		data = {
			'region1': region1,
			'region1_poll': region1_poll,
			'region1_rank1_party': region1_rank1_party,
			'region1_rank1_name': region1_rank1_name,
			'region1_rank1_rate': region1_rank1_rate,
			'region1_rank2_party': region1_rank2_party,
			'region1_rank2_name': region1_rank2_name,
			'region1_rank2_rate': region1_rank2_rate,
		}

		if confirm:
			text = text_templates['17-1'].format(**data)
		else:
			data['hour'] = hourConverter(time.hour)
			data['region1_openrate'] = round(region1_openrate[0], 2)
			text = text_templates[card_seq].format(**data)
		
		RANK1 = region1_rank1_party
		title = None
		rate = None
		name = None
		# graph = generateGraph(region1_ranks)
		graph = None
		map = None

	elif card_seq is 18:
		candidate = candidates[index]
		
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
