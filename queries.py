from templates import text_templates
from orm import *
from sqlalchemy.sql import func
from graph import generateMap, generateGraph
import pandas as pd
from timeit import default_timer as timer
import tossi
from collections import Counter
import numpy as np
from decimal import *
import datetime
from random import randint

class NoTextError(Exception):
	pass

def hourConverter(h):
	if h < 12:
		return '오전 ' + str(h) + '시'
	elif h == 12:
		return '오후 ' + str(h) + '시'
	else:
		return '오후 ' + str(h - 12) + '시'

def josaPick(word, josa):
	return tossi.pick(word, josa)

def regionPoll(r, code):
	if r.endswith('시'):
		poll = '시장'
	elif r.endswith('도'):
		poll = '도지사'
	elif r.endswith('구'):
		poll = '구청장'
	elif r.endswith('군'):
		poll = '군수'
	elif code == 2:
		poll = '국회의원'
	elif code == 11:
		poll = '교육감'
	else:
		poll = None
	return poll

def openTable(code):
	if code == 2:
		return OpenProgress2
	elif code == 3:
		return OpenProgress3
	elif code == 4:
		return OpenProgress4
	elif code == 11:
		return OpenProgress11
	else:
		return OpenProgress

# TODO: parallel, 중복 쿼리 가지 않도록 새로운 데이터 있는지 체크
def query_card_data(order, index, polls, regions, parties, candidates, time, card_seq):
	if card_seq is 1:
		# TODO: 파라미터 선택하지 않았을 때 , 선택한거 다 보여주기
		customs = []
		text = text_templates[card_seq].format('#' + ' #'.join(customs))

		meta_card = {
			'order': order,
			'type': 'cover',
			'party': 'default',
			'data': {'tags': text}
		}

	elif card_seq is 2:
		# each_toorate = sess.query(func.max(VoteProgress.tooRate).label('max')).filter(VoteProgress.timeslot<=time.hour).group_by(VoteProgress.sido).subquery()
		# toorate_avg_nat = sess.query(func.avg(each_toorate.c.max)).scalar()
		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t = 23
		else:
			t = time.hour

		each_toorate = sess.query(func.max(VoteProgress.yooToday).label('yooToday'), func.max(VoteProgress.yooEarly).label('yooEarly'), func.max(VoteProgress.tooToday).label('tooToday'), func.max(VoteProgress.tooEarly).label('tooEarly')).filter(VoteProgress.timeslot<=t).group_by(VoteProgress.sido).subquery()
		yooToday, yooEarly, tooToday, tooEarly = sess.query(func.sum(each_toorate.c.yooToday), func.sum(each_toorate.c.yooEarly), func.sum(each_toorate.c.tooToday), func.sum(each_toorate.c.tooEarly)).first()
		toorate_avg_nat = (tooToday+tooEarly) / (yooToday+yooEarly) * 100

		data = {
			'toorate_avg_nat': round(toorate_avg_nat, 2),
		}
		if t > 18:
			text = text_templates[2].format(**data)
			title = '최종 투표율'
		else:
			data['hour'] = hourConverter(time.hour)
			text = text_templates['2-1'].format(**data)
			title = hourConverter(time.hour) + ', 현재 투표율'

		meta_card = {
			'order': order,
			'type': 'rate',
			'party': 'default',
			'data': {
				'title': title,
				'rate': round(toorate_avg_nat),
				'text': text,
			}
		}

	elif card_seq is 3:
		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t = 23
		else:
			t = time.hour
		# past = sess.query(func.max(PastVoteProgress.tooRate).label('max')).filter(PastVoteProgress.timeslot <= time.hour).group_by(PastVoteProgress.sido).subquery()
		# past_toorate = sess.query(func.avg(past.c.max)).scalar()
		each_toorate_p = sess.query(func.max(PastVoteProgress.yooToday).label('yooToday'), func.max(PastVoteProgress.yooEarly).label('yooEarly'), func.max(PastVoteProgress.tooToday).label('tooToday'), func.max(PastVoteProgress.tooEarly).label('tooEarly')).filter(PastVoteProgress.timeslot<=t).group_by(PastVoteProgress.sido).subquery()
		yooToday_p, yooEarly_p, tooToday_p, tooEarly_p = sess.query(func.sum(each_toorate_p.c.yooToday), func.sum(each_toorate_p.c.yooEarly), func.sum(each_toorate_p.c.tooToday), func.sum(each_toorate_p.c.tooEarly)).first()
		past_toorate = (tooToday_p+tooEarly_p) / (yooToday_p+yooEarly_p) * 100

		# current = sess.query(func.max(VoteProgress.tooRate).label('max')).filter(VoteProgress.timeslot <= time.hour).group_by(VoteProgress.sido).subquery()
		# current_toorate = sess.query(func.avg(current.c.max)).scalar()
		each_toorate = sess.query(func.max(VoteProgress.yooToday).label('yooToday'), func.max(VoteProgress.yooEarly).label('yooEarly'), func.max(VoteProgress.tooToday).label('tooToday'), func.max(VoteProgress.tooEarly).label('tooEarly')).filter(VoteProgress.timeslot<=t).group_by(VoteProgress.sido).subquery()
		yooToday, yooEarly, tooToday, tooEarly = sess.query(func.sum(each_toorate.c.yooToday), func.sum(each_toorate.c.yooEarly), func.sum(each_toorate.c.tooToday), func.sum(each_toorate.c.tooEarly)).first()
		current_toorate = (tooToday+tooEarly) / (yooToday+yooEarly) * 100

		current_toorate_past_toorate = current_toorate - past_toorate

		toorate_compare = '높은' if current_toorate_past_toorate > 0 else '낮은'

		ranks = sess.query(func.max(VoteProgress.tooRate).label('max'), VoteProgress.sido).filter(VoteProgress.timeslot<=t).group_by(VoteProgress.sido).order_by(func.max(VoteProgress.tooRate).desc()).all()
		# print(ranks)

		toorate_rank1 = ranks[0][1]
		toorate_rank = ', '.join(rank[1] for rank in ranks[1:5])

		data = {
			'past_toorate': round(past_toorate, 2),
			'current_toorate_past_toorate': round(abs(current_toorate_past_toorate), 2),
			'toorate_compare': toorate_compare,
			'toorate_rank1': toorate_rank1,
			'toorate_rank': toorate_rank,
			'josa': josaPick(toorate_rank[-1], '이')
		}

		if t > 18:
			text = text_templates[card_seq].format(**data)
		else:
			text = text_templates['3-1'].format(**data)

		map_data = []
		for v, r in ranks:
			if r == '합계':
				pass
			else:
				map_data.append({'name':r, 'value':float(v)*0.01})
		# print(map_data)

		meta_card = {
			'order': order,
			'type': 'map',
			'party': 'default',
			'data': {
				'map_data': {
					'area': '전국',
					'party': 'default',
					'data': map_data,
				},
				'text': text,
			}
		}

	elif card_seq is 4:
		region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.sggCityCode==regions[index]).first()

		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t = 23
		else:
			t = time.hour

		# 서울, 서울
		toorate_region1 = sess.query(func.max(VoteProgress.tooRate)).filter(VoteProgress.timeslot<=t, VoteProgress.sido==region1).scalar()

		each_toorate = sess.query(func.max(VoteProgress.yooToday).label('yooToday'), func.max(VoteProgress.yooEarly).label('yooEarly'), func.max(VoteProgress.tooToday).label('tooToday'), func.max(VoteProgress.tooEarly).label('tooEarly')).filter(VoteProgress.timeslot<=t).group_by(VoteProgress.sido).subquery()
		yooToday, yooEarly, tooToday, tooEarly = sess.query(func.sum(each_toorate.c.yooToday), func.sum(each_toorate.c.yooEarly), func.sum(each_toorate.c.tooToday), func.sum(each_toorate.c.tooEarly)).first()
		toorate_avg_nat = (tooToday+tooEarly) / (yooToday+yooEarly) * 100

		toorate_region1_toorate_avg_nat = toorate_region1 - toorate_avg_nat

		toorate_compare1 = '높은' if toorate_region1_toorate_avg_nat > 0 else '낮은'

		data = {
			'region1': region1,
			'toorate_region1': round(toorate_region1, 2),
			'toorate_region1_toorate_avg_nat': round(abs(toorate_region1_toorate_avg_nat),2),
			'toorate_compare1': toorate_compare1,
		}

		if t > 18:
			text = text_templates[card_seq].format(**data)
		else:
			text = text_templates['4-1'].format(**data)

		toorate_region1_sub = sess.query(VoteProgressLatest.tooRate, VoteProgressLatest.gusigun).filter(VoteProgressLatest.timeslot<=t, VoteProgressLatest.sido==region1).all()
		# print(region1)
		# print(toorate_region1_sub)
		map_data = []
		for v, r in toorate_region1_sub:
			if r == '합계':
				pass
			else:
				map_data.append({'name':r, 'value':float(v)*0.01})
		# print(map_data)
		meta_card = {
			'order': order,
			'type': 'map',
			'party': 'default',
			'data': {
				'map_data': {
					'area': region1,
					'party': 'default',
					'data': map_data,
				},
				'text': text,
			}
		}

	elif card_seq is 5:
		candidate, candidate_region, candidate_sdName = sess.query(CandidateInfo.name, CandidateInfo.sggName, CandidateInfo.sdName).filter(CandidateInfo.huboid==candidates[index]).first()

		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t = 23
		else:
			t = time.hour

		candidate_region_toorate = sess.query(func.max(VoteProgress.tooRate)).filter(VoteProgress.timeslot<=t, VoteProgress.sido==candidate_sdName).scalar()
		# VoteProgress에 sggName 필요함

		data = {
			'candidate': candidate,
			'candidate_region': candidate_region,
			'candidate_region_toorate': candidate_region_toorate,
		}
		if t > 18:
			text = text_templates[card_seq].format(**data)
		else:
			data['hour'] = hourConverter(time.hour)
			text = text_templates['5-1'].format(**data)

		candidate_region_sub = sess.query(VoteProgressLatest.tooRate, VoteProgressLatest.gusigun).filter(VoteProgressLatest.timeslot<=t, VoteProgressLatest.sido==candidate_sdName).all()
		# print(candidate_sdName)
		# print(candidate_region_sub)
		map_data = []
		for v, r in candidate_region_sub:
			if r == '합계':
				pass
			else:
				map_data.append({'name':r, 'value':float(v)*0.01})
		# print(map_data)
		meta_card = {
			'order': order,
			'type': 'map',
			'party': 'default',
			'data': {
				'map_data': {
					'area': candidate_sdName,
					'party': 'default',
					'data': map_data,
				},
				'text': text,
			}
		}
		

	elif card_seq is 6:
		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t = 23
		else:
			t = time.hour

		each_toorate_p = sess.query(PastVoteProgress.sido, func.max(PastVoteProgress.yooToday).label('yooToday'), func.max(PastVoteProgress.yooEarly).label('yooEarly'), func.max(PastVoteProgress.tooToday).label('tooToday'), func.max(PastVoteProgress.tooEarly).label('tooEarly')).filter(PastVoteProgress.timeslot<=t).group_by(PastVoteProgress.sido)

		yooToday_p, yooEarly_p, tooToday_p, tooEarly_p = sess.query(func.sum(each_toorate_p.subquery().c.yooToday), func.sum(each_toorate_p.subquery().c.yooEarly), func.sum(each_toorate_p.subquery().c.tooToday), func.sum(each_toorate_p.subquery().c.tooEarly)).first()
		past_toorate = (tooToday_p+tooEarly_p) / (yooToday_p+yooEarly_p) * 100

		each_toorate = sess.query(VoteProgress.sido, func.max(VoteProgress.yooToday).label('yooToday'), func.max(VoteProgress.yooEarly).label('yooEarly'), func.max(VoteProgress.tooToday).label('tooToday'), func.max(VoteProgress.tooEarly).label('tooEarly')).filter(VoteProgress.timeslot<=t).group_by(VoteProgress.sido)
		
		yooToday, yooEarly, tooToday, tooEarly = sess.query(func.sum(each_toorate.subquery().c.yooToday), func.sum(each_toorate.subquery().c.yooEarly), func.sum(each_toorate.subquery().c.tooToday), func.sum(each_toorate.subquery().c.tooEarly)).first()
		current_toorate = (tooToday+tooEarly) / (yooToday+yooEarly) * 100

		current_toorate_past_toorate = current_toorate - past_toorate

		past = sess.query(PastVoteProgress.sido, func.max(PastVoteProgress.tooRate).label('max')).filter(PastVoteProgress.timeslot <= t, PastVoteProgress.gusigun=='합계').group_by(PastVoteProgress.sido)
		current = sess.query(VoteProgress.sido, func.max(VoteProgress.tooRate).label('max')).filter(VoteProgress.timeslot <= t).group_by(VoteProgress.sido)
		currentDf = pd.DataFrame(current.all())
		pastDf = pd.DataFrame(past.all())
		currentPastDf = pd.merge(currentDf, pastDf, on='sido')
		# print(currentPastDf['max_x'] - currentPastDf['max_y'])
		if t > 18:
			text = text_templates[card_seq] if current_toorate_past_toorate > 0 else text_templates['6-0']
		else:
			# print(current.all())
			# print(past.all())
			# ratio = sum([1 for s in np.subtract(current.all(), past.all()) if s > 0]) / len(current.all())
			ratio = sum([1 for s in (currentPastDf['max_x'] - currentPastDf['max_y']).values if s > 0]) / len(currentDf['sido'])
			# print(ratio)
			if current_toorate_past_toorate >= 5:
				text = text_templates['6-1']
			elif ratio >= 0.8:
				text = text_templates['6-2']
			else:
				# text = None
				raise NoTextError
				
		meta_card = {
			'order': order,
			'type': 'default',
			'party': 'default',
			'data': {
				'text': text,
			}
		}

	elif card_seq is 7:
		each_openrate = sess.query(func.max(OpenProgress.openPercent).label('max')).filter(OpenProgress.datatime<=time).group_by(OpenProgress.cityCode).subquery()
		openrate_avg_nat = sess.query(func.avg(each_openrate.c.max)).scalar()
		# 

		data = {
			'hour': hourConverter(time.hour),
			'openrate_avg_nat': round(openrate_avg_nat, 2),
		}

		text = text_templates[card_seq].format(**data)
		# RANK1 = 'default'
		# title = hourConverter(time.hour) + ', 평균 개표율'
		# rate = round(openrate_avg_nat)
		# name = None
		# graph = None
		# map = None
		meta_card = {
			'order': order,
			'type': 'rate',
			'party': 'default',
			'data': {
				'title': hourConverter(time.hour) + ', 평균 개표율',
				'rate': round(openrate_avg_nat),
				'text': text,
			}
		}

	elif card_seq is 8:
		openrate_sunname1_ranks = sess.query(OpenProgress3.openPercent.label('max'), OpenProgress3.sido).filter(OpenProgress3.datatime<=time).group_by(OpenProgress3.cityCode).order_by(func.max(OpenProgress3.openPercent).desc()).all()
		#[(Decimal('60.00'), '충청남도'), (Decimal('56.00'), '서울특별시'), (Decimal('55.00'), '부산광역시')]

		# TODO: find openrat == 100
		openDf = pd.DataFrame(openrate_sunname1_ranks)
		print(openDf)
		if len(openDf.loc[openDf['max']==100,'sido']):
			open_finished = ', '.join(openDf.loc[openDf['max']==100,'sido'])
			openrate_sunname1_rank1 = openDf.loc[openDf['max']!=100,].iloc[0]
			data = {
				'hour': hourConverter(time.hour),
				'open_finished': open_finished,
				'openrate_sunname1_rank1': openrate_sunname1_rank1['sido'],
				'openrate_sunname1_rank1_rate': openrate_sunname1_rank1['max'],
			}
			text = text_templates['8-1'].format(**data)
		else:
			data = {
				'hour': hourConverter(time.hour),
				'openrate_sunname1_rank1': openrate_sunname1_ranks[0][1],
				'josa': josaPick(openrate_sunname1_ranks[0][1],'으로'),
				'openrate_sunname1_rank1_rate': round(openrate_sunname1_ranks[0][0], 2),
				'openrate_sunname1_rank2': openrate_sunname1_ranks[1][1],
				'openrate_sunname1_rank2_rate': round(openrate_sunname1_ranks[1][0], 2),
			}
			text = text_templates[card_seq].format(**data)

		# RANK1 = 'default'
		# title = None
		# rate = None
		# name = None
		# graph = None
		# map = None ## 
		# map = generateMap('전국', openrate_sunname1_ranks)
		meta_card = {
			'order': order,
			'type': 'map',
			'party': 'default',
			'data': {
				'map_data': {
					'area': '전국',
					'party': 'default',
					'data': map_data,
				},
				'text': text,
			}
		}

	elif card_seq is 9:
		openrate_sunname2_ranks = sess.query(func.max(OpenProgress.openPercent).label('max'), OpenProgress.sido, OpenProgress.gusigun).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==4).group_by(OpenProgress.sggCityCode).order_by(func.max(OpenProgress.openPercent).desc()).all()
		# sggCityCode 매치 안됨, OpenProgress, PrecinctCode
		# 시군구청장 선거 group by 뭘로
		print(openrate_sunname2_ranks)


		openDf = pd.DataFrame(openrate_sunname2_ranks)
		if len(openDf.loc[openDf['max']==100,'gusigun']):
			open_finished = ', '.join(openDf.loc[openDf['max']==100,'gusigun'])
			openrate_sunname2_rank1 = openDf.loc[openDf['max']!=100,].iloc[0]
			data = {
				'hour': hourConverter(time.hour),
				'open_finished': open_finished,
				'openrate_sunname2_rank1': openrate_sunname2_rank1['gusigun'],
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
		region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.sggCityCode==regions[index]).first()

		each_openrate = sess.query(func.max(OpenProgress.openPercent).label('max'), OpenProgress.sido.label('name')).filter(OpenProgress.datatime<=time).group_by(OpenProgress.cityCode).subquery()

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

			openrate_region1_sub = sess.query(func.max(OpenProgress.openPercent), OpenProgress.sido).filter(OpenProgress.datatime<=time).group_by(OpenProgress.sido).all()
			# map = generateMap('전국', openrate_region1_sub)
			map = None
	
		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None

	elif card_seq is 11:
		poll, poll_num_sunname = sess.query(SgTypecode.sgName, func.count(PrecinctCode.sggCityCode)).join(PrecinctCode, PrecinctCode.electionCode==SgTypecode.sgTypecode).filter(SgTypecode.sgTypecode==polls[index]).first()

		# poll 종류에 대해 달라져야함, OpenSido / OpenGusigun ...
		# poll 종류에 따라 table을 선택하고, table마다 column name은 같도록
		# Open = openTable(polls[index])
		if polls[index] == 2: # 국회의원
			each_openrate = sess.query(func.max(OpenProgress2.openPercent).label('max'), OpenProgress2.sgg).filter(OpenProgress2.datatime<=time).group_by(OpenProgress2.sgg).order_by(func.max(OpenProgress2.openPercent).desc()).subquery()
		elif polls[index] == 3:
			each_openrate = sess.query(func.max(OpenProgress3.openPercent).label('max'), OpenProgress3.sido).filter(OpenProgress3.datatime<=time).group_by(OpenProgress3.sido).order_by(func.max(OpenProgress3.openPercent).desc()).subquery()
		elif polls[index] == 4:
			each_openrate = sess.query(func.max(OpenProgress4.openPercent).label('max'), OpenProgress4.gusigun).filter(OpenProgress4.datatime<=time).group_by(OpenProgress4.gusigun).order_by(func.max(OpenProgress4.openPercent).desc()).subquery()
		elif polls[index] == 11:
			each_openrate = sess.query(func.max(OpenProgress11.openPercent).label('max'), OpenProgress11.sido).filter(OpenProgress11.datatime<=time).group_by(OpenProgress11.sido).order_by(func.max(OpenProgress11.openPercent).desc()).subquery()
		else:
			each_openrate = sess.query(func.max(OpenProgress.openPercent).label('max'), OpenProgress.sido).filter(OpenProgress.datatime<=time).group_by(OpenProgress.sido).order_by(func.max(OpenProgress.openPercent).desc()).subquery()

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
		# map = generateMap('전국', poll_openrate_ranks)
		map = None

	elif card_seq is 12:
		candidate, candidate_region, candidate_poll_code = sess.query(CandidateInfo.name, CandidateInfo.sggName, CandidateInfo.sgTypecode).filter(CandidateInfo.huboid==candidates[index]).first()
		# sggName에서 regionPoll 

		candidate_poll = regionPoll(candidate_region, candidate_poll_code)
		print(candidate_region)
		# candidate_poll에 맞게 테이블 선택		
		if candidate_poll_code == 2: # 국회의원
			candidate_poll_openrate = sess.query(func.max(OpenProgress2.openPercent)).filter(OpenProgress2.datatime<=time, OpenProgress2.sgg==candidate_region).scalar()
		elif candidate_poll_code == 3:
			candidate_poll_openrate = sess.query(func.max(OpenProgress3.openPercent)).filter(OpenProgress3.datatime<=time,  OpenProgress3.sido==candidate_region).scalar()
		elif candidate_poll_code == 4:
			candidate_poll_openrate = sess.query(func.max(OpenProgress4.openPercent)).filter(OpenProgress4.datatime<=time, OpenProgress4.gusigun==candidate_region).scalar()
		elif candidate_poll_code == 11:
			candidate_poll_openrate = sess.query(func.max(OpenProgress11.openPercent)).filter(OpenProgress11.datatime<=time, OpenProgress11.sido==candidate_region).scalar()
		else:
			candidate_poll_openrate = sess.query(func.max(OpenProgress.openPercent)).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==candidate_poll_code, OpenProgress.sido==candidate_region).scalar()

		data = {
			'candidate': candidate,
			'candidate_region': candidate_region,
			'candidate_poll': candidate_poll,
			'candidate_poll_openrate': candidate_poll_openrate,
		}
		
		if candidate_poll_openrate is None:
			text = text_templates['12-1'].format(**data)
		elif candidate_poll_openrate == 100:
			text = text_templates['12-2'].format(**data)
		else:
			text = text_templates[card_seq].format(**data)

		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		# map = generateMap(region1, openrate_region1_sub)
		map = None

	elif card_seq is 13:
		each_openrate = sess.query(func.max(OpenProgress.openPercent).label('max')).filter(OpenProgress.datatime<=time).group_by(OpenProgress.sgg).subquery()
		openrate_avg_nat = sess.query(func.avg(each_openrate.c.max)).scalar()

		if openrate_avg_nat < 100:
			openrate_sido = sess.query(OpenProgress3.sido).filter(OpenProgress3.openPercent==100).group_by(OpenProgress3.sido).order_by(OpenProgress3.datatime.asc()).all()
			if len(openrate_sido) > 0:
				data = {
					'hour': hourConverter(time.hour),
					'open_finished_sido': ', '.join(sido[0] for sido in openrate_sido),
				}
				text = text_templates[card_seq].format(**data)
			else:
				text = ''

			openrate_gusigun = sess.query(OpenProgress4.gusigun).filter(OpenProgress4.openPercent==100).group_by(OpenProgress4.gusigun).order_by(OpenProgress4.datatime.asc()).all()
			if len(openrate_gusigun) > 0:
				data = {
					'hour': hourConverter(time.hour),
					'open_finished_gusigun': ', '.join(gusigun[0] for gusigun in openrate_gusigun),
				}
				text += text_templates['13-1'].format(**data)
			else:
				text += ''
		else:
			text = text_templates['13-2'].format(hour=hourConverter(time.hour))

		text = None if text == '' else text
		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		map = None

	elif card_seq is 14:
		sub_ranks = sess.query(OpenProgress3).filter(OpenProgress3.datatime<=time).group_by(OpenProgress3.sido)
		ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
		ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)	
		print(ranks_vote)
		ranks_ttl = []
		for i, ranks in ranks_vote.iterrows():
			ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])
		# 각 group 마다 랭킹 만들기
		ranking = []
		for i, ranks in enumerate(ranks_ttl):
			ranking.append(ranksDf.loc[i, ranks[0]+'_jdName'])
		ranking = Counter(ranking).most_common(3)
		rank1_party = ranking[0][0]
		rank1_party_num = ranking[0][1]

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
		candidate_poll_code = sess.query(CandidateInfo.SgTypeCode).filter(CandidateInfo.huboid==candidates[index]).first()

		if len(regions) == 0:
			if candidate_poll_code is 3 or polls[index] is 3: # 시도지사
				sub_ranks = sess.query(OpenProgress3).filter(OpenProgress3.datatime<=time).group_by(OpenProgress3.sido)
				ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
				ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)

				ranks_ttl = []
				for i, ranks in ranks_vote.iterrows():
					ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])

				ranking1 = [] # 1위만	
				ranking2 = []
				ranking3 = []
				for i, ranks in enumerate(ranks_ttl):
					ranking1.append(ranksDf.loc[i, ranks[0]+'_jdName'])
					ranking2.append(ranksDf.loc[i, ranks[1]+'_jdName'])
					try:
						ranking3.append(ranksDf.loc[i, ranks[3]+'_jdName'])
					except IndexError:
						pass

				ranking1 = Counter(ranking1).most_common()[0]
				rank1_party = ranking1[0]
				rank1_party_num = ranking1[1]
				ranking2 = Counter(ranking2).most_common()[0]

				try:
					ranking3 = Counter(ranking3).most_common()[0]
					ranks_party = ranking2[0] + ', ' + ranking3[0]
				except IndexError:
					ranks_party = ranking2[0]

				data = {
					'hour': hourConverter(time.hour),
					'rank1_party': rank1_party, 
					'josa1': josaPick(rank1_party, '이'),
					'rank1_party_num': rank1_party_num,
					'ranks_party': ranks_party,
					'josa2': josaPick(ranks_party[-1], '이'),
				}
				text = text_templates[card_seq].format(**data)
		
			elif candidate_poll_code is 4 or polls[index] is 4: # 시군구청장
				sub_ranks = sess.query(OpenProgress4).filter(OpenProgress4.datatime<=time).group_by(OpenProgress4.gusigun)
				ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
				ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)
				
				ranks_ttl = []
				for i, ranks in ranks_vote.iterrows():
					ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])

				ranking1 = [] # 1위만	
				ranking2 = []
				ranking3 = []
				for i, ranks in enumerate(ranks_ttl):
					ranking1.append(ranksDf.loc[i, ranks[0]+'_jdName'])
					ranking2.append(ranksDf.loc[i, ranks[1]+'_jdName'])
					try:
						ranking3.append(ranksDf.loc[i, ranks[3]+'_jdName'])
					except IndexError:
						pass

				ranking1 = Counter(ranking1).most_common()[0]
				rank1_party = ranking1[0]
				rank1_party_num = ranking1[1]
				ranking2 = Counter(ranking2).most_common()[0]

				try:
					ranking3 = Counter(ranking3).most_common()[0]
					ranks_party = ranking2[0] + ', ' + ranking3[0]
				except IndexError:
					ranks_party = ranking2[0]
				data = {
					'hour': hourConverter(time.hour),
					'rank1_party': rank1_party,
					'josa1': josaPick(rank1_party, '이'),
					'rank1_party_num': rank1_party_num,
					'ranks_party': ranks_party, 
					'josa2': josaPick(ranks_party[-1], '이'),
				}
				text = text_templates['15-1'].format(**data)

			elif candidate_poll_code is 2 or polls[index] is 2: # 국회의원
				sub_ranks = sess.query(OpenProgress2).filter(OpenProgress2.datatime<=time).group_by(OpenProgress2.sgg)
				ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
				ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)
				
				ranks_ttl = []
				for i, ranks in ranks_vote.iterrows():
					ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])

				ranking1 = [] # 1위만	
				ranking2 = []
				ranking3 = []
				for i, ranks in enumerate(ranks_ttl):
					ranking1.append(ranksDf.loc[i, ranks[0]+'_jdName'])
					ranking2.append(ranksDf.loc[i, ranks[1]+'_jdName'])
					try:
						ranking3.append(ranksDf.loc[i, ranks[3]+'_jdName'])
					except IndexError:
						pass

				ranking1 = Counter(ranking1).most_common()[0]
				rank1_party = ranking1[0]
				rank1_party_num = ranking1[1]
				ranking2 = Counter(ranking2).most_common()[0]

				try:
					ranking3 = Counter(ranking3).most_common()[0]
					ranks_party = ranking2[0] + ', ' + ranking3[0]
				except IndexError:
					ranks_party = ranking2[0]

				data = {
					'hour': hourConverter(time.hour),
					'rank1_party': rank1_party, 
					'josa1': josaPick(rank1_party, '이'),
					'rank1_party_num': rank1_party_num,
					'ranks_party': ranks_party, 
					'josa2': josaPick(ranks_party[-1], '이'),
				}
				text = text_templates['15-2'].format(**data)

			elif candidate_poll_code is 11 or polls[index] is 11: # 교육감
				
				openrate_rank1_region = sess.query(OpenProgress11.sido).filter(OpenProgress11.datatime<=time).group_by(OpenProgress11.sido).order_by(OpenProgress11.openPercent.desc()).fisrt()

				sub_ranks = sess.query(OpenProgress11).filter(OpenProgress11.datatime<=time, OpenProgress11.sido==openrate_rank1_region).group_by(OpenProgress11.sido)
				ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
				ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)
				
				ranks_ttl = []
				for i, ranks in ranks_vote.iterrows():
					ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])

				ranking1 = [] # 1위만	
				ranking2 = []
				# ranking3 = []
				for i, ranks in enumerate(ranks_ttl):
					ranking1.append(ranksDf.loc[i, ranks[0]+'_name'])
					ranking2.append(ranksDf.loc[i, ranks[1]+'_name'])
					# try:
					# 	ranking3.append(ranksDf.loc[i, ranks[3]+'_mame'])
					# except IndexError:
					# 	pass

				ranking1 = Counter(ranking1).most_common()[0]
				openrate_rank1_region_candidate = ranking1[0]
				# rank1_party_num = ranking1[1]
				ranking2 = Counter(ranking2).most_common()[0]
				openrate_rank2_region_candidate = ranking2[0]

				# try:
				# 	ranking3 = Counter(ranking3).most_common()[0]
				# 	ranks_party = ranking2[0] + ', ' + ranking3[0]
				# except IndexError:
				# 	ranks_party = ranking2[0]

				data = {
					'hour': hourConverter(time.hour),
					'openrate_rank1_region': openrate_rank1_region,
					'openrate_rank1_region_candidate': openrate_rank1_region_candidate, 
					'openrate_rank2_region_candidate': openrate_rank2_region_candidate,
				}
				text = text_templates['15-3'].format(**data)
		else:
			text = None	

		RANK1 = rank1_party
		title = hourConverter(time.hour) + ', ' + str(rank1_party_num) + '개 선거구 1위'
		rate = None
		name = rank1_party
		graph = None
		map = None

	elif card_seq is 16:
		region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.sggCityCode==regions[index]).first()
		
		region1_poll = regionPoll(region1)

		region1_openrate = sess.query(func.max(OpenProgress3.openPercent)).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==region1).scalar()

		sub_ranks = sess.query(OpenProgress3).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==region1).group_by(OpenProgress3.sido)
		ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
		ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)	

		ranks_ttl = []
		for i, ranks in ranks_vote.iterrows():
			ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])
		
		ranking1 = [] # 1위만	
		ranking2 = []
		for i, ranks in enumerate(ranks_ttl):
			ranking1.append(ranks[0])
			ranking2.append(ranks[1])
			# try:
			# 	ranking3.append(ranksDf.loc[i, ranks[3]+'_mame'])
			# except IndexError:
			# 	pass

		# ranking1 = Counter(ranking1).most_common()[0]
		# ranking2 = Counter(ranking2).most_common()[0]

		region1_rank1_party = ranksDf[anking1[0]+'_jdName']
		region1_rank1_name = ranksDf[ranking1[0]+'_name']
		region1_rank1_rate = ranksDf[anking1[0]+'_percent']

		region1_rank2_party = ranksDf[ranking2[0]+'_jdName']
		region1_rank2_name = ranksDf[ranking2[0]+'_name']
		region1_rank2_rate = ranksDf[ranking2[0]+'_percent']

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

		rank1_cnt = ranksDf[ranking1[0]+'_vote']
		rank2_cnt = ranksDf[ranking2[0]+'_vote']
		yet_cnt = ranksDf.tooTotal - ranksDf.n_total - ranksDf.invalid
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
		# graph_data = [(region1_rank1_rate, region1_rank1_party + ' ' + region1_rank1_name), (region1_rank2_rate, region1_rank2_party + ' ' + region1_rank2_name)]
		# graph = generateGraph(graph_data)
		graph = None
		map = None

	elif card_seq is 17:
		candidate, candidate_region, sgtype = sess.query(CandidateInfo.name, CandidateInfo.sggName, CandidateInfo.sgTypecode).filter(CandidateInfo.huboid==candidates[index]).first()
		candidate_poll = regionPoll(candidate_region, sgtype)

		# candidate_poll table 선택
		if sgtype is 2: 
			candidate_poll_openrate = sess.query(func.max(OpenProgress2.openPercent)).filter(OpenProgress2.datatime<=time, OpenProgress2.sgg==candidate_region).scalar()
			sub_ranks = sess.query(OpenProgress2).filter(OpenProgress2.datatime<=time, OpenProgress2.sgg==candidate_region).group_by(OpenProgress2.sgg)
		elif sgtype is 3:
			candidate_poll_openrate = sess.query(func.max(OpenProgress3.openPercent)).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==candidate_region).scalar()
			sub_ranks = sess.query(OpenProgress3).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==candidate_region).group_by(OpenProgress3.sido)
		elif sgtype is 4:
			candidate_poll_openrate = sess.query(func.max(OpenProgress4.openPercent)).filter(OpenProgress4.datatime<=time, OpenProgress4.gusigun==candidate_region).scalar()
			sub_ranks = sess.query(OpenProgress4).filter(OpenProgress4.datatime<=time, OpenProgress4.gusigun==candidate_region).group_by(OpenProgress4.gusigun)
		elif sgtype is 11:
			candidate_poll_openrate = sess.query(func.max(OpenProgress11.openPercent)).filter(OpenProgress11.datatime<=time,OpenProgress11.sido==candidate_region).scalar()
			sub_ranks = sess.query(OpenProgress11).filter(OpenProgress11.datatime<=time, OpenProgress11.sido==candidate_region).group_by(OpenProgress11.sido)

		ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
		ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)
		
		ranks_ttl = []
		for i, ranks in ranks_vote.iterrows():
			ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])

		ranking1 = [] # 1위만	
		ranking2 = []
		for i, ranks in enumerate(ranks_ttl):
			ranking1.append(ranks[0])
			ranking2.append(ranks[1])

		# ranking1 = Counter(ranking1).most_common()[0]
		# ranking2 = Counter(ranking2).most_common()[0]

		candidate_poll_rank1_party = ranksDf[ranking1[0]+'_jdName']
		candidate_poll_rank1_name = ranksDf[ranking1[0]+'_name']
		candidate_poll_rank1_rate = ranksDf[ranking1[0]+'_percent']

		candidate_poll_rank2_party = ranksDf[ranking2[0]+'_jdName']
		candidate_poll_rank2_name = ranksDf[ranking2[0]+'_name']
		candidate_poll_rank2_rate = ranksDf[ranking2[0]+'_percent']

		data = {
			'hour': hourConverter(time.hour),
			'candidate': candidate,
			'candidate_region': candidate_region,
			'candidate_poll': candidate_poll,
			'candidate_poll_rank1_name': candidate_poll_rank1_name,
			'candidate_poll_rank1_rate': candidate_poll_rank1_rate,
			'candidate_poll_rank2_name': candidate_poll_rank2_name,
			'candidate_poll_rank2_rate': candidate_poll_rank2_rate,
		}

		rank1_cnt = ranksDf[ranking1[0]+'_vote']
		rank2_cnt = ranksDf[ranking2[0]+'_vote']
		yet_cnt = ranksDf.tooTotal - ranksDf.n_total - ranksDf.invalid
		confirm = True if (rank1_cnt-rank2_cnt) > yet_cnt else False

		if candidate_poll_rank1_name is candidate: 
			if (region1_rank1_rate - region1_rank2_rate) >= 15:
				text = text_templates['17-3'].format(**data)
			elif (region1_rank1_rate - region1_rank2_rate) < 5:
				text = text_templates['17-1'].format(**data)
			elif confirm:
				text = text_templates['17-6'].format(**data)
			else:
				text = text_templates[card_seq].format(**data)

		elif candidate_poll_rank2_name is candidate:
			if abs(region1_rank1_rate - region1_rank2_rate) >= 15:
				text = text_templates['17-4'].format(**data)
			elif abs(region1_rank1_rate - region1_rank2_rate) < 5:
				text = text_templates['17-2'].format(**data)
			elif confirm:
				text = text_templates['17-7'].format(**data)
			else:
				text = text_templates[card_seq].format(**data)

		else:
			if abs(region1_rank1_rate - region1_rank2_rate) < 5:
				text = text_templates['17-5'].format(**data)
			else:
				text = text_templates[card_seq].format(**data)
		
		# text = None
		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		map = None
		

	elif card_seq is 18:
		# party = sess.query(PartyCode.jdName).filter(PartyCode.pOrder==parties[index]).scalar()
		
		# # 시도지사
		# sub_ranks = sess.query(OpenProgress3).filter(OpenProgress3.datatime<=time).group_by(OpenProgress3.sido)
		# ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
		# ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)

		# ranks_ttl = []
		# for i, ranks in ranks_vote.iterrows():
		# 	ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])

		# ranking1 = [] # 1위만	
		# ranking2 = []
		# ranking3 = []
		# for i, ranks in enumerate(ranks_ttl):
		# 	ranking1.append(ranksDf.loc[i, ranks[0]+'_jdName'])
		# 	ranking2.append(ranksDf.loc[i, ranks[1]+'_jdName'])
		# 	try:
		# 		ranking3.append(ranksDf.loc[i, ranks[3]+'_jdName'])
		# 	except IndexError:
		# 		pass

		# ranking1 = Counter(ranking1).most_common()
		# ranking2 = Counter(ranking2).most_common()
		# try:
		# 	ranking3 = Counter(ranking3).most_common()
		# except IndexError:
		# 	pass
		# # 구시군청장
		# sub_ranks_g = sess.query(OpenProgress4).filter(OpenProgress4.datatime<=time).group_by(OpenProgress4.gusigun)
		# ranksDf_g = pd.read_sql(sub_ranks_g.statement, sub_ranks_g.session.bind)
		# ranks_vote_g = ranksDf_g.filter(regex="n*_percent").dropna(axis=1)
		
		# ranks_ttl_g = []
		# for i, ranks in ranks_vote_g.iterrows():
		# 	ranks_ttl_g.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])

		# ranking1_g = [] # 1위만	
		# ranking2_g = []
		# ranking3_g = []
		# for i, ranks in enumerate(ranks_ttl_g):
		# 	ranking1_g.append(ranksDf_g.loc[i, ranks[0]+'_jdName'])
		# 	ranking2_g.append(ranksDf_g.loc[i, ranks[1]+'_jdName'])
		# 	try:
		# 		ranking3_g.append(ranksDf_g.loc[i, ranks[3]+'_jdName'])
		# 	except IndexError:
		# 		pass

		# ranking1_g = Counter(ranking1_g).most_common()
		# ranking2_g = Counter(ranking2).most_common()
		# try:
		# 	ranking3_g = Counter(ranking3_g).most_common()
		# except IndexError:
		# 	pass

		# # 
		# my_party_rank1_sido_num = ranking1[party]
		# my_party_rank1_gusigun_num = ranking1_g[party]
		# party_rank1_sido_num = ranking1[0][1]
		# party_rank1_sido_name = ranking1[0][0]
		# party_rank2_sido_num = ranking2[0][1]
		# party_rank2_sido_name = ranking2[0][0]
		# party_rank3_sido_num = ranking3[0][1]
		# party_rank3_sido_name = ranking3[0][0]
		# party_rank1_gusigun_num = ranking1_g[0][1]
		# party_rank123_gusigun_name = ranking1_g[0][0] + ', ' + ranking2_g[0][0] + ', ' + ranking3_g[0][0]


		# data = {
		# 	'party': party,
		# 	'my_party_rank1_sido_num': my_party_rank1_sido_num,
		# 	'my_party_rank1_gusigun_num': my_party_rank1_gusigun_num,
		# 	'party_rank1_sido_num': party_rank1_sido_num,
		# 	'party_rank1_sido_name': party_rank1_sido_name,
		# 	'party_rank2_sido_num': party_rank2_sido_num,
		# 	'party_rank2_sido_name': party_rank2_sido_name,
		# 	'party_rank3_sido_name': party_rank3_sido_name,
		# 	'party_rank3_sido_num': party_rank3_sido_num,
		# 	'party_rank1_gusigun_num': party_rank1_gusigun_num,
		# 	'party_rank123_gusigun_name': party_rank123_gusigun_name,
		# 	'party_rank1_sido_num_confirm': party_rank1_sido_num_confirm,
		# 	'party_rank1_gusigun_num_confirm': party_rank1_gusigun_num_confirm,
		# }	

		

		text = None
		RANK1 = 'default'
		title = None
		rate = None
		name = None
		graph = None
		map = None


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

	elif card_seq is 22:
		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t = 23
		else:
			t = time.hour

		each_toorate = sess.query(func.max(VoteProgress.yooToday).label('yooToday'), func.max(VoteProgress.yooEarly).label('yooEarly'), func.max(VoteProgress.tooToday).label('tooToday'), func.max(VoteProgress.tooEarly).label('tooEarly')).filter(VoteProgress.timeslot<=t).group_by(VoteProgress.sido).subquery()
		yooToday, yooEarly, tooToday, tooEarly = sess.query(func.sum(each_toorate.c.yooToday), func.sum(each_toorate.c.yooEarly), func.sum(each_toorate.c.tooToday), func.sum(each_toorate.c.tooEarly)).first()
		toorate_avg_nat = (tooToday+tooEarly) / (yooToday+yooEarly) * 100

		if toorate_avg_nat < 68.4:
			text = text_templates[22].format(toorate_avg_nat=round(toorate_avg_nat, 2))
		else:
			num = '22-' + str(randint(0,7))
			text = text_templates[num]

		meta_card = {
			'order': order,
			'type': 'default',
			'party': 'default',
			'data': {
				'text': text,
			}
		}

	elif card_seq is 23:
		num = '23-' + str(randint(0,4))
		text = text_templates[num].format(hour=hourConverter(time.hour))
		meta_card = {
			'order': order,
			'type': 'default',
			'party': 'default',
			'data': {
				'text': text,
			}
		}
	# return text, RANK1, title, rate, name, graph, map
	return meta_card
