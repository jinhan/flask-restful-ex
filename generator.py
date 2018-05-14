# from string import Formatter
import datetime
from templates import text_templates, seq2type
from orm import *
from sqlalchemy.sql import func
from random import randint
from graph import generateMap, generateGraph

idx2poll = {1: "시도지사"}

def generateMeta(args):
	# poll = "시도지사"
	poll = args['type']
	region = sess.query(District.sun_name1, District.sun_name2).filter(District.suncode.in_(args['region'])).all()
	print(region)
	party = args['party']
	candidate = args['candidate']
	# time = datetime.datetime.now()
	time = datetime.datetime(2017, 5, 9, 23, 10, 56, 970686)

	card_seqs = getCardSeqs(poll, region, party, candidate, time)
	print(card_seqs)

	meta = {}
	meta['card_count'] = len(card_seqs)
	meta['design_variation'] = randint(0,3)
	meta_cards = []
	for i, card_seq in enumerate(card_seqs):
			meta_card = {}
			meta_card['order'] = i+1

			img_type, img_party, data = generateTextsImgsViss(poll, region, party, candidate, time, card_seq)

			meta_card['type'] = img_type
			meta_card['party'] = img_party
			meta_card['data'] = data

			meta_cards.append(meta_card)
	meta['cards'] = meta_cards

	sess.close()
	return meta


def getCardSeqs(poll, region, party, candidate, time):
	card_seqs = []

	each_openrate = sess.query(func.max(OpenSido.openrate).label('max')).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name1)
	openrate = sess.query(func.avg(each_openrate.subquery().columns.max)).first()[0]
	print(openrate)
	if time.hour < 19: # 투표중
		card_seqs.extend([1, 2, 3, 23]) # 6 특이사항
		card_seqs.extend([4] * len(region))
		card_seqs.extend([5] * len(candidate))
		card_seqs.sort()

	elif time.hour > 19 and openrate < 10: # 투표마감이후
		card_seqs.extend([1, 2, 3, 22, 23]) # 6 특이사항
		card_seqs.extend([4] * len(region))
		card_seqs.extend([5] * len(candidate))
		card_seqs.sort()
	
	elif time.hour > 19 and openrate >= 10 and openrate < 30: # 개표율 10% 이상
		card_seqs.extend([1, 2, 3, 7, 8, 9, 23]) # 6, 13, 20 특이사항
		card_seqs.extend([4] * len(region))
		card_seqs.extend([5] * len(candidate))
		card_seqs.extend([10] * len(region))
		card_seqs.extend([11] * len(poll))
		card_seqs.extend([12] * len(candidate))
		card_seqs.extend([17] * len(region))
		card_seqs.extend([18] * len(candidate))
		card_seqs.extend([19] * len(party))
		card_seqs.sort()

	elif time.hour > 19 and openrate >= 30: # 개표율 30% 이상
		card_seqs.extend([1, 2, 7, 8, 9, 14, 15, 16, 23]) # 13, 20 특이사항
		card_seqs.extend([10] * len(region))
		card_seqs.extend([11] * len(poll))
		card_seqs.extend([12] * len(candidate))
		card_seqs.extend([17] * len(region))
		card_seqs.extend([18] * len(candidate))
		card_seqs.extend([19] * len(party))
		card_seqs.sort()

	# card_seqs = [1,2,3,4,5,6,7,8,9,10,11]
	# card_seqs = [3, 7]
	return card_seqs


# each by card
def generateTextsImgsViss(poll, region, party, candidate, time, card_seq):
	# db queries
	text, RANK1, title, rate, name, graph, map = query_card_data(poll, region, party, candidate, time, card_seq)
	# text = text_templates[card_seq].format(**text_data)

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


def query_card_data(poll, region, party, candidate, time, card_seq):
	# 같은 card_seq에서 순서를 가져야, parameter랑 매치가 됨
	if card_seq is 1:
		# 관심 지역이 2개 이상일때 cover에 어떻게 표기?
		data = {
			'custom1': region[0],
			'custom2': region[1],
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
				'hour': hourConverter(time.hour)
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

		current = sess.query(func.max(CurrentVote.toorate).filter(CurrentVote.tootime <= time.hour).label('max')).group_by(CurrentVote.sun_name1).subquery()
		current_toorate = sess.query(func.avg(current.c.max)).first()
		current_toorate_past_toorate = current_toorate[0] - past_toorate[0]

		toorate_compare = '높은' if current_toorate_past_toorate > 0 else '낮은'

		ranks = sess.query(func.max(CurrentVote.toorate).label('max'), CurrentVote.sun_name1).filter(CurrentVote.tootime <= time.hour).group_by(CurrentVote.sun_name1).order_by(func.max(CurrentVote.toorate).desc()).all()
		toorate_rank1 = ranks[0][1]
		toorate_rank = ', '.join(rank[1] for rank in ranks[1:5])
		josa = '이'

		data = {
			'past_toorate': round(past_toorate[0], 2),
			'current_toorate_past_toorate': round(current_toorate_past_toorate, 2),
			'toorate_compare': toorate_compare,
			'toorate_rank1': toorate_rank1,
			'toorate_rank': toorate_rank,
			'josa': josa
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
		region1 = region[0]

		toorate_region1 = sess.query(func.max(CurrentVote.toorate)).filter(CurrentVote.tootime<=time.hour, CurrentVote.sun_name1==region1).first()

		each_toorate = sess.query(func.max(CurrentVote.toorate).label('max'), CurrentVote.sun_name1).filter(CurrentVote.tootime<=time.hour).group_by(CurrentVote.sun_name1)

		toorate_avg_nat = sess.query(func.avg(each_toorate.subquery().columns.max)).first()
		toorate_region1_toorate_avg_nat = toorate_region1[0] - toorate_avg_nat[0]

		toorate_compare1 = '높은' if toorate_region1_toorate_avg_nat > 0 else '낮은'

		region2 = region[1]

		# TODO: _vote table에 sun_name2 없음
		# toorate_region2 = sess.query(func.max(CurrentVote.toorate)).filter(CurrentVote.tootime<=time.hour, CurrentVote.sun_name2==region2).first()
		toorate_region2 = sess.query(func.max(CurrentVote.toorate)).filter(CurrentVote.tootime<=time.hour, CurrentVote.sun_name1==region1).first()

		toorate_compare2 = '높은' if (toorate_region2[0] - toorate_avg_nat[0]) > 0 else '낮은'

		data = {
			'region1': region1,
			'toorate_region1': round(toorate_region1[0], 2),
			'toorate_region1_toorate_avg_nat': round(abs(toorate_region1_toorate_avg_nat),2),
			'toorate_compare1': toorate_compare1,
			'region2': region2,
			'josa': '이',
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

		if time.hour > 18:
			data = {
				'candidate1':,
				'candidate1_region':,
				'candidate1_region_toorate':,
			}
			text = text_templates[card_seq].format(**data)
		else:
			data = {
				'candidate1':,
				'candidate1_region':,
				'hour': hourConverter(time.hour),
				'candidate1_region_toorate':,
			}
			text = text_templates['5-1'].format(**data)

		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		map = generateMap(region2, each_toorate.all())

	elif card_seq is 6:
		pass

	elif card_seq is 7:
		each_openrate = sess.query(func.max(OpenSido.openrate).label('max')).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name1)
		openrate_avg_nat = sess.query(func.avg(each_openrate.subquery().columns.max)).first()

		compare_openrate = '빠른' if (openrate_avg_nat[0] - past_openrate_avg_nat[0]) > 0 else '느린'
		compare_openrate_plus = '이른' if (openrate_avg_nat[0] - past_openrate_avg_nat[0]) > 0 else '늦은'

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
		openrate_sunname1_rank1 = sess.query(func.max(OpenSido.openrate).label('max'), OpenSido.sun_name1).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name1).order_by(func.max(OpenSido.openrate).desc()).first()

		data = {
			'hour': hourConverter(time.hour),
			'openrate_sunname1_rank1': openrate_sunname1_rank1[1],
			'openrate_sunname1_rank1_rate': round(openrate_sunname1_rank1[0], 2)
			'openrate_sunname1_rank2': openrate_sunname1_rank2[1],
			'openrate_sunname1_rank2_rate': round(openrate_sunname1_rank2[0], 2),
		}

		text = text_templates[card_seq].format(**data)
		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = generateGraph(openrate_sunname1_rank1)
		map = None

	elif card_seq is 9:
		openrate_sunname2_rank1 = sess.query(func.max(OpenSido.openrate).label('max'), OpenSido.sun_name2, OpenSido.sun_name1).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name2).order_by(func.max(OpenSido.openrate).desc()).first()

		data = {
			'hour': hourConverter(time.hour),
			'openrate_sunname2_rank1': openrate_sunname2_rank1[1],
			'openrate_sunname2_rank1_rate': round(openrate_sunname2_rank1[0], 2)
			'openrate_sunname2_rank2': openrate_sunname2_rank2[1],
			'openrate_sunname2_rank2_rate': round(openrate_sunname2_rank2[0], 2),
		}

		text = text_templates[card_seq].format(**data)
		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = generateGraph(openrate_sunname2_rank1)
		map = None

	elif card_seq is 10:
		region1 = region[0]

		openrate_region1 = sess.query(func.max(OpenSido.openrate)).filter(OpenSido.sendtime<=time, OpenSido.sun_name1==region1).first()

		if openrate_region1[0] == 0:
			data = {
				'hour': hourConverter(time.hour),
				'region1': region1,
			}
			text = text_templates['10-1'].format(**data)
		else:
			each_openrate = sess.query(func.max(OpenSido.openrate).label('max'), OpenSido.sun_name1.label('name')).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name1).subquery()
			openrate_avg_nat = sess.query(func.avg(each_openrate.c.max)).first()

			openrate_region1_openrate_avg_nat = openrate_region1[0] - openrate_avg_nat[0]
			compare_region1 = '높은' if openrate_region1_openrate_avg_nat > 0 else '낮은'

			kwargs = {
				'openrate_region1_openrate_avg_nat': round(abs(openrate_region1_openrate_avg_nat),2),
				'compare_region1': compare_region1,
			}
			region1_exception = text_templates['7-1'].format(**kwargs)

			region2 = region[1]

			openrate_region2 = sess.query(func.max(OpenSido.openrate)).filter(OpenSido.sendtime<=time, OpenSido.sun_name2==region2).first()

			if openrate_region2[0] == 0:
				region2_exception = text_templates['7-0']
			else:
				compare_region2 = '높은' if (openrate_region2[0] - openrate_avg_nat[0]) > 0 else '낮은'

				kwargs = {
					'compare_region2': compare_region2,
				}
				region1_exception = text_templates['7-2'].format(**kwargs)

			openrate_sido_rank1 = sess.query(each_openrate).order_by(each_openrate.c.max.desc()).first()

			each_openrate_region1 = sess.query(func.max(OpenSido.openrate).label('max'), OpenSido.sun_name2.label('name')).filter(OpenSido.sendtime<=time, OpenSido.sun_name1==region1).group_by(OpenSido.sun_name2).subquery()
			openrate_region1_rank1 = sess.query(each_openrate_region1).order_by(each_openrate_region1.c.max.desc()).first()


			openrate_region1_sub =  sess.query(func.max(OpenSido.openrate), OpenSido.sun_name2).filter(OpenSido.sendtime<=time, OpenSido.sun_name1==region1).group_by(OpenSido.sun_name2).all()

			data = {
				'hour': hourConverter(time.hour),
				'region1': region1,
				'openrate_region1': round(openrate_region1[0], 2),
				'openrate_region1_openrate_avg_nat':,
				'compare_region1':
				'region1':
				'openrate_regio1_region2_rank1':
				'openrate_regio1_region2_rank1_rate':
				'region2': region2,
				'openrate_region2': round(openrate_region2[0], 2),
				'compare_region2': compare_region2,
			}


	
		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		map = generateMap(region1, openrate_region1_sub)

	elif card_seq is 8:
		sub_ranks = sess.query(OpenViewSido.rank01.label('rank01'), OpenViewSido.sun_name2).filter(OpenViewSido.sendtime<=time, OpenViewSido.rank01!=0).group_by(OpenViewSido.sun_name2).subquery()
		ranks = sess.query(func.count(sub_ranks.c.rank01), sub_ranks.c.rank01).group_by(sub_ranks.c.rank01).order_by(func.count(sub_ranks.c.rank01).desc()).all()

		rank1_party = sess.query(Candidate.affiliation).filter(Candidate.number==ranks[0][1]).first()[0]
		rank1_party_num = ranks[0][0]

		rank2_party = sess.query(Candidate.affiliation).filter(Candidate.number==ranks[1][1]).first()[0]
		rank2_party_num = ranks[1][0]

		rank3_party = sess.query(Candidate.affiliation).filter(Candidate.number==ranks[2][1]).first()[0]
		rank3_party_num = ranks[2][0]

		josa = '이'

		data = {
			'hour': hourConverter(time.hour),
			'num': 100,
			'rank1_party': rank1_party,
			'rank1_party_num': rank1_party_num,
			'rank2_party': rank2_party,
			'rank2_party_num': rank2_party_num,
			'rank2_party_num': rank2_party_num,
			'rank3_party': rank3_party,
			'rank3_party_num': rank3_party_num,
			'josa': josa,
		}
		RANK1 = rank1_party
		title = hourConverter(time.hour) + ', ' + str(rank1_party_num) + '개 1위'
		rate = None
		name = rank1_party
		graph = None
		map = None

	elif card_seq is 9:
		# TODO: TypeError exception
		sub_ranks = sess.query(OpenViewSido.rank01.label('rank01'), OpenViewSido.sun_name1).filter(OpenViewSido.sendtime<=time, OpenViewSido.rank01!=0).group_by(OpenViewSido.sun_name1).subquery()
		ranks = sess.query(func.count(sub_ranks.c.rank01), sub_ranks.c.rank01).group_by(sub_ranks.c.rank01).order_by(func.count(sub_ranks.c.rank01).desc()).all()

		rank1_party = sess.query(Candidate.affiliation).filter(Candidate.number==ranks[0][1]).first()[0]
		rank1_party_num = ranks[0][0]

		rank2_party = sess.query(Candidate.affiliation).filter(Candidate.number==ranks[1][1]).first()[0]
		rank2_party_num = ranks[1][0]

		# rank3_party = sess.query(Candidate.affiliation).filter(Candidate.number==ranks[2][1]).first()[0]
		# rank3_party_num = ranks[2][0]
		rank3_party = '3위없음'
		rank3_party_num = '3위없음'

		josa = '이'

		data = {
			'hour': hourConverter(time.hour),
			'num': 100,
			'rank1_party': rank1_party,
			'rank1_party_num': rank1_party_num,
			'rank2_party': rank2_party,
			'rank2_party_num': rank2_party_num,
			'rank2_party_num': rank2_party_num,
			'rank3_party': rank3_party,
			'rank3_party_num': rank3_party_num,
			'josa': josa,
		}
		RANK1 = rank1_party
		title = None
		rate = None
		name = None
		graph = generateGraph(sub_ranks)
		map = None

	elif card_seq is 10:
		region1 = region[0]

		sido_type = '시장'

		openrate_region1 = sess.query(func.max(OpenSido.openrate)).filter(OpenSido.sendtime<=time, OpenSido.sun_name1==region1).first()

		region1_rank = sess.query(OpenViewSido.rank01.label('rank01'), OpenViewSido.rate01.label('rate01'), OpenViewSido.rank02.label('rank02'), OpenViewSido.rate02.label('rate02')).filter(OpenViewSido.sendtime<=time, OpenViewSido.sun_name1==region1).order_by(OpenViewSido.sendtime.desc()).first()

		region1_rank1 = sess.query(Candidate.affiliation, Candidate.name).filter(Candidate.number==region1_rank.rank01).first()
		region1_rank1_party = region1_rank1[0]
		region1_rank1_candidate = region1_rank1[1]
		region1_rank1_pollrate = region1_rank.rate01

		region1_rank2 = sess.query(Candidate.affiliation, Candidate.name).filter(Candidate.number==region1_rank.rank02).first()
		region1_rank2_party = region1_rank2[0]
		region1_rank2_candidate = region1_rank2[1]
		region1_rank2_pollrate = region1_rank.rate02

		data = {
			'hour': hourConverter(time.hour),
			'region1': region1,
			'sido_type': sido_type,
			'openrate_region1': round(openrate_region1[0], 2),
			'region1_rank1_party': region1_rank1_party,
			'region1_rank1_candidate': region1_rank1_candidate,
			'region1_rank1_pollrate': region1_rank1_pollrate,
			'region1_rank2_party': region1_rank2_party,
			'region1_rank2_candidate': region1_rank2_candidate,
			'region1_rank2_pollrate': region1_rank2_pollrate,
		}
		RANK1 = region1_rank1_party
		title = None
		rate = None
		name = None
		graph = generateGraph(region1_rank)
		map = None

	elif card_seq is 11:
		# TODO: TypeError exception 0인 경우
		region2 = region[1]
		region2 = '서귀포'
		sido_type = "구청장"

		openrate_region2 = sess.query(func.max(OpenSido.openrate)).filter(OpenSido.sendtime<=time, OpenSido.sun_name2==region2).first()

		region2_rank = sess.query(OpenViewSido.rank01.label('rank01'), OpenViewSido.rate01.label('rate01'), OpenViewSido.rank02.label('rank02'), OpenViewSido.rate02.label('rate02')).filter(OpenViewSido.sendtime<=time, OpenViewSido.sun_name2==region2).order_by(OpenViewSido.sendtime.desc()).first()

		region2_rank1 = sess.query(Candidate.affiliation, Candidate.name).filter(Candidate.number==region2_rank.rank01).first()
		# print(region2_rank1)
		region2_rank1_party = region2_rank1[0]
		region2_rank1_candidate = region2_rank1[1]
		region2_rank1_pollrate = region2_rank.rate01

		region2_rank2 = sess.query(Candidate.affiliation, Candidate.name).filter(Candidate.number==region2_rank.rank02).first()
		region2_rank2_party = region2_rank2[0]
		region2_rank2_candidate = region2_rank2[1]
		region2_rank2_pollrate = region2_rank.rate02

		data = {
			'hour': hourConverter(time.hour),
			'region2': region2,
			'sido_type': sido_type,
			'openrate_region2': round(openrate_region2[0], 2),
			'region2_rank1_party': region2_rank1_party,
			'region2_rank1_candidate': region2_rank1_candidate,
			'region2_rank1_pollrate': region2_rank1_pollrate,
			'region2_rank2_party': region2_rank2_party,
			'region2_rank2_candidate': region2_rank2_candidate,
			'region2_rank2_pollrate': region2_rank2_pollrate,
		}
		RANK1 = region2_rank1_party
		title = None
		rate = None
		name = None
		graph = generateGraph(region2_rank)
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
