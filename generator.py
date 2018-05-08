# from string import Formatter
import datetime
from templates import text_templates, seq2type
from orm import *
from sqlalchemy.sql import func
from random import randint
from graph import generateMap, generateGraph


def generateMeta(args):
	type = "시도지사"
	region = sess.query(District.sun_name1, District.sun_name2).filter(District.suncode==args['region']).first()
	party = args['party']
	candidate = args['candidate']
	time = datetime.datetime.now()

	card_seqs = getCardSeqs(type, region, party, candidate, time)

	meta = {}
	meta['card_count'] = len(card_seqs)
	meta['design_variation'] = randint(0,3)
	meta_cards = []
	for i, card_seq in enumerate(card_seqs):
			meta_card = {}
			meta_card['order'] = i+1

			img_type, img_party, data = generateTextsImgsViss(type, region, party, candidate, time, card_seq)

			meta_card['type'] = img_type
			meta_card['party'] = img_party
			meta_card['data'] = data

			meta_cards.append(meta_card)
	meta['cards'] = meta_cards

	sess.close()
	return meta


def getCardSeqs(type, region, party, candidate, time):

	# card_seqs = [1,2,3,4,5,6,7,8,9,10,11]
	card_seqs = [3, 7]
	return card_seqs


# each by card
def generateTextsImgsViss(type, region, party, candidate, time, card_seq):
	# db queries
	text_data, RANK1, title, rate, name, graph, map = query_card_data(type, region, party, candidate, time, card_seq)
	text = text_templates[card_seq].format(**text_data)

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


# def generateMap(r, q):
#
# 	return "https://s3.amazonaws.com/"
#
#
# def generateGraph(q):
# 	return "https://s3.amazonaws.com/"


def query_card_data(type, region, party, candidate, time, card_seq):
	time = datetime.datetime(2017, 5, 9, 23, 10, 56, 970686)

	# keys = [kw for _, kw, _, _ in Formatter().parse(text_templates[card_seq]) if kw]
	# vals = []
	# data = {}
	if card_seq is 1:
		data = {
			'custom1': region[0],
			'custom2': region[1],
			'custom3': '시도지사',
		}
		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		map = None

	elif card_seq is 2:
		each_toorate = sess.query(func.max(CurrentVote.toorate).label('max')).filter(CurrentVote.tootime<=time.hour).group_by(CurrentVote.sun_name1)
		toorate_avg_nat = sess.query(func.avg(each_toorate.subquery().columns.max)).first()

		data = {
			'toorate_avg_nat': round(toorate_avg_nat[0], 2),
		}
		RANK1 = 'default'
		title = '최종 투표율'
		rate = round(toorate_avg_nat[0])
		name = None
		graph = None
		map = None

	elif card_seq is 3:
		past = sess.query(func.max(PastVote.toorate).label('max')).group_by(PastVote.sun_name1).subquery()
		past_toorate = sess.query(func.avg(past.c.max)).first()

		current = sess.query(func.max(CurrentVote.toorate).label('max')).group_by(CurrentVote.sun_name1).subquery()
		current_toorate = sess.query(func.avg(current.c.max)).first()
		current_toorate_past_toorate = current_toorate[0] - past_toorate[0]
		# print(current_toorate_past_toorate)

		toorate_compare = '높은' if current_toorate_past_toorate > 0 else '낮은'
		toorate_compare_add = '선거에 대한 높은 관심을 반영하고 있다' if current_toorate_past_toorate > 0 else '지난 지방선거에 미치지 못했다'

		ranks = sess.query(func.max(CurrentVote.toorate).label('max'), CurrentVote.sun_name1).group_by(CurrentVote.sun_name1).order_by(func.max(CurrentVote.toorate).desc()).all()
		toorate_rank1 = ranks[0][1]
		toorate_rank = ', '.join(rank[1] for rank in ranks[1:5])
		josa = '이'

		data = {
			'current_toorate_past_toorate': round(current_toorate_past_toorate, 2),
			'toorate_compare': toorate_compare,
			'toorate_compare_add': toorate_compare_add,
			'toorate_rank1': toorate_rank1,
			'toorate_rank': toorate_rank,
			'josa': josa
		}
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
			'toorate_region2': round(toorate_region2[0],2),
			'toorate_compare2': toorate_compare2,
		}
		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		map = generateMap(region2, each_toorate.all())

	elif card_seq is 5:
		each_openrate = sess.query(func.max(OpenSido.openrate).label('max')).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name1)
		openrate_avg_nat = sess.query(func.avg(each_openrate.subquery().columns.max)).first()

		openrate_seoul = sess.query(func.max(OpenSido.openrate)).filter(OpenSido.sendtime<=time, OpenSido.sun_name1=='서울').first()

		openrate_gyeonggi = sess.query(func.max(OpenSido.openrate)).filter(OpenSido.sendtime<=time, OpenSido.sun_name1=='경기').first()

		data = {
			'hour': hourConverter(time.hour),
			'openrate_avg_nat': round(openrate_avg_nat[0], 2),
			'openrate_seoul': round(openrate_seoul[0], 2),
			'openrate_gyeonggi': round(openrate_gyeonggi[0], 2),
		}
		RANK1 = 'default'
		title = hourConverter(time.hour) + ', 평균 개표율'
		rate = round(openrate_avg_nat[0])
		name = None
		graph = None
		map = None

	elif card_seq is 6:
		openrate_sunname1_rank1 = sess.query(func.max(OpenSido.openrate).label('max'), OpenSido.sun_name1).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name1).order_by(func.max(OpenSido.openrate).desc()).first()

		openrate_sunname2_rank1 = sess.query(func.max(OpenSido.openrate).label('max'), OpenSido.sun_name2, OpenSido.sun_name1).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name2).order_by(func.max(OpenSido.openrate).desc()).first()

		data = {
			'hour': hourConverter(time.hour),
			'openrate_sunname1_rank1': openrate_sunname1_rank1[1],
			'openrate_sunname2_rank1': openrate_sunname2_rank1[1],
			'openrate_sunname2_rank1_rate': round(openrate_sunname2_rank1[0], 2),
		}
		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = generateGraph(openrate_sunname1_rank1)
		map = None

	elif card_seq is 7:
		region1 = region[0]

		openrate_region1 = sess.query(func.max(OpenSido.openrate)).filter(OpenSido.sendtime<=time, OpenSido.sun_name1==region1).first()

		each_openrate = sess.query(func.max(OpenSido.openrate).label('max'), OpenSido.sun_name1.label('name')).filter(OpenSido.sendtime<=time).group_by(OpenSido.sun_name1).subquery()
		openrate_avg_nat = sess.query(func.avg(each_openrate.c.max)).first()

		if openrate_region1[0] == 0:
			region1_exception = text_templates['7-0']
		else:
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
			'region1_exception': region1_exception,
			'region2': region2,
			'openrate_region2': round(openrate_region2[0], 2),
			'region2_exception': region2_exception,
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

	return data, RANK1, title, rate, name, graph, map
