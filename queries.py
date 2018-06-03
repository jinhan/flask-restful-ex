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
		# each_openrate = sess.query(func.max(OpenProgress.openPercent).label('max')).filter(OpenProgress.datatime<=time).group_by(OpenProgress.cityCode).subquery()
		# openrate_avg_nat = sess.query(func.avg(each_openrate.c.max)).scalar()

		sub = sess.query(func.max(OpenProgress.tooTotal).label('tooTotal'), func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid')).filter(OpenProgress.datatime<=time).group_by(OpenProgress.townCode).subquery()
		tooTotal, n_total, invalid = sess.query(func.sum(sub.c.tooTotal), func.sum(sub.c.n_total), func.sum(sub.c.invalid)).first()
		
		openrate_avg_nat = (n_total + invalid) / tooTotal * 100

		data = {
			'hour': hourConverter(time.hour),
			'openrate_avg_nat': round(openrate_avg_nat, 2),
		}
		text = text_templates[card_seq].format(**data)

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
		if len(openrate_sunname1_ranks):
			openDf = pd.DataFrame(openrate_sunname1_ranks)
			# print(openDf)
			if len(openDf.loc[openDf['max']==100,'sido']):
				open_finished = ', '.join(openDf.loc[openDf['max']==100,'sido'])
				try:
					openrate_sunname1_rank1 = openDf.loc[openDf['max']!=100,].iloc[0]
				except IndexError:
					raise NoTextError
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
		else:
			raise NoTextError

		# print(openrate_sunname1_ranks)
		map_data = []
		for v, r in openrate_sunname1_ranks:
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

	elif card_seq is 9:
		openrate_sunname2_ranks = sess.query(func.max(OpenProgress4.openPercent).label('max'),  OpenProgress4.gusigun).filter(OpenProgress4.datatime<=time).group_by(OpenProgress4.sggCityCode).order_by(func.max(OpenProgress4.openPercent).desc()).all()
		# sggCityCode 매치 안됨, OpenProgress, PrecinctCode
		# 시군구청장 선거 group by 뭘로
		# print(openrate_sunname2_ranks)

		openDf = pd.DataFrame(openrate_sunname2_ranks)
		if len(openrate_sunname2_ranks):
			if len(openDf.loc[openDf['max']==100,'gusigun']):
				open_finished = ', '.join(openDf.loc[openDf['max']==100,'gusigun'])
				try:
					openrate_sunname2_rank1 = openDf.loc[openDf['max']!=100,].iloc[0]
				except IndexError:
					raise NoTextError
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
		else:
			raise NoTextError

		graph_data = []
		for v, r in openrate_sunname2_ranks:
			graph_data.append({'name':r, 'value':float(v)*0.01})
		# print(map_data)

		meta_card = {
			'order': order,
			'type': 'graph',
			'party': 'default',
			'data': {
				'graph_data': {
					'type': 'region',
					'data': graph_data,
				},
				'text': text,
			}
		}

	elif card_seq is 10:
		region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.sggCityCode==regions[index]).first()

		# each_openrate = sess.query(func.max(OpenProgress.openPercent).label('max'), OpenProgress.sido.label('name')).filter(OpenProgress.datatime<=time).group_by(OpenProgress.cityCode).subquery()

		# openrate_region1 = sess.query(each_openrate.c.max).filter(each_openrate.c.name==region1).scalar()

		sub_r = sess.query(OpenProgress.gusigun,func.max(OpenProgress.tooTotal).label('tooTotal'), func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid')).filter(OpenProgress.datatime<=time, OpenProgress.sido==region1).group_by(OpenProgress.townCode)
		tooTotal_r, n_total_r, invalid_r = sess.query(func.sum(sub_r.subquery().c.tooTotal), func.sum(sub_r.subquery().c.n_total), func.sum(sub_r.subquery().c.invalid)).first()
		
		openrate_region1 = (n_total_r + invalid_r) / tooTotal_r * 100

		data = {
			'hour': hourConverter(time.hour),
			'region1': region1,
		}
		if openrate_region1 == 0:
			text = text_templates['10-1'].format(**data)
		elif openrate_region1 == 100:
			text = text_templates['10-2'].format(**data)
		else:
			sub = sess.query(func.max(OpenProgress.tooTotal).label('tooTotal'), func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid')).filter(OpenProgress.datatime<=time).group_by(OpenProgress.townCode).subquery()

			tooTotal, n_total, invalid = sess.query(func.sum(sub.c.tooTotal), func.sum(sub.c.n_total), func.sum(sub.c.invalid)).first()

			openrate_avg_nat = (n_total + invalid) / tooTotal * 100

			openrate_region1_openrate_avg_nat = openrate_region1 - openrate_avg_nat
			compare_region1 = '높은' if openrate_region1_openrate_avg_nat > 0 else '낮은'

			data['openrate_region1'] = round(openrate_region1, 2)
			data['openrate_region1_openrate_avg_nat'] = round(abs(openrate_region1_openrate_avg_nat), 2)
			data['compare_region1'] = compare_region1
			
			text = text_templates[card_seq].format(**data)

		# openrate_region1_sub = sess.query(func.max(OpenProgress.openPercent), OpenProgress.sido).filter(OpenProgress.datatime<=time).group_by(OpenProgress.sido).all()

		map_data = []
		for r, tooTotal, n_total, invalid in sub_r.all():
			v = (n_total + invalid) / tooTotal
			map_data.append({'name':r, 'value':v})

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

	elif card_seq is 11:
		poll, poll_num_sunname = sess.query(SgTypecode.sgName, func.count(PrecinctCode.sggCityCode)).join(PrecinctCode, PrecinctCode.electionCode==SgTypecode.sgTypecode).filter(SgTypecode.sgTypecode==polls[index]).first()
		# print(polls[index], poll, poll_num_sunname)

		# poll 종류에 대해 달라져야함, OpenSido / OpenGusigun ...
		# poll 종류에 따라 table을 선택하고, table마다 column name은 같도록
		# Open = openTable(polls[index])
		if polls[index] == 2: # 국회의원
			# each_openrate = sess.query(func.max(OpenProgress2.openPercent).label('max'), OpenProgress2.sgg).filter(OpenProgress2.datatime<=time).group_by(OpenProgress2.sgg).order_by(func.max(OpenProgress2.openPercent).desc()).subquery()
			sub = sess.query(OpenProgress2.sgg, func.max(OpenProgress2.tooTotal).label('tooTotal'), func.max(OpenProgress2.n_total).label('n_total'), func.max(OpenProgress2.invalid).label('invalid')).filter(OpenProgress2.datatime<=time).group_by(OpenProgress2.sgg)
		elif polls[index] == 3:
			# each_openrate = sess.query(func.max(OpenProgress3.openPercent).label('max'), OpenProgress3.sido).filter(OpenProgress3.datatime<=time).group_by(OpenProgress3.sido).order_by(func.max(OpenProgress3.openPercent).desc()).subquery()
			sub = sess.query(OpenProgress3.sido, func.max(OpenProgress3.tooTotal).label('tooTotal'), func.max(OpenProgress3.n_total).label('n_total'), func.max(OpenProgress3.invalid).label('invalid')).filter(OpenProgress3.datatime<=time).group_by(OpenProgress3.sido)
		elif polls[index] == 4:
			# each_openrate = sess.query(func.max(OpenProgress4.openPercent).label('max'), OpenProgress4.gusigun).filter(OpenProgress4.datatime<=time).group_by(OpenProgress4.gusigun).order_by(func.max(OpenProgress4.openPercent).desc()).subquery()
			sub = sess.query(OpenProgress4.gusigun, func.max(OpenProgress4.tooTotal).label('tooTotal'), func.max(OpenProgress4.n_total).label('n_total'), func.max(OpenProgress4.invalid).label('invalid')).filter(OpenProgress4.datatime<=time).group_by(OpenProgress4.townCode)
		elif polls[index] == 11:
			# each_openrate = sess.query(func.max(OpenProgress11.openPercent).label('max'), OpenProgress11.sido).filter(OpenProgress11.datatime<=time).group_by(OpenProgress11.sido).order_by(func.max(OpenProgress11.openPercent).desc()).subquery()
			sub = sess.query(OpenProgress11.sido, func.max(OpenProgress11.tooTotal).label('tooTotal'), func.max(OpenProgress11.n_total).label('n_total'), func.max(OpenProgress11.invalid).label('invalid')).filter(OpenProgress11.datatime<=time).group_by(OpenProgress11.sido)
		else:
			# each_openrate = sess.query(func.max(OpenProgress.openPercent).label('max'), OpenProgress.sido).filter(OpenProgress.datatime<=time).group_by(OpenProgress.sido).order_by(func.max(OpenProgress.openPercent).desc()).subquery()
			sub = sess.query(OpenProgress.sido, func.max(OpenProgress.tooTotal).label('tooTotal'), func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid')).filter(OpenProgress.datatime<=time).group_by(OpenProgress.townCode)
		# print(polls[index])
		tooTotal, n_total, invalid = sess.query(func.sum(sub.subquery().c.tooTotal), func.sum(sub.subquery().c.n_total), func.sum(sub.subquery().c.invalid)).first()

		poll_openrate_ranks = []
		try:
			poll_openrate_nat_avg = (n_total + invalid) / tooTotal * 100
			
			for r, tooTotal, n_total, invalid in sub.all():
				v = (n_total + invalid) / tooTotal
				poll_openrate_ranks.append({'name':r, 'value':v})
			
			poll_openrate_ranks = sorted(poll_openrate_ranks, key=lambda x: x['value'], reverse=True)
			# print(poll_openrate_ranks)

			if poll_openrate_nat_avg == 100:
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

		except TypeError:
			if tooTotal is None:
				data = {
					'hour': hourConverter(time.hour),
					'poll': poll,
					'josa': josaPick(poll, '은'),
				}
				text = text_templates['11-1'].format(**data)
			else:
				raise NoTextError

		meta_card = {
			'order': order,
			'type': 'graph',
			'party': 'default',
			'data': {
				'graph_data': {
					'type': 'region',
					'data': poll_openrate_ranks,
				},
				'text': text,
			}
		}

	elif card_seq is 12:
		candidate, candidate_region, candidate_sdName, candidate_poll_code = sess.query(CandidateInfo.name, CandidateInfo.sggName, CandidateInfo.sdName, CandidateInfo.sgTypecode).filter(CandidateInfo.huboid==candidates[index]).first()
		# sggName에서 regionPoll 

		candidate_poll = regionPoll(candidate_region, candidate_poll_code)
		# print(candidate_region)
		# candidate_poll에 맞게 테이블 선택		
		if candidate_poll_code == 2: # 국회의원
			candidate_poll_openrate = sess.query(func.max(OpenProgress2.openPercent)).filter(OpenProgress2.datatime<=time, OpenProgress2.sgg==candidate_region).scalar()
		
		elif candidate_poll_code == 4:
			candidate_poll_openrate = sess.query(func.max(OpenProgress4.openPercent)).filter(OpenProgress4.datatime<=time, OpenProgress4.gusigun==candidate_region).scalar()

		elif candidate_poll_code == 3:
			candidate_poll_openrate = sess.query(func.max(OpenProgress3.openPercent)).filter(OpenProgress3.datatime<=time,  OpenProgress3.sido==candidate_region).scalar()
			candidate_poll_openrate_sub = sess.query(OpenProgress3.openPercent, OpenProgress3.gusigun).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==candidate_sdName, OpenProgress3.gusigun!='합계').all()

		elif candidate_poll_code == 11:
			candidate_poll_openrate = sess.query(func.max(OpenProgress11.openPercent)).filter(OpenProgress11.datatime<=time, OpenProgress11.sido==candidate_region).scalar()
			candidate_poll_openrate_sub = sess.query(OpenProgress11.openPercent, OpenProgress11.gusigun).filter(OpenProgress11.datatime<=time, OpenProgress11.sido==candidate_sdName, OpenProgress3.gusigun!='합계').all()

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

		if candidate_poll_code in [2,4]:
			meta_card = {
				'order': order,
				'type': 'default',
				'party': 'default',
				'data': {
					'text': text,
				}
			}
		else:
			map_data = []
			for v, r in candidate_poll_openrate_sub:
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

		if text == '':
			raise NoTextError
		else:
			text = text

		meta_card = {
			'order': order,
			'type': 'default',
			'party': 'default',
			'data': {
				'text': text,
			}
		}

	elif card_seq is 14:
		# sub_ranks = sess.query(OpenProgress3).filter(OpenProgress3.datatime<=time).group_by(OpenProgress3.townCode)
		sub_ranks = sess.query(OpenProgress3).filter(OpenProgress3.gusigun=='합계')
		# 실제에서 time 살리기
		ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
		ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)	
		# print(ranks_vote)
		ranks_ttl = []
		for i, ranks in ranks_vote.iterrows():
			ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])
		# 각 group 마다 랭킹 만들기
		# if len(ranks_ttl) > 1:
		ranking = [[]] * len(ranks_ttl[0])
		for idx, ranks in enumerate(ranks_ttl):
			for i, r in enumerate(ranks):
				ranking[i].append({
					'jdName':ranksDf.loc[idx, r+'_jdName'],
					'name': ranksDf.loc[idx, r+'_name'],
					'percent': ranksDf.loc[idx, r+'_percent'],
					})
		
		rank1_count = Counter([r['jdName'] for r in ranking[0]]).most_common()
		rank1_party = rank1_count[0][0]
		rank1_party_num = rank1_count[0][1]
		# else:

		data = {
			'hour': hourConverter(time.hour),
			'rank1_party': rank1_party,
			'josa1': josaPick(rank1_party, '이'),
			'josa2': josaPick(rank1_party, '은'),
			'rank1_party_num': rank1_party_num,
		}
		text = text_templates[card_seq].format(**data)

		meta_card = {
			'order': order,
			'type': 'winner',
			'party': rank1_party,
			'data': {
				'title': hourConverter(time.hour) + ', ' + str(rank1_party_num) + '개 선거구 1위',
				'name': rank1_party,
				'text': text,
			}
		}

	elif card_seq is 15:
		try:
			candidate_poll_code = sess.query(CandidateInfo.sgTypecode).filter(CandidateInfo.huboid==candidates[index]).first()
		except IndexError:
			candidate_poll_code = None

		if len(regions) == 0:
			openrate_rank1_region = None
			if candidate_poll_code is 3 or polls[index] is 3: # 시도지사
				# sub_ranks = sess.query(OpenProgress3).filter(OpenProgress3.datatime<=time).group_by(OpenProgress3.sido)
				sub_ranks = sess.query(OpenProgress3).filter(OpenProgress3.gusigun=='합계')
		
			elif candidate_poll_code is 4 or polls[index] is 4: # 시군구청장
				# sub_ranks = sess.query(OpenProgress4).filter(OpenProgress4.datatime<=time).group_by(OpenProgress4.gusigun)
				sub_ranks = sess.query(OpenProgress4)

			elif candidate_poll_code is 2 or polls[index] is 2: # 국회의원
				# sub_ranks = sess.query(OpenProgress2).filter(OpenProgress2.datatime<=time).group_by(OpenProgress2.sgg)
				sub_ranks = sess.query(OpenProgress2)

			elif candidate_poll_code is 11 or polls[index] is 11: # 교육감
				# openrate_rank1_region = sess.query(OpenProgress11.sido).filter(OpenProgress11.datatime<=time).order_by(OpenProgress11.openPercent.desc()).fisrt()
				openrate_rank1_region = sess.query(OpenProgress11.sido).filter(OpenProgress11.gusigun=='합계').order_by(func.max(OpenProgress11.openPercent).desc()).scalar()
				print(openrate_rank1_region)
				# sub_ranks = sess.query(OpenProgress11).filter(OpenProgress11.datatime<=time, OpenProgress11.sido==openrate_rank1_region).group_by(OpenProgress11.sido)
				sub_ranks = sess.query(OpenProgress11).filter( OpenProgress11.sido==openrate_rank1_region, OpenProgress11.gusigun=='합계')	
		else:
			# text = None
			raise NoTextError	

		ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
		ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)

		ranks_ttl = []
		for i, ranks in ranks_vote.iterrows():
			ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])

		if len(ranks_ttl) > 1:
			ranking = [[]] * len(ranks_ttl[0])
			for idx, ranks in enumerate(ranks_ttl):
				for i, r in enumerate(ranks):
					ranking[i].append({
						'jdName':ranksDf.loc[idx, r+'_jdName'],
						'name': ranksDf.loc[idx, r+'_name'],
						'percent': ranksDf.loc[idx, r+'_percent'],
						})
			rank1_count = Counter([r['jdName'] for r in ranking[0]]).most_common()
			rank1_party = rank1_count[0][0]
			rank1_party_num = rank1_count[0][1]
			ranks_party = ', '.join(r[0] for r in rank1_count[1:])
			openrate_rank1_region_candidate = ranking[0][0]['name']
			openrate_rank2_region_candidate = ranking[0][1]['name']

			data = {
				'hour': hourConverter(time.hour),
				'rank1_party': rank1_party, 
				'josa1': josaPick(rank1_party, '이'),
				'rank1_party_num': rank1_party_num,
				'ranks_party': ranks_party,
				'josa2': josaPick(ranks_party, '이'),
				'openrate_rank1_region': openrate_rank1_region,
				'openrate_rank1_region_candidate': openrate_rank1_region_candidate, 
				'openrate_rank2_region_candidate': openrate_rank2_region_candidate,
			}

		else:
			# ranking = [[]] * len(ranks_ttl[0])
			ranking = []
			for idx, ranks in enumerate(ranks_ttl):
				for i, r in enumerate(ranks):
					ranking.append({
						'jdName':ranksDf.loc[idx, r+'_jdName'],
						'name': ranksDf.loc[idx, r+'_name'],
						'percent': ranksDf.loc[idx, r+'_percent'],
						})
			print(ranking)
			rank1_count = Counter([r['jdName'] for r in ranking]).most_common()
			rank1_party = rank1_count[0][0]
			rank1_party_num = rank1_count[0][1]
			print(rank1_count)
			ranks_party = ', '.join(r[0] for r in rank1_count[1:] if r[0] is not None)
			openrate_rank1_region_candidate = ranking[0]['name']
			openrate_rank2_region_candidate = ranking[1]['name']

			data = {
				'hour': hourConverter(time.hour),
				'rank1_party': rank1_party, 
				'josa1': josaPick(rank1_party, '이'),
				'rank1_party_num': rank1_party_num,
				'ranks_party': ranks_party,
				'josa2': josaPick(ranks_party, '이'),
				'openrate_rank1_region': openrate_rank1_region,
				'openrate_rank1_region_candidate': openrate_rank1_region_candidate, 
				'openrate_rank2_region_candidate': openrate_rank2_region_candidate,
			}

		if candidate_poll_code is 11 or polls[index] is 11:
			text = text_templates['15-11'].format(**data)

			meta_card = {
				'order': order,
				'type': 'winner',
				'party': 'default',
				'data': {
					'title': hourConverter(time.hour) + ', ' + openrate_rank1_region + ' 교육감선거 1위',
					'name': openrate_rank1_region_candidate,
					'text': text,
				}
			}
		else:
			num = candidate_poll_code or polls[index]
			num = '15-' + str(num)
			print(num)
			text = text_templates[num].format(**data)

			meta_card = {
				'order': order,
				'type': 'winner',
				'party': rank1_party,
				'data': {
					'title': hourConverter(time.hour) + ', ' + str(rank1_party_num) + '개 선거구 1위',
					'name': rank1_party,
					'text': text,
				}
			}

	elif card_seq is 16:
		region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.sggCityCode==regions[index]).first()
		
		region1_poll = regionPoll(region1, 3)

		region1_openrate = sess.query(func.max(OpenProgress3.openPercent)).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==region1).scalar()

		# sub_ranks = sess.query(OpenProgress3).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==region1).group_by(OpenProgress3.sido)
		sub_ranks = sess.query(OpenProgress3).filter(OpenProgress3.sido==region1).group_by(OpenProgress3.sido)

		ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
		ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)	

		ranks_ttl = [] # one line
		for i, ranks in ranks_vote.iterrows():
			ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])
		# print(ranks_ttl)
		# ranking = [[]] * len(ranks_ttl[0])
		ranking = []
		for idx, ranks in enumerate(ranks_ttl):
			for i, r in enumerate(ranks):
				ranking.append({
					'jdName':ranksDf.loc[idx, r+'_jdName'],
					'name': ranksDf.loc[idx, r+'_name'],
					'percent': ranksDf.loc[idx, r+'_percent'],
					'vote': ranksDf.loc[idx, r+'_vote'],
				})
		# print(ranking)
		region1_rank1_party = ranking[0]['jdName']
		region1_rank1_name = ranking[0]['name']
		region1_rank1_rate = ranking[0]['percent']

		region1_rank2_party = ranking[1]['jdName']
		region1_rank2_name = ranking[1]['name']
		region1_rank2_rate = ranking[1]['percent']

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

		rank1_cnt = ranking[0]['vote']
		rank2_cnt = ranking[1]['vote']
		yet_cnt = ranksDf.loc[0, 'tooTotal'] - ranksDf.loc[0, 'n_total'] - ranksDf.loc[0, 'invalid']
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

		graph_data = []
		for r in ranking:
			graph_data.append({
				'name': r['name'],
				'party': r['jdName'],
				'value': float(r['percent']) * 0.01,
			})
		# print(graph_data)
		meta_card = {
			'order': order,
			'type': 'graph',
			'party': 'default',
			'data': {
				'graph_data': {
					'type': 'candidate',
					'data': graph_data,
				},
				'text': text,
			}
		}
	
	elif card_seq is 17:
		candidate, candidate_region, sgtype = sess.query(CandidateInfo.name, CandidateInfo.sggName, CandidateInfo.sgTypecode).filter(CandidateInfo.huboid==candidates[index]).first()
		candidate_poll = regionPoll(candidate_region, sgtype)

		# candidate_poll table 선택
		if sgtype is 2: 
			# candidate_poll_openrate = sess.query(func.max(OpenProgress2.openPercent)).filter(OpenProgress2.datatime<=time, OpenProgress2.sgg==candidate_region).scalar()
			# sub_ranks = sess.query(OpenProgress2).filter(OpenProgress2.datatime<=time, OpenProgress2.sgg==candidate_region).group_by(OpenProgress2.sgg)
			candidate_poll_openrate = sess.query(func.max(OpenProgress2.openPercent)).filter(OpenProgress2.sgg==candidate_region).scalar()
			sub_ranks = sess.query(OpenProgress2).filter( OpenProgress2.sgg==candidate_region)
		elif sgtype is 3:
			# candidate_poll_openrate = sess.query(func.max(OpenProgress3.openPercent)).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==candidate_region).scalar()
			# sub_ranks = sess.query(OpenProgress3).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==candidate_region).group_by(OpenProgress3.sido)
			candidate_poll_openrate = sess.query(func.max(OpenProgress3.openPercent)).filter( OpenProgress3.sido==candidate_region, OpenProgress3.gusigun=='합계').scalar()
			sub_ranks = sess.query(OpenProgress3).filter(OpenProgress3.sido==candidate_region, OpenProgress3.gusigun=='합계')
		elif sgtype is 4:
			# candidate_poll_openrate = sess.query(func.max(OpenProgress4.openPercent)).filter(OpenProgress4.datatime<=time, OpenProgress4.gusigun==candidate_region).scalar()
			# sub_ranks = sess.query(OpenProgress4).filter(OpenProgress4.datatime<=time, OpenProgress4.gusigun==candidate_region).group_by(OpenProgress4.gusigun)
			candidate_poll_openrate = sess.query(func.max(OpenProgress4.openPercent)).filter( OpenProgress4.gusigun==candidate_region).scalar()
			sub_ranks = sess.query(OpenProgress4).filter(OpenProgress4.gusigun==candidate_region)
		elif sgtype is 11:
			# candidate_poll_openrate = sess.query(func.max(OpenProgress11.openPercent)).filter(OpenProgress11.datatime<=time,OpenProgress11.sido==candidate_region).scalar()
			# sub_ranks = sess.query(OpenProgress11).filter(OpenProgress11.datatime<=time, OpenProgress11.sido==candidate_region).group_by(OpenProgress11.sido)
			candidate_poll_openrate = sess.query(func.max(OpenProgress11.openPercent)).filter(OpenProgress11.sido==candidate_region, OpenProgress11.gusigun=='합계').scalar()
			sub_ranks = sess.query(OpenProgress11).filter(OpenProgress11.sido==candidate_region, OpenProgress11.gusigun=='합계')

		ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
		ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)
		
		ranks_ttl = []
		for i, ranks in ranks_vote.iterrows():
			ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])

		ranking = []
		for idx, ranks in enumerate(ranks_ttl):
			for i, r in enumerate(ranks):
				ranking.append({
					'jdName':ranksDf.loc[idx, r+'_jdName'],
					'name': ranksDf.loc[idx, r+'_name'],
					'percent': ranksDf.loc[idx, r+'_percent'],
					'vote': ranksDf.loc[idx, r+'_vote'],
				})
		# print(ranking)

		candidate_poll_rank1_party = ranking[0]['jdName']
		candidate_poll_rank1_name = ranking[0]['name']
		candidate_poll_rank1_rate = ranking[0]['percent']

		candidate_poll_rank2_party = ranking[1]['jdName']
		candidate_poll_rank2_name = ranking[1]['name']
		candidate_poll_rank2_rate = ranking[1]['percent']

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

		rank1_cnt = ranking[0]['vote']
		rank2_cnt = ranking[1]['vote']
		yet_cnt = ranksDf.loc[0, 'tooTotal'] - ranksDf.loc[0, 'n_total'] - ranksDf.loc[0, 'invalid']
		confirm = True if (rank1_cnt-rank2_cnt) > yet_cnt else False

		if candidate_poll_rank1_name is candidate: 
			if (candidate_poll_rank1_rate - candidate_poll_rank2_rate) >= 15:
				text = text_templates['17-3'].format(**data)
			elif (candidate_poll_rank1_rate - candidate_poll_rank2_rate) < 5:
				text = text_templates['17-1'].format(**data)
			elif confirm:
				text = text_templates['17-6'].format(**data)
			else:
				text = text_templates[card_seq].format(**data)

		elif candidate_poll_rank2_name is candidate:
			if abs(candidate_poll_rank1_rate - candidate_poll_rank2_rate) >= 15:
				text = text_templates['17-4'].format(**data)
			elif abs(candidate_poll_rank1_rate - candidate_poll_rank2_rate) < 5:
				text = text_templates['17-2'].format(**data)
			elif confirm:
				text = text_templates['17-7'].format(**data)
			else:
				text = text_templates[card_seq].format(**data)

		else:
			if abs(candidate_poll_rank1_rate - candidate_poll_rank2_rate) < 5:
				text = text_templates['17-5'].format(**data)
			else:
				text = text_templates[card_seq].format(**data)
		
		graph_data = []
		for r in ranking:
			graph_data.append({
				'name': r['name'],
				'party': r['jdName'],
				'value': float(r['percent']) * 0.01,
			})
		# print(graph_data)
		meta_card = {
			'order': order,
			'type': 'graph',
			'party': 'default',
			'data': {
				'graph_data': {
					'type': 'candidate',
					'data': graph_data,
				},
				'text': text,
			}
		}
		

	elif card_seq is 18:
		party = sess.query(PartyCode.jdName).filter(PartyCode.pOrder==parties[index]).scalar()
		
		# 시도지사
		# sub_ranks = sess.query(OpenProgress3).filter(OpenProgress3.datatime<=time).group_by(OpenProgress3.sido)
		sub_ranks = sess.query(OpenProgress3).filter(OpenProgress3.gusigun=='합계')
		ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
		ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)

		ranks_ttl = []
		for i, ranks in ranks_vote.iterrows():
			ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])

		ranking = [[]] * len(ranks_ttl[0])
		for idx, ranks in enumerate(ranks_ttl):
			for i, r in enumerate(ranks):
				ranking[i].append({
					'jdName':ranksDf.loc[idx, r+'_jdName'],
					'name': ranksDf.loc[idx, r+'_name'],
					'percent': ranksDf.loc[idx, r+'_percent'],
					'vote': ranksDf.loc[idx, r+'_vote'],
					})
		rank1_count = Counter([r['jdName'] for r in ranking[0]]).most_common()
		
		# 구시군청장
		# sub_ranks_g = sess.query(OpenProgress4).filter(OpenProgress4.datatime<=time).group_by(OpenProgress4.gusigun)
		sub_ranks_g = sess.query(OpenProgress4)
		ranksDf_g = pd.read_sql(sub_ranks_g.statement, sub_ranks_g.session.bind)
		ranks_vote_g = ranksDf_g.filter(regex="n*_percent").dropna(axis=1)
		
		ranks_ttl_g = []
		for i, ranks in ranks_vote_g.iterrows():
			ranks_ttl_g.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])

		ranking_g = [[]] * len(ranks_ttl_g[0])
		for idx, ranks in enumerate(ranks_ttl_g):
			for i, r in enumerate(ranks):
				ranking_g[i].append({
					'jdName':ranksDf.loc[idx, r+'_jdName'],
					'name': ranksDf.loc[idx, r+'_name'],
					'percent': ranksDf.loc[idx, r+'_percent'],
					'vote': ranksDf.loc[idx, r+'_vote'],
					})

		rank1_count_g = Counter([r['jdName'] for r in ranking_g[0]]).most_common()

		# 
		print(rank1_count)
		my_party_rank1_sido_num = [v for r, v in rank1_count if r is party]
		my_party_rank1_gusigun_num = [v for r, v in rank1_count_g if r is party]
		party_rank1_sido_num = rank1_count_g[0][1]
		party_rank1_sido_name = rank1_count_g[0][0]
		party_rank2_sido_num = rank1_count_g[1][1]
		party_rank2_sido_name = rank1_count_g[1][0]
		party_rank3_sido_num = rank1_count_g[2][1]
		party_rank3_sido_name = rank1_count_g[2][0]
		party_rank1_gusigun_num = rank1_count_g[0][1]
		party_rank123_gusigun_name = ', '.join([r[0] for r in rank1_count_g])

		# party_rank1_sido_num_confirm = []
		# party_rank2_sido_num_confirm = 0
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
				
		
		if abs(party_rank1_sido_num - party_rank2_sido_num) / len(rank1_count_g) < 0.05: # 1,2위 경합
			text = text_templates['18-1'].format(**data)

		elif abs(party_rank2_sido_num - party_rank3_sido_num) / len(rank1_count_g) < 0.05: # 2,3위 경합
			text = text_templates['18-2'].format(**data)
		
		elif (abs(party_rank1_sido_num - party_rank2_sido_num) / len(rank1_count_g) < 0.05) and (abs(party_rank2_sido_num - party_rank3_sido_num) / len(rank1_count_g) < 0.05): # 1,2,3위 경합
			text = text_templates['18-3'].format(**data)

		elif (party is party_rank1_sido_name) and (abs(ranking[0][0]['percent'] - ranking[0][1]['percent']) > 15): # 내가 선택한 정당이 1위일때, 1위와 2위의 격차가 15% 이상
			text = text_templates['18-4'].format(**data)
		
		elif (party is party_rank2_sido_name) and (abs(ranking[0][0]['percent'] - ranking[0][1]['percent']) > 15): # 내가 선택한 정당이 2위일때, 1위와 2위의 격차가 15% 이상
			text = text_templates['18-5'].format(**data)

		elif confirms_count[0][0] is party:
			data['party_rank1_sido_num_confirm'] = confirms_count[0][1],
			data['party_rank1_gusigun_num_confirm'] = [v for r, v in confirms_count_g if r is party][0],
			text = text_templates['18-6'].format(**data)

		elif confirms_count[1][0] is party:
			data['party_rank1_sido_num_confirm'] = confirms_count[1][1],
			data['party_rank1_gusigun_num_confirm'] = [v for r, v in confirms_count_g if r is party][0],
			text = text_templates['18-7'].format(**data)
		
		else:
			text = text_templates[card_seq].format(**data)

		meta_card = {
			'order': order,
			'type': 'default',
			'party': 'default',
			'data': {
				'text': text,
			}
		}

	elif card_seq is 19:
		index=0
		if polls[index] == 2:
			sub = sess.query(OpenProgress2) # time 추가

		elif polls[index] is 3:
			sub = sess.query(OpenProgress3).filter(OpenProgress3.gusigun=='합계')
		
		elif polls[index] is 4:
			sub = sess.query(OpenProgress4)
		
		elif polls[index] is 11:
			sub = sess.query(OpenProgress11).filter(OpenProgress11.gusigun=='합계')
		# else:
		# 	sub = sess.query(OpenProgress).group_by(OpenProgress.sido)


		if polls[index] in [2,3,4]:
			ranksDf = pd.read_sql(sub.statement, sub.session.bind)
			ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)

			ranks_ttl = [] # 각 지역 - 순위
			for i, ranks in ranks_vote.iterrows():
				ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])
			# if len(ranks_ttl) > 1:
			# 	ranking = [[]] * len(ranks_ttl)
			# 	print()
			# 	for idx, ranks in enumerate(ranks_ttl): # 지역에서
			# 		for i, r in enumerate(ranks): # 1,2,3 등을
			# 			print(idx, r)
			# 			ranking[idx].append({ 
			# 				'jdName':ranksDf.loc[idx, r+'_jdName'],
			# 				'name': ranksDf.loc[idx, r+'_name'],
			# 				'percent': ranksDf.loc[idx, r+'_percent'],
			# 				'vote': ranksDf.loc[idx, r+'_vote'],
			# 				}) # 등수별로 모아준다.
			# 	rank1_count = Counter([r['jdName'] for r in ranking[0]]).most_common() # 1등중에서 가장 많이 나온 정당을 찾음
			# else: 
			ranking = []
			for idx, ranks in enumerate(ranks_ttl):
				for i, r in enumerate(ranks):
					ranking.append({
						'idx': idx,
						'rank': i,
						'jdName':ranksDf.loc[idx, r+'_jdName'],
						'name': ranksDf.loc[idx, r+'_name'],
						'percent': ranksDf.loc[idx, r+'_percent'],
						'vote': ranksDf.loc[idx, r+'_vote'],
						})
			rank1_count = Counter([r['jdName'] for r in ranking if r['rank']==0]).most_common()
			print(rank1_count)
			rank1_party = rank1_count[0][0] # (key, count)
			rank1_party_num = rank1_count[0][1]
			rank2_party = rank1_count[1][0]
			rank2_party_num = rank1_count[1][1]

			confirms = []
			for idx, rank in enumerate(ranks_ttl):
				rank1_cnt = ranksDf.loc[idx, rank[0]+'_vote']
				rank2_cnt = ranksDf.loc[idx, rank[1]+'_vote']
				yet_cnt = ranksDf.loc[idx, 'tooTotal'] - ranksDf.loc[idx, 'n_total'] - ranksDf.loc[idx, 'invalid']
				confirm = 1 if (rank1_cnt-rank2_cnt) > yet_cnt else 0
				if confirm:
					confirms.append(ranksDf.loc[idx, rank[0]+'_jdName'])
			confirms_count = Counter(confirms).most_common()
			print(confirms_count)
			confirms_rank1_party = confirms_count[0][0]
			confirms_rank1_party_num = confirms_count[0][1]
			try:
				confirms_rank2_party = confirms_count[1][0]
				confirms_rank2_party_num = confirms_count[1][1]
				chair_name = '의석을' if polls[index] == 2 else '자리를'

				confirms_rank2 = confirms_rank2_party + josaPick(confirms_rank2_party, '가') + ' ' + str(confirms_rank2_party_num) + '개의 ' + chair_name + ' 가져가는데 그쳤다.'
			except IndexError:
				confirms_rank2 = ''

			data = {
				'hour': hourConverter(time.hour),
				'rank1_party': rank1_party,
				'josa1': josaPick(rank1_party, '은'),
				'rank1_party_num': rank1_party_num,
				'rank2_party': rank2_party,
				'josa2': josaPick(rank2_party, '가'),
				'rank2_party_num': rank2_party_num,
				'confirms_rank1_party': confirms_rank1_party,
				'josa3': josaPick(confirms_rank1_party, '은'),
				'confirms_rank1_party_num': confirms_rank1_party_num,
				'confirms_rank2': confirms_rank2,
				# 'confirms_rank2_party': confirms_rank2_party,
				# 'josa4': josaPick(confirms_rank2_party, '가'),			
				# 'confirms_rank2_party_num': confirms_rank2_party_num,
			}
		else: # 11 type
			ranksDf = pd.read_sql(sub.statement, sub.session.bind)
			ranksDf = ranksDf.sort_values(by='openPercent', ascending=False)
			# ranksDf_1 = ranksDf.loc[0,:]
			# ranksDf_2 = ranksDf.loc[1,:]
			ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)

			ranks_ttl = []
			for i, ranks in ranks_vote.iterrows(): # 가로 등수, 세로 지역수: 지역끼리
				ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])
			
			# if len(ranks_ttl) > 1:
			# 	ranking = [[]] * len(ranks_ttl[0])
			# 	for idx, ranks in enumerate(ranks_ttl): # 지역에서
			# 		for i, r in enumerate(ranks): # 1,2,3 등을
			# 			ranking[i].append({ 
			# 				'sido':ranksDf.loc[idx, r+'_sido'],
			# 				'name': ranksDf.loc[idx, r+'_name'],
			# 				# 'percent': ranksDf.loc[idx, r+'_percent'],
			# 				# 'vote': ranksDf.loc[idx, r+'_vote'],
			# 				}) # 등수별로 모아준다.
			# 	# rank1_count = Counter([r['openPercent'] for r in ranking[0]]).most_common() # 1등중에서 가장 많이 나온 정당을 찾음
			# 	open_rank1_region = ranking[0][0]['sido'] 
			# 	open_rank1_region_candidate = ranking[0][0]['name']
			# 	open_rank2_region = ranking[0][1]['sido']
			# 	open_rank2_region_candidate = ranking[0][1]['name']
			# else:
			ranking = []
			for idx, ranks in enumerate(ranks_ttl):
				for i, r in enumerate(ranks):
					ranking.append({
						'idx': idx,
						'rank': i,
						'sido':ranksDf.loc[idx, 'sido'],
						'name': ranksDf.loc[idx, r+'_name'],
						# 'percent': ranksDf.loc[idx, r+'_percent'],
						# 'vote': ranksDf.loc[idx, r+'_vote'],
						})
			# rank1_count = Counter([r['openPercent'] for r in ranking).most_common()

			open_rank1_region = [r['sido'] for r in ranking if r['idx'] == 0][0] 
			open_rank1_region_candidate = [r['name'] for r in ranking if (r['idx'] == 0) and (r['rank']==0)][0]
			try:
				open_rank2_region = [r['sido'] for r in ranking if r['idx'] == 1][0] 
				open_rank2_region_candidate = [r['name'] for r in ranking if (r['idx'] == 1) and (r['rank']==0)][0] 
				open_rank2 = '그 다음으로 개표가 빠른 지역은 ' + open_rank2_region + '로, 이 지역에서는 ' + open_rank2_region_candidate + ' 후보가 1위로 앞서 나가고 있다.'
			except IndexError:
				open_rank2 = ''
			
			# ranking = []
			# for idx, ranks in enumerate(ranks_ttl):
			# 	for i, r in enumerate(ranks):
			# 		ranking.append({
			# 			'idx': idx,
			# 			'rank': i,
			# 			'jdName':ranksDf.loc[idx, r+'_jdName'],
			# 			'name': ranksDf.loc[idx, r+'_name'],
			# 			'percent': ranksDf.loc[idx, r+'_percent'],
			# 			'vote': ranksDf.loc[idx, r+'_vote'],
			# 			})
			# rank1_count = Counter([r['jdName'] for r in ranking if r['rank']==0]).most_common()
			

			confirms = []
			for idx, ranks in enumerate(ranks_ttl):#같은지역에서
				rank1_cnt = ranksDf.loc[idx, ranks[0]+'_vote'] # 1위
				rank2_cnt = ranksDf.loc[idx, ranks[1]+'_vote'] # 2위
				yet_cnt = ranksDf.loc[idx, 'tooTotal'] - ranksDf.loc[idx, 'n_total'] - ranksDf.loc[idx, 'invalid']
				confirm = 1 if (rank1_cnt-rank2_cnt) > yet_cnt else 0
				if confirm:
					confirms.append({'sido': ranks[0]['sido'], 'name': ranks[0]['name']})
			if len(confirms) > 0:
				confirms_open_rank1_region = confirms[0]['sido']
				confirms_open_rank1_region_candidate = confirms[0]['name']
				try:
					out = []
					for c in confirms[1:]:
						out.append(c['sido'] + ' ' + c['name'] + ' 후보')
					confirms_open_ranks = '그 외' + ', '.join(out) + ' 역시 당선이 확정되었다.'
				except IndexError:
					confirms_open_ranks = ''
			else:
				confirms_open_rank1_region = ''
				confirms_open_rank1_region_candidate = ''
				confirms_open_ranks = ''

			data = {
				'hour': hourConverter(time.hour),
				'open_rank1_region': open_rank1_region,
				'open_rank1_region_candidate': open_rank1_region_candidate,
				# 'open_rank2_region': open_rank2_region,
				# 'open_rank2_region_candidate': open_rank2_region_candidate,
				'open_rank2': open_rank2,
				'confirms_open_rank1_region': confirms_open_rank1_region, 
				'confirms_open_rank1_region_candidate': confirms_open_rank1_region_candidate,
				'confirms_open_ranks': confirms_open_ranks,
			}	
			
		print("index:    ", index)
		if polls[index] is 2:
			if (abs(rank1_party_num-rank2_party_num) / len(ranking) < 0.05):
				text = text_templates['19-4'].format(**data)
			elif (abs(rank1_party_num-rank2_party_num) / len(ranking) > 0.15):
				text = text_templates['19-7'].format(**data)
			elif (confirms_rank1_party_num + confirms_rank2_party_num) > 2:
				text = text_templates['19-14'].format(**data)
			else:
				text = text_templates[card_seq].format(**data)
			
		elif polls[index] is 3:
			if (abs(rank1_party_num-rank2_party_num) / len(ranking) < 0.05):
				text = text_templates['19-5'].format(**data)
			elif (abs(rank1_party_num-rank2_party_num) / len(ranking) > 0.15):
				text = text_templates['19-8'].format(**data)
			elif (confirms_rank1_party_num + confirms_rank2_party_num) > 2:
				text = text_templates['19-15'].format(**data)
			else:
				text = text_templates['19-1'].format(**data)
		
		elif polls[index] is 4:
			if (abs(rank1_party_num-rank2_party_num) / len(ranking) < 0.05):
				text = text_templates['19-6'].format(**data)
			elif (abs(rank1_party_num-rank2_party_num) / len(ranking) > 0.15):
				text = text_templates['19-9'].format(**data)
			elif (confirms_rank1_party_num + confirms_rank2_party_num) > 2:
				text = text_templates['19-16'].format(**data)
			else:
				text = text_templates['19-2'].format(**data)
		
		elif polls[index] is 11:
			if len(confirms) > 2:
				text = text_templates['19-17'].format(**data)
			else:
				text = text_templates['19-3'].format(**data)
		
		meta_card = {
			'order': order,
			'type': 'default',
			'party': 'default',
			'data': {
				'text': text,
			}
		}

	elif card_seq is 20:
		meta_card = {
			'order': order,
			'type': 'default',
			'party': 'default',
			'data': {
				'text': 20,
			}
		}

	elif card_seq is 21:
		text = text_templates[card_seq].format(hour=hourConverter(time.hour))
		meta_card = {
			'order': order,
			'type': 'default',
			'party': 'default',
			'data': {
				'text': text,
			}
		}

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
		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t = 23
		else:
			t = time.hour

		if t > 18:
			num = '23-' + str(randint(0,4))
		else: 
			num = '23-' + str(randint(0,3))
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
