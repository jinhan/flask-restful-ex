from templates import text_templates
from orm import *
from sqlalchemy.sql import func, and_
from graph import generateMap, generateGraph
import pandas as pd
from timeit import default_timer as timer
import tossi
from collections import Counter
import numpy as np
from decimal import *
import datetime
from random import randint, choice

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
	if code == 3:
		if r.endswith('시'):
			poll = '시장'
		elif r.endswith('도'):
			poll = '도지사'
	elif code == 4:
		if r.endswith('구'):
			poll = '구청장'
		elif r.endswith('군'):
			poll = '군수'
		elif r.endswith('시'):
			poll = '시장'
	elif code == 2:
		poll = '국회의원'
	elif code == 11:
		poll = '교육감'
	else:
		poll = None
	return poll


def query_card_data(order, index, polls, regions, parties, candidates, time, card_seq, seqs_type):
	if card_seq == 1:
		if (len(candidates) > 0):
			card_num = '1'
			# **해당 변수가 2개 선택됐을 경우 먼저 선택한 변수를 출력, {투표율|득표율}에서는 해당 후보가 참여한 선거의 개표율이 10% 이하일 경우 투표율, 이상일 경우 득표율 출력
			candidate_names = sess.query(CandidateInfo.name).filter(CandidateInfo.huboid.in_(candidates)).all()
			candidate_names = ', '.join([r[0] for r in candidate_names])
			data = {
				'candidate_names': candidate_names,
				'tooOrget': '득표율' if seqs_type else '투표율',
			}
			text = '당신이 선택한 {candidate_names} 후보가 참여한 선거의 {tooOrget} 현황'.format(**data)
		
		else:
			if len(regions) > 0:
				card_num = '1-1'
				# **해당 변수가 2개 선택됐을 경우 먼저 선택한 변수를 출력 {투표율|득표율}에서는 해당 지역 시도지사 선거의 개표율이 10% 이하일 경우 투표율, 이상일 경우 득표율 출력
				region_names = sess.query(PrecinctCode.sido).filter(PrecinctCode.townCode.in_(regions)).all()
				region_names = list(set(region_names))
				region_names = ', '.join([r[0] for r in region_names])
				data = {
					'region_names': region_names,
					'tooOrget': '득표율' if seqs_type else '투표율',
				}
				text = '{region_names} 지역 선거 {tooOrget} 현황'.format(**data)
				# TODO: region_name 출략 안됨 : 테스트 
			else:
				if len(parties) > 0:
					card_num = '1-2'
					# **해당 변수가 2개 선택됐을 경우 먼저 선택한 변수를 출력 {투표율|득표율}에서는 전체 시도지사 선거(17개), 시군구청장 선거(226개)에서 개표율이 10%가 넘는 지역의 수가 전체 선거구의 10%보다 적을 경우(2개, 23개) 투표율, 이상일 경우 득표율 출력
					party_names = sess.query(PartyCode.jdName).filter(PartyCode.pOrder.in_(parties)).all()
					party_names = ', '.join([r[0] for r in party_names])
					data = {
						'party_names': party_names,
						'tooOrget': '득표율' if seqs_type else '투표율',
					}
					text = '618 지방선거 {party_names} {tooOrget} 현황'.format(**data)
				
				else:
					if len(polls) > 0:
						card_num = '1-3'
						# **해당 변수가 2개 선택됐을 경우 먼저 선택한 변수를 출력 {투표율|득표율}에서는 선택한 선거 종류(시도지사/시군구청장/교육감/국회의원)별 전체 선거구 수의 10% 이상이 개표율 10%를 넘겼을 경우 득표율, 이하일 경우 투표율 출력
						poll_names = sess.query(SgTypecode.sgName).filter(SgTypecode.sgTypecode.in_(polls)).all()
						poll_names = ', '.join([r[0] for r in poll_names])
						data = {
							'poll_names': poll_names,
							'tooOrget': '득표율' if seqs_type else '투표율',
						}
						text = '현재 {poll_names} {tooOrget} 현황'.format(**data)
					
					else:
						raise NoTextError

		meta_card = {
			'order': order,
			'type': 'cover',
			'party': 'default',
			'data': {
				'title': text, 
				'text': ''
			},
			'debugging': card_num,
		}

	elif card_seq == 2:
		# each_toorate = sess.query(func.max(VoteProgress.tooRate).label('max')).filter(VoteProgress.timeslot<=time.hour).group_by(VoteProgress.sido).subquery()
		# toorate_avg_nat = sess.query(func.avg(each_toorate.c.max)).scalar()
		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t = 23
		else:
			t = time.hour

		each_toorate = sess.query(func.max(VoteProgress.yooToday).label('yooToday'), func.max(VoteProgress.yooEarly).label('yooEarly'), func.max(VoteProgress.tooToday).label('tooToday'), func.max(VoteProgress.tooEarly).label('tooEarly')).filter(VoteProgress.timeslot<=t, VoteProgress.gusigun=='합계').group_by(VoteProgress.sido).subquery()

		yooToday, yooEarly, tooToday, tooEarly = sess.query(func.sum(each_toorate.c.yooToday), func.sum(each_toorate.c.yooEarly), func.sum(each_toorate.c.tooToday), func.sum(each_toorate.c.tooEarly)).first()
		if tooEarly == None:
			tooEarly = 0
		toorate_avg_nat = (tooToday+tooEarly) / (yooToday+yooEarly) * 100

		data = {
			'toorate_avg_nat': round(toorate_avg_nat, 2),
		}
		if t > 18:
			card_num = '2'
			text = text_templates[card_num].format(**data)
			title = '최종 투표율'
		else:
			card_num = '2-1'
			data['hour'] = hourConverter(time.hour)
			text = text_templates[card_num].format(**data)
			title = hourConverter(time.hour) + ', 현재 투표율'

		meta_card = {
			'order': order,
			'type': 'rate',
			'party': 'default',
			'data': {
				'title': title,
				'rate': round(toorate_avg_nat),
				'text': text,
			},
			'debugging': card_num,

		}

	elif card_seq == 3:
		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t = 23
		else:
			t = time.hour
		# past = sess.query(func.max(PastVoteProgress.tooRate).label('max')).filter(PastVoteProgress.timeslot <= time.hour).group_by(PastVoteProgress.sido).subquery()
		# past_toorate = sess.query(func.avg(past.c.max)).scalar()
		each_toorate_p = sess.query(func.max(PastVoteProgress.yooToday).label('yooToday'), func.max(PastVoteProgress.yooEarly).label('yooEarly'), func.max(PastVoteProgress.tooToday).label('tooToday'), func.max(PastVoteProgress.tooEarly).label('tooEarly')).filter(PastVoteProgress.timeslot<=t, PastVoteProgress.gusigun=='합계').group_by(PastVoteProgress.sido).subquery()
		yooToday_p, yooEarly_p, tooToday_p, tooEarly_p = sess.query(func.sum(each_toorate_p.c.yooToday), func.sum(each_toorate_p.c.yooEarly), func.sum(each_toorate_p.c.tooToday), func.sum(each_toorate_p.c.tooEarly)).first()
		if tooEarly_p == None:
			tooEarly_p = 0
		past_toorate = (tooToday_p+tooEarly_p) / (yooToday_p+yooEarly_p) * 100

		# current = sess.query(func.max(VoteProgress.tooRate).label('max')).filter(VoteProgress.timeslot <= time.hour).group_by(VoteProgress.sido).subquery()
		# current_toorate = sess.query(func.avg(current.c.max)).scalar()
		each_toorate = sess.query(func.max(VoteProgress.yooToday).label('yooToday'), func.max(VoteProgress.yooEarly).label('yooEarly'), func.max(VoteProgress.tooToday).label('tooToday'), func.max(VoteProgress.tooEarly).label('tooEarly')).filter(VoteProgress.timeslot<=t, VoteProgress.gusigun=='합계').group_by(VoteProgress.sido).subquery()
		yooToday, yooEarly, tooToday, tooEarly = sess.query(func.sum(each_toorate.c.yooToday), func.sum(each_toorate.c.yooEarly), func.sum(each_toorate.c.tooToday), func.sum(each_toorate.c.tooEarly)).first()
		if tooEarly == None:
			tooEarly = 0
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
			card_num = '3'
			text = text_templates[card_num].format(**data)
		else:
			card_num = '3-1'
			text = text_templates[card_num].format(**data)

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
			},
			'debugging': card_num,
		}

	elif card_seq == 4:
		try:
			region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.townCode==regions[index]).first()
		except TypeError:
			raise NoTextError
		# print(region1, region2)
		if region2 == '합계':
			# region2 = None
			raise NoTextError

		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t = 23
		else:
			t = time.hour

		# 서울, 서울
		# TODO: NoTextError되는 이유 찾기: 해결
		# region1이 아니라 region2로 수정해야함 0607
		toorate_region1 = sess.query(func.max(VoteProgress.tooRate)).filter(VoteProgress.timeslot<=t, VoteProgress.gusigun==region2).scalar()
	
		if toorate_region1 == None: # toorate_region1 없으면
			raise NoTextError
			
		each_toorate = sess.query(func.max(VoteProgress.yooToday).label('yooToday'), func.max(VoteProgress.yooEarly).label('yooEarly'), func.max(VoteProgress.tooToday).label('tooToday'), func.max(VoteProgress.tooEarly).label('tooEarly')).filter(VoteProgress.timeslot<=t, VoteProgress.gusigun=='합계').group_by(VoteProgress.sido).subquery()
		yooToday, yooEarly, tooToday, tooEarly = sess.query(func.sum(each_toorate.c.yooToday), func.sum(each_toorate.c.yooEarly), func.sum(each_toorate.c.tooToday), func.sum(each_toorate.c.tooEarly)).first()
		if tooEarly == None:
			tooEarly = 0
		toorate_avg_nat = (tooToday+tooEarly) / (yooToday+yooEarly) * 100

		toorate_region1_toorate_avg_nat = toorate_region1 - toorate_avg_nat

		toorate_compare1 = '높은' if toorate_region1_toorate_avg_nat > 0 else '낮은'

		data = {
			'region1': region2,
			'toorate_region1': round(toorate_region1, 2),
			'toorate_region1_toorate_avg_nat': round(abs(toorate_region1_toorate_avg_nat),2),
			'toorate_compare1': toorate_compare1,
		}

		if t > 18:
			card_num = '4'
			text = text_templates[card_num].format(**data)
		else:
			card_num = '4-1'
			text = text_templates[card_num].format(**data)

		toorate_region1_sub = sess.query(func.max(VoteProgress.tooRate), VoteProgress.gusigun).filter(VoteProgress.timeslot<=t, VoteProgress.sido==region1, VoteProgress.gusigun!='합계').group_by(VoteProgress.gusigun).order_by(func.max(VoteProgress.tooRate).desc()).all()
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
			},
			'debugging': card_num,
		}

	elif card_seq == 5:
		candidate, candidate_region, candidate_sdName = sess.query(CandidateInfo.name, CandidateInfo.sggName, CandidateInfo.sdName).filter(CandidateInfo.huboid==candidates[index]).first()

		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t = 23
		else:
			t = time.hour

		candidate_region_toorate = sess.query(func.max(VoteProgress.tooRate)).filter(VoteProgress.timeslot<=t, VoteProgress.sido==candidate_sdName, VoteProgress.gusigun=='합계').scalar()
		# VoteProgress에 sggName 필요함

		data = {
			'candidate': candidate,
			'candidate_region': candidate_region,
			'candidate_region_toorate': candidate_region_toorate,
		}
		if t > 18:
			card_num = '5'
			text = text_templates[card_num].format(**data)
		else:
			card_num = '5-1'
			data['hour'] = hourConverter(time.hour)
			text = text_templates[card_num].format(**data)

		candidate_region_sub = sess.query(VoteProgress.tooRate, VoteProgress.gusigun).filter(VoteProgress.timeslot<=t, VoteProgress.sido==candidate_sdName, VoteProgress.gusigun!='합계').group_by(VoteProgress.gusigun).all()
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
			},
			'debugging': card_num,
		}
		

	elif card_seq == 6:
		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t = 23
		else:
			t = time.hour

		each_toorate_p = sess.query(PastVoteProgress.sido, func.max(PastVoteProgress.yooToday).label('yooToday'), func.max(PastVoteProgress.yooEarly).label('yooEarly'), func.max(PastVoteProgress.tooToday).label('tooToday'), func.max(PastVoteProgress.tooEarly).label('tooEarly')).filter(PastVoteProgress.timeslot<=t, PastVoteProgress.gusigun=='합계').group_by(PastVoteProgress.sido)

		yooToday_p, yooEarly_p, tooToday_p, tooEarly_p = sess.query(func.sum(each_toorate_p.subquery().c.yooToday), func.sum(each_toorate_p.subquery().c.yooEarly), func.sum(each_toorate_p.subquery().c.tooToday), func.sum(each_toorate_p.subquery().c.tooEarly)).first()
		if tooEarly_p == None:
			tooEarly_p = 0
		past_toorate = (tooToday_p+tooEarly_p) / (yooToday_p+yooEarly_p) * 100

		each_toorate = sess.query(VoteProgress.sido, func.max(VoteProgress.yooToday).label('yooToday'), func.max(VoteProgress.yooEarly).label('yooEarly'), func.max(VoteProgress.tooToday).label('tooToday'), func.max(VoteProgress.tooEarly).label('tooEarly')).filter(VoteProgress.timeslot<=t, VoteProgress.gusigun=='합계').group_by(VoteProgress.sido)
		
		yooToday, yooEarly, tooToday, tooEarly = sess.query(func.sum(each_toorate.subquery().c.yooToday), func.sum(each_toorate.subquery().c.yooEarly), func.sum(each_toorate.subquery().c.tooToday), func.sum(each_toorate.subquery().c.tooEarly)).first()
		if tooEarly == None:
			tooEarly = 0
		current_toorate = (tooToday+tooEarly) / (yooToday+yooEarly) * 100

		current_toorate_past_toorate = current_toorate - past_toorate

		past = sess.query(PastVoteProgress.sido, func.max(PastVoteProgress.tooRate).label('max')).filter(PastVoteProgress.timeslot <= t, PastVoteProgress.gusigun=='합계').group_by(PastVoteProgress.sido)
		current = sess.query(VoteProgress.sido, func.max(VoteProgress.tooRate).label('max')).filter(VoteProgress.timeslot <= t).group_by(VoteProgress.sido)
		currentDf = pd.DataFrame(current.all())
		pastDf = pd.DataFrame(past.all())
		currentPastDf = pd.merge(currentDf, pastDf, on='sido')
		# print(currentPastDf['max_x'] - currentPastDf['max_y'])
		if t > 18:
			card_num = '6' if current_toorate_past_toorate > 0 else text_templates['6-0']
			text = text_templates[card_num]
		else:
			# print(current.all())
			# print(past.all())
			# ratio = sum([1 for s in np.subtract(current.all(), past.all()) if s > 0]) / len(current.all())
			ratio = sum([1 for s in (currentPastDf['max_x'] - currentPastDf['max_y']).values if s > 0]) / len(currentDf['sido'])
			# print(ratio)
			if current_toorate_past_toorate >= 5:
				card_num = '6-1'
				text = text_templates[card_num]
			elif ratio >= 0.8:
				card_num = '6-2'
				text = text_templates[card_num]
			else:
				# text = None
				raise NoTextError
				
		meta_card = {
			'order': order,
			'type': 'text',
			'party': 'default',
			'data': {
				'text': text,
			},
			'debugging': card_num,
		}

	elif card_seq == 7:
		subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.townCode).filter(OpenProgress.datatime<=time, OpenProgress.gusigun!='합계', OpenProgress.electionCode==3).subquery()

		tooTotal, n_total, invalid = sess.query(func.sum(OpenProgress.tooTotal), func.sum(OpenProgress.n_total), func.sum(OpenProgress.invalid)).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxtime)).first()
		
		if invalid == None:
			invalid = 0
		openrate_avg_nat = (n_total + invalid) / tooTotal * 100

		data = {
			'hour': hourConverter(time.hour),
			'openrate_avg_nat': round(openrate_avg_nat, 2),
		}
		card_num = '7'
		text = text_templates[card_num].format(**data)

		meta_card = {
			'order': order,
			'type': 'rate',
			'party': 'default',
			'data': {
				'title': hourConverter(time.hour) + ', 평균 개표율',
				'rate': round(openrate_avg_nat),
				'text': text,
			},
			'debugging': card_num,
		}

	elif card_seq == 8:
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
				card_num = '8-1'
				text = text_templates[card_num].format(**data)
			else:
				data = {
					'hour': hourConverter(time.hour),
					'openrate_sunname1_rank1': openrate_sunname1_ranks[0][1],
					'josa': josaPick(openrate_sunname1_ranks[0][1],'으로'),
					'openrate_sunname1_rank1_rate': round(openrate_sunname1_ranks[0][0], 2),
					'openrate_sunname1_rank2': openrate_sunname1_ranks[1][1],
					'openrate_sunname1_rank2_rate': round(openrate_sunname1_ranks[1][0], 2),
				}
				card_num = '8'
				text = text_templates[card_num].format(**data)
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
			},
			'debugging': card_num,
		}

	elif card_seq == 9:
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
				card_num = '9-1'
				text = text_templates[card_num].format(**data)
			else:
				data = {
					'hour': hourConverter(time.hour),
					'openrate_sunname2_rank1': openrate_sunname2_ranks[0][1],
					'openrate_sunname2_rank1_rate': round(openrate_sunname2_ranks[0][0], 2),
					'openrate_sunname2_rank2': openrate_sunname2_ranks[1][1],
					'openrate_sunname2_rank2_rate': round(openrate_sunname2_ranks[1][0], 2),
				}
				card_num = '9'
				text = text_templates[card_num].format(**data)
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
			},
			'debugging': card_num,
		}

	elif card_seq == 10:
		try:
			region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.townCode==regions[index]).first()
		except TypeError:
			raise NoTextError
		if region2 == '합계':
			region2 = None

		# each_openrate = sess.query(func.max(OpenProgress.openPercent).label('max'), OpenProgress.sido.label('name')).filter(OpenProgress.datatime<=time).group_by(OpenProgress.cityCode).subquery()

		# openrate_region1 = sess.query(each_openrate.c.max).filter(each_openrate.c.name==region1).scalar()

		# sub_r = sess.query(OpenProgress.gusigun,func.max(OpenProgress.tooTotal).label('tooTotal'), func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid')).filter(OpenProgress.datatime<=time, OpenProgress.sido==region1).group_by(OpenProgress.townCode)
		# tooTotal_r, n_total_r, invalid_r = sess.query(func.sum(sub_r.subquery().c.tooTotal), func.sum(sub_r.subquery().c.n_total), func.sum(sub_r.subquery().c.invalid)).first()

		subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.townCode).filter(OpenProgress.datatime<=time, OpenProgress.gusigun!='합계', OpenProgress.electionCode==3, OpenProgress.sido==region1).subquery()

		sub_r = sess.query(OpenProgress.gusigun, OpenProgress.tooTotal, OpenProgress.n_total, OpenProgress.invalid).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxtime))

		tooTotal_r, n_total_r, invalid_r = sess.query(func.sum(OpenProgress.tooTotal), func.sum(OpenProgress.n_total), func.sum(OpenProgress.invalid)).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxtime)).first()
		
		if invalid_r == None:
			invalid_r = 0
		try:
			openrate_region1 = (n_total_r + invalid_r) / tooTotal_r * 100
		except TypeError:
			openrate_region1 = 0

		data = {
			'hour': hourConverter(time.hour),
			'region1': region1,
		}
		if openrate_region1 == 0:
			card_num = '10-1'
			text = text_templates[card_num].format(**data)
		elif openrate_region1 >= 100:
			card_num = '10-2'
			text = text_templates[card_num].format(**data)
		else:
			sub = sess.query(func.max(OpenProgress.tooTotal).label('tooTotal'), func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid')).filter(OpenProgress.datatime<=time).group_by(OpenProgress.townCode).subquery()

			tooTotal, n_total, invalid = sess.query(func.sum(sub.c.tooTotal), func.sum(sub.c.n_total), func.sum(sub.c.invalid)).first()

			if invalid == None:
				invalid = 0
			openrate_avg_nat = (n_total + invalid) / tooTotal * 100

			openrate_region1_openrate_avg_nat = openrate_region1 - openrate_avg_nat
			compare_region1 = '높은' if openrate_region1_openrate_avg_nat > 0 else '낮은'

			data['openrate_region1'] = round(openrate_region1, 2)
			data['openrate_region1_openrate_avg_nat'] = round(abs(openrate_region1_openrate_avg_nat), 2)
			data['compare_region1'] = compare_region1
			card_num = '10'
			text = text_templates[card_num].format(**data)

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
			},
			'debugging': card_num,
		}

	elif card_seq == 11:
		poll, poll_num_sunname = sess.query(SgTypecode.sgName, func.count(PrecinctCode.sggCityCode)).join(PrecinctCode, PrecinctCode.electionCode==SgTypecode.sgTypecode).filter(SgTypecode.sgTypecode==polls[index]).first()
		# print(polls[index], poll, poll_num_sunname)

		# poll 종류에 대해 달라져야함, OpenSido / OpenGusigun ...
		# poll 종류에 따라 table을 선택하고, table마다 column name은 같도록
		# Open = openTable(polls[index])

		if polls[index] == 2: # 국회의원
			subq = sess.query(func.max(OpenProgress2.serial).label('maxserial'), func.max(OpenProgress2.datatime).label('maxtime')).group_by(OpenProgress2.sgg).filter(OpenProgress2.datatime<=time).subquery()

			sub = sess.query(OpenProgress2.sgg, OpenProgress2.tooTotal, OpenProgress2.n_total, OpenProgress2.invalid).join(subq, and_(OpenProgress2.serial==subq.c.maxserial, OpenProgress2.datatime==subq.c.maxtime))

			tooTotal, n_total, invalid = sess.query(func.sum(OpenProgress2.tooTotal), func.sum(OpenProgress2.n_total), func.sum(OpenProgress2.invalid)).join(subq, and_(OpenProgress2.serial==subq.c.maxserial, OpenProgress2.datatime==subq.c.maxtime)).first()

		elif polls[index] == 3:
			subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.gusigun=='합계').subquery()

			sub = sess.query(OpenProgress3.sido, OpenProgress3.tooTotal, OpenProgress3.n_total, OpenProgress3.invalid).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))

			tooTotal, n_total, invalid = sess.query(func.sum(OpenProgress3.tooTotal), func.sum(OpenProgress3.n_total), func.sum(OpenProgress3.invalid)).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime)).first()

		elif polls[index] == 4:
			subq = sess.query(func.max(OpenProgress4.serial).label('maxserial'), func.max(OpenProgress4.datatime).label('maxtime')).group_by(OpenProgress4.townCode).filter(OpenProgress4.datatime<=time).subquery()

			sub = sess.query(OpenProgress4.sido, OpenProgress4.tooTotal, OpenProgress4.n_total, OpenProgress4.invalid).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime))

			tooTotal, n_total, invalid = sess.query(func.sum(OpenProgress4.tooTotal), func.sum(OpenProgress4.n_total), func.sum(OpenProgress4.invalid)).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime)).first()

		elif polls[index] == 11:
			subq = sess.query(func.max(OpenProgress11.serial).label('maxserial'), func.max(OpenProgress11.datatime).label('maxtime')).group_by(OpenProgress11.sido).filter(OpenProgress11.datatime<=time, OpenProgress11.gusigun=='합계').subquery()

			sub = sess.query(OpenProgress11.sido, OpenProgress11.tooTotal, OpenProgress11.n_total, OpenProgress11.invalid).join(subq, and_(OpenProgress11.serial==subq.c.maxserial, OpenProgress11.datatime==subq.c.maxtime))

			tooTotal, n_total, invalid = sess.query(func.sum(OpenProgress11.tooTotal), func.sum(OpenProgress11.n_total), func.sum(OpenProgress11.invalid)).join(subq, and_(OpenProgress11.serial==subq.c.maxserial, OpenProgress11.datatime==subq.c.maxtime)).first()

		else:
			raise NoTextError

		poll_openrate_ranks = []
		if invalid == None:
			invalid = 0

		try:
			poll_openrate_nat_avg = (n_total + invalid) / tooTotal * 100
			
			for r, tooTotal, n_total, invalid in sub.all():
				v = (n_total + invalid) / tooTotal
				poll_openrate_ranks.append({'name':r, 'value':v})
			
			poll_openrate_ranks = sorted(poll_openrate_ranks, key=lambda x: x['value'], reverse=True)
			# print(poll_openrate_ranks)

			if poll_openrate_nat_avg >= 100:
				data = {
					'hour': hourConverter(time.hour),
					'poll': poll,
				}
				card_num = '11-2'
				text = text_templates[card_num].format(**data)
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
				card_num = '11'
				text = text_templates[card_num].format(**data)

		except TypeError:
			if tooTotal == None:
				data = {
					'hour': hourConverter(time.hour),
					'poll': poll,
					'josa': josaPick(poll, '은'),
				}
				card_num = '11-1'
				text = text_templates[card_num].format(**data)
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
			}, 
			'debugging': card_num,
		}

	elif card_seq == 12:
		candidate, candidate_region, candidate_sdName, candidate_poll_code = sess.query(CandidateInfo.name, CandidateInfo.sggName, CandidateInfo.sdName, CandidateInfo.sgTypecode).filter(CandidateInfo.huboid==candidates[index]).first()
		print(candidate_poll_code)
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
			print(candidate_poll_openrate)
			candidate_poll_openrate_sub = sess.query(OpenProgress11.openPercent, OpenProgress11.gusigun).filter(OpenProgress11.datatime<=time, OpenProgress11.sido==candidate_sdName, OpenProgress11.gusigun!='합계').all()

		# else:
		# 	raise NoTextError

		data = {
			'candidate': candidate,
			'candidate_region': candidate_region,
			'candidate_poll': candidate_poll,
			'candidate_poll_openrate': candidate_poll_openrate,
		}
		
		if candidate_poll_openrate == None:
			card_num = '12-1'
			text = text_templates[card_num].format(**data)
		elif candidate_poll_openrate >= 100:
			card_num = '12-2'
			text = text_templates[card_num].format(**data)
		else:
			card_num = '12'
			text = text_templates[card_num].format(**data)

		if candidate_poll_code in [2,4]:
			meta_card = {
				'order': order,
				'type': 'default',
				'party': 'default',
				'data': {
					'text': text,
				},
				'debugging': card_num,
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
				}, 
				'debugging': card_num,
			}

	elif card_seq == 13:
		subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.gusigun=='합계').subquery()

		sub = sess.query(OpenProgress3.sido, OpenProgress3.tooTotal, OpenProgress3.n_total, OpenProgress3.invalid).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))

		tooTotal, n_total, invalid = sess.query(func.sum(OpenProgress3.tooTotal), func.sum(OpenProgress3.n_total), func.sum(OpenProgress3.invalid)).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime)).first()

		if invalid == None:
			invalid = 0
		openrate_avg_nat = (n_total + invalid) / tooTotal * 100

		if openrate_avg_nat < 100:
			openrate_sido = sess.query(OpenProgress3.sido).filter(OpenProgress3.openPercent==100, OpenProgress3.gusigun=='합계').group_by(OpenProgress3.sido).all()
			if len(openrate_sido) > 0:
				data = {
					'hour': hourConverter(time.hour),
					'open_finished_sido': ', '.join(sido[0] for sido in openrate_sido),
				}
				card_num = '13'
				text = text_templates[card_num].format(**data)
			else:
				text = ''

			openrate_gusigun = sess.query(OpenProgress4.gusigun).filter(OpenProgress4.openPercent==100).group_by(OpenProgress4.gusigun).all()
			if len(openrate_gusigun) > 0:
				data = {
					'hour': hourConverter(time.hour),
					'open_finished_gusigun': ', '.join(gusigun[0] for gusigun in openrate_gusigun),
				}
				card_num = '13-1'
				text += text_templates[card_num].format(**data)
			else:
				text += ''
		else:
			card_num = '13-2'
			text = text_templates[card_num].format(hour=hourConverter(time.hour))

		if text == '':
			raise NoTextError
		else:
			text = text

		meta_card = {
			'order': order,
			'type': 'text',
			'party': 'default',
			'data': {
				'text': text,
			},
			'debugging': card_num,
		}

	# elif card_seq == 14:
	# 	subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.gusigun=='합계').subquery()

	# 	sub_ranks = sess.query(OpenProgress3).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))
	# 	# 실제에서 time 살리기
	# 	ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
	# 	if len(ranksDf) == 0:
	# 		raise NoTextError

	# 	ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)	
	# 	ranks_ttl = []
	# 	for i, ranks in ranks_vote.iterrows():
	# 		ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])
	# 	# 각 group 마다 랭킹 만들기
	# 	ranking = []
	# 	for idx, ranks in enumerate(ranks_ttl):
	# 		for i, r in enumerate(ranks):
	# 			ranking.append({
	# 				'idx': idx,
	# 				'rank': i,
	# 				'jdName':ranksDf.loc[idx, r+'_jdName'],현
	# 				'name': ranksDf.loc[idx, r+'_name'],
	# 				'percent': ranksDf.loc[idx, r+'_percent'],
	# 			})
	# 	rank1_count = Counter([r['jdName'] for r in ranking if r['rank']==1]).most_common()
	# 	# TODO: count 개수가 같아서 동률일때 
	# 	rank1_party = rank1_count[0][0]
	# 	rank1_party_num = rank1_count[0][1]

	# 	data = {
	# 		'hour': hourConverter(time.hour),
	# 		'rank1_party': rank1_party,
	# 		'josa1': josaPick(rank1_party, '이'),
	# 		'josa2': josaPick(rank1_party, '은'),
	# 		'rank1_party_num': rank1_party_num,
	# 	}
	# 	text = text_templates[card_seq].format(**data)

	# 	meta_card = {
	# 		'order': order,
	# 		'type': 'winner',
	# 		'party': rank1_party,
	# 		'data': {
	# 			'title': hourConverter(time.hour) + ', ' + str(rank1_party_num) + '개 선거구 1위',
	# 			'name': rank1_party,
	# 			'text': text,
	# 		}
	# 	}

	elif card_seq == 15:
		try:
			candidate_poll_code = sess.query(CandidateInfo.sgTypecode).filter(CandidateInfo.huboid==candidates[index]).first()[0]
		except IndexError:
			candidate_poll_code = None

		if len(regions) == 0:
			openrate_rank1_region = None
			if (candidate_poll_code == 3) or (polls[index] == 3): # 시도지사
				subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.gusigun=='합계').subquery()

				sub_ranks = sess.query(OpenProgress3).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))
		
			elif (candidate_poll_code == 4) or (polls[index] == 4): # 시군구청장
				subq = sess.query(func.max(OpenProgress4.serial).label('maxserial'), func.max(OpenProgress4.datatime).label('maxtime')).group_by(OpenProgress4.gusigun).filter(OpenProgress4.datatime<=time).subquery()

				sub_ranks = sess.query(OpenProgress4).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime))

			elif (candidate_poll_code == 2) or (polls[index] == 2): # 국회의원
				subq = sess.query(func.max(OpenProgress2.serial).label('maxserial'), func.max(OpenProgress2.datatime).label('maxtime')).group_by(OpenProgress2.sgg).filter(OpenProgress2.datatime<=time).subquery()

				sub_ranks = sess.query(OpenProgress2).join(subq, and_(OpenProgress2.serial==subq.c.maxserial, OpenProgress2.datatime==subq.c.maxtime))

			elif (candidate_poll_code == 11) or (polls[index] == 11): # 교육감
				openrate_rank1_region = sess.query(OpenProgress11.sido).filter(OpenProgress11.datatime<=time, OpenProgress11.gusigun=='합계').order_by(func.max(OpenProgress11.openPercent).desc()).scalar()
			
				subq = sess.query(func.max(OpenProgress11.serial).label('maxserial'), func.max(OpenProgress11.datatime).label('maxtime')).group_by(OpenProgress11.sido).filter(OpenProgress11.datatime<=time, OpenProgress11.gusigun=='합계').subquery()

				sub_ranks = sess.query(OpenProgress11).join(subq, and_(OpenProgress11.serial==subq.c.maxserial, OpenProgress11.datatime==subq.c.maxtime))
			
			ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
			ranksDf = ranksDf.sort_values(by='openPercent', ascending=False)
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
			# print(ranking)
			rank1_count = Counter([r['jdName'] for r in ranking if r['rank']==0]).most_common()
			rank1_party = rank1_count[0][0]
			rank1_party_num = rank1_count[0][1]
			# print(rank1_count)
			ranks_party = ', '.join(r[0] for r in rank1_count[1:] if r[0] != None)

			openrate_rank1_region_candidate = [r['name'] for r in ranking if (r['idx']==0) and (r['rank']==0)][0]
			openrate_rank2_region_candidate = [r['name'] for r in ranking if (r['idx']==0) and (r['rank']==1)][0]

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

			if (candidate_poll_code == 11) or (polls[index] == 11):
				card_num = '15-11'
				text = text_templates[card_num].format(**data)
				meta_card = {
					'order': order,
					'type': 'winner',
					'party': 'default',
					'data': {
						'title': hourConverter(time.hour) + ', ' + openrate_rank1_region + ' 교육감선거 1위',
						'name': openrate_rank1_region_candidate,
						'text': text,
					},
					'debugging': card_num,
				}
			else:
				card_num = candidate_poll_code or polls[index]
				card_num = '15-' + str(card_num)
				text = text_templates[card_num].format(**data)

				meta_card = {
					'order': order,
					'type': 'winner',
					'party': rank1_party,
					'data': {
						'title': hourConverter(time.hour) + ', ' + str(rank1_party_num) + '개 선거구 1위',
						'name': rank1_party,
						'text': text,
					},
					'debugging': card_num,
				}
			# else:
				# raise NoTextError
		else: # 지역선택이 있으면
			subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.gusigun=='합계').subquery()

			sub_ranks = sess.query(OpenProgress3).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))
			# 실제에서 time 살리기
			ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
			if len(ranksDf) == 0:
				raise NoTextError

			ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)	
			ranks_ttl = []
			for i, ranks in ranks_vote.iterrows():
				ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])
			# 각 group 마다 랭킹 만들기
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
			rank1_count = Counter([r['jdName'] for r in ranking if r['rank']==1]).most_common()
			# TODO: count 개수가 같아서 동률일때 
			rank1_party = rank1_count[0][0]
			rank1_party_num = rank1_count[0][1]

			data = {
				'hour': hourConverter(time.hour),
				'rank1_party': rank1_party,
				'josa1': josaPick(rank1_party, '이'),
				'josa2': josaPick(rank1_party, '은'),
				'rank1_party_num': rank1_party_num,
			}
			card_num = '14'
			text = text_templates[card_num].format(**data)

			meta_card = {
				'order': order,
				'type': 'winner',
				'party': rank1_party,
				'data': {
					'title': hourConverter(time.hour) + ', ' + str(rank1_party_num) + '개 선거구 1위',
					'name': rank1_party,
					'text': text,
				},
				'debugging': card_num,
			}

	elif card_seq == 16:
		try:
			region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.townCode==regions[index]).first()
		except TypeError:
			raise NoTextError
		if region2 == '합계':
			region2 = None
		
		region1_poll = regionPoll(region1, 3)

		region1_openrate = sess.query(func.max(OpenProgress3.openPercent)).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==region1).scalar()

		subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.gusigun=='합계').subquery()

		sub_ranks = sess.query(OpenProgress3).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))

		ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
		if len(ranksDf) == 0:
			raise NoTextError

		ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)	
		ranks_ttl = [] # one line
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
			card_num = '16-3'
		else:
			if (region1_rank1_rate - region1_rank2_rate) >= 15:
				card_num = '16-2'
			elif (region1_rank1_rate - region1_rank2_rate) < 5:
				card_num = '16-1'
			else:
				card_num = '16'
		
		text = text_templates[card_num].format(**data)

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
			},
			'debugging': card_num,
		}
	
	elif card_seq == 17:
		candidate, candidate_region, sgtype = sess.query(CandidateInfo.name, CandidateInfo.sggName, CandidateInfo.sgTypecode).filter(CandidateInfo.huboid==candidates[index]).first()
		candidate_poll = regionPoll(candidate_region, sgtype)

		# candidate_poll table 선택
		if sgtype == 2: 
			candidate_poll_openrate = sess.query(func.max(OpenProgress2.openPercent)).filter(OpenProgress2.datatime<=time, OpenProgress2.sgg==candidate_region).scalar()

			subq = sess.query(func.max(OpenProgress2.serial).label('maxserial'), func.max(OpenProgress2.datatime).label('maxtime')).group_by(OpenProgress2.sgg).filter(OpenProgress2.datatime<=time, OpenProgress2.sgg==candidate_region).subquery()

			sub_ranks = sess.query(OpenProgress2).join(subq, and_(OpenProgress2.serial==subq.c.maxserial, OpenProgress2.datatime==subq.c.maxtime))

		elif sgtype == 3:
			candidate_poll_openrate = sess.query(func.max(OpenProgress3.openPercent)).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==candidate_region).scalar()

			subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==candidate_region, OpenProgress3.gusigun=='합계').subquery()

			sub_ranks = sess.query(OpenProgress3).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))

		elif sgtype == 4:
			candidate_poll_openrate = sess.query(func.max(OpenProgress4.openPercent)).filter(OpenProgress4.datatime<=time, OpenProgress4.gusigun==candidate_region).scalar()
			
			subq = sess.query(func.max(OpenProgress4.serial).label('maxserial'), func.max(OpenProgress4.datatime).label('maxtime')).group_by(OpenProgress4.gusigun).filter(OpenProgress4.datatime<=time, OpenProgress4.gusigun==candidate_region).subquery()

			sub_ranks = sess.query(OpenProgress4).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime))

		elif sgtype == 11:
			candidate_poll_openrate = sess.query(func.max(OpenProgress11.openPercent)).filter(OpenProgress11.sido==candidate_region, OpenProgress11.gusigun=='합계').scalar()

			subq = sess.query(func.max(OpenProgress11.serial).label('maxserial'), func.max(OpenProgress11.datatime).label('maxtime')).group_by(OpenProgress11.sido).filter(OpenProgress11.datatime<=time, OpenProgress11.sido==candidate_region, OpenProgress11.gusigun=='합계').subquery()

			sub_ranks = sess.query(OpenProgress11).join(subq, and_(OpenProgress11.serial==subq.c.maxserial, OpenProgress11.datatime==subq.c.maxtime))

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

		if candidate_poll_rank1_name == candidate: 
			if (candidate_poll_rank1_rate - candidate_poll_rank2_rate) >= 15:
				card_num = '17-3'
				text = text_templates[card_num].format(**data)
			elif (candidate_poll_rank1_rate - candidate_poll_rank2_rate) < 5:
				card_num = '17-1'
				text = text_templates[card_num].format(**data)
			elif confirm:
				card_num = '17-6'
				text = text_templates[card_num].format(**data)
			else:
				card_num = '17'
				text = text_templates[card_num].format(**data)

		elif candidate_poll_rank2_name == candidate:
			if abs(candidate_poll_rank1_rate - candidate_poll_rank2_rate) >= 15:
				card_num = '17-4'
				text = text_templates[card_num].format(**data)
			elif abs(candidate_poll_rank1_rate - candidate_poll_rank2_rate) < 5:
				card_num = '17-2'
				text = text_templates[card_num].format(**data)
			elif confirm:
				card_num = '17-7'
				text = text_templates[card_num].format(**data)
			else:
				text = text_templates[card_seq].format(**data)

		else:
			if abs(candidate_poll_rank1_rate - candidate_poll_rank2_rate) < 5:
				card_num = '17-5'
				text = text_templates[card_num].format(**data)
			else:
				card_num = '17'
				text = text_templates[card_num].format(**data)
		
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
			},
			'debugging': card_num,
		}
		

	elif card_seq == 18:
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
		
		# 구시군청장
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

		# 
		print(rank1_count)
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
				
		graph_data = []
		for r in rank1_count:
			graph_data.append({
				'party': r[0],
				'value': float(r[1] / len(ranking[0])),
			})
		
		# print(graph_data)
		if abs(party_rank1_sido_num - party_rank2_sido_num) / len(rank1_count_g) < 0.05: # 1,2위 경합
			card_num = '18-1'
			graph = True

		elif abs(party_rank2_sido_num - party_rank3_sido_num) / len(rank1_count_g) < 0.05: # 2,3위 경합
			card_num = '18-2'
			graph = True
		
		elif (abs(party_rank1_sido_num - party_rank2_sido_num) / len(rank1_count_g) < 0.05) and (abs(party_rank2_sido_num - party_rank3_sido_num) / len(rank1_count_g) < 0.05): # 1,2,3위 경합
			card_num = '18-3'
			graph = True

		elif (party == party_rank1_sido_name) and (abs(ranking[0][0]['percent'] - ranking[0][1]['percent']) > 15): # 내가 선택한 정당이 1위일때, 1위와 2위의 격차가 15% 이상
			card_num = '18-4'
			graph = True
		
		elif (party == party_rank2_sido_name) and (abs(ranking[0][0]['percent'] - ranking[0][1]['percent']) > 15): # 내가 선택한 정당이 2위일때, 1위와 2위의 격차가 15% 이상
			card_num = '18-5'
			graph = True

		elif confirms_count[0][0] == party:
			data['party_rank1_sido_num_confirm'] = confirms_count[0][1],
			data['party_rank1_gusigun_num_confirm'] = [v for r, v in confirms_count_g if r == party][0],
			card_num = '18-6'
			graph = False

		elif confirms_count[1][0] == party:
			data['party_rank1_sido_num_confirm'] = confirms_count[1][1],
			data['party_rank1_gusigun_num_confirm'] = [v for r, v in confirms_count_g if r == party][0],
			card_num = '18-7'
			graph = False
		
		else:
			card_num = '18'
			graph = False
			
		text = text_templates[card_num].format(**data)
		if graph:
			meta_card = {
				'order': order,
				'type': 'graph',
				'party': 'default',
				'data': {
					'graph_data': {
						'type': 'party',
						'data': graph_data,
					},
					'text': text,
				},
				'debugging': card_num,
			}
		else:
			meta_card = {
				'order': order,
				'type': 'default',
				'party': 'default',
				'data': {
					'text': text,
				},
				'debugging': card_num,
			}


	elif card_seq == 19:
		# TODO: sub with time
		if polls[index] == 2:
			sub = sess.query(OpenProgress2) # time 추가

		elif polls[index] == 3:
			sub = sess.query(OpenProgress3).filter(OpenProgress3.gusigun=='합계')
		
		elif polls[index] == 4:
			sub = sess.query(OpenProgress4)
		
		elif polls[index] == 11:
			sub = sess.query(OpenProgress11).filter(OpenProgress11.gusigun=='합계')
		# else:
		# 	sub = sess.query(OpenProgress).group_by(OpenProgress.sido)

		if polls[index] in [2,3,4]:
			ranksDf = pd.read_sql(sub.statement, sub.session.bind)
			if len(ranksDf) == 0:
				raise NoTextError

			ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)

			ranks_ttl = [] # 각 지역 - 순위
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
			if len(ranksDf) == 0:
				raise NoTextError

			ranksDf = ranksDf.sort_values(by='openPercent', ascending=False)
			ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)

			ranks_ttl = []
			for i, ranks in ranks_vote.iterrows(): # 가로 등수, 세로 지역수: 지역끼리
				ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])
			
			ranking = []
			for idx, ranks in enumerate(ranks_ttl):
				for i, r in enumerate(ranks):
					ranking.append({
						'idx': idx,
						'rank': i,
						'sido':ranksDf.loc[idx, 'sido'],
						'name': ranksDf.loc[idx, r+'_name'],
						})

			open_rank1_region = [r['sido'] for r in ranking if r['idx'] == 0][0] 
			open_rank1_region_candidate = [r['name'] for r in ranking if (r['idx'] == 0) and (r['rank']==0)][0]
			try:
				open_rank2_region = [r['sido'] for r in ranking if r['idx'] == 1][0] 
				open_rank2_region_candidate = [r['name'] for r in ranking if (r['idx'] == 1) and (r['rank']==0)][0] 
				open_rank2 = '그 다음으로 개표가 빠른 지역은 ' + open_rank2_region + '로, 이 지역에서는 ' + open_rank2_region_candidate + ' 후보가 1위로 앞서 나가고 있다.'
			except IndexError:
				open_rank2 = ''

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
		if polls[index] == 2:
			if (abs(rank1_party_num-rank2_party_num) / len(ranking) < 0.05):
				card_num = '19-4'
			elif (abs(rank1_party_num-rank2_party_num) / len(ranking) > 0.15):
				card_num = '19-7'
			elif (confirms_rank1_party_num + confirms_rank2_party_num) > 2:
				card_num = '19-14'
			else:
				card_num = '19'
			
		elif polls[index] == 3:
			if (abs(rank1_party_num-rank2_party_num) / len(ranking) < 0.05):
				card_num = '19-5'
			elif (abs(rank1_party_num-rank2_party_num) / len(ranking) > 0.15):
				card_num = '19-8'
			elif (confirms_rank1_party_num + confirms_rank2_party_num) > 2:
				card_num = '19-15'
			else:
				card_num = '19-1'
		
		elif polls[index] == 4:
			if (abs(rank1_party_num-rank2_party_num) / len(ranking) < 0.05):
				card_num = '19-6'
			elif (abs(rank1_party_num-rank2_party_num) / len(ranking) > 0.15):
				card_num = '19-9'
			elif (confirms_rank1_party_num + confirms_rank2_party_num) > 2:
				card_num = '19-16'
			else:
				card_num = '19-2'
			
		
		elif polls[index] == 11:
			if len(confirms) > 2:
				card_num = '19-17'
			else:
				card_num = '19-3'
		try:
			text = text_templates[card_num].format(**data)
		except KeyError:
			raise NoTextError

		meta_card = {
			'order': order,
			'type': 'default',
			'party': 'default',
			'data': {
				'text': text,
			},
			'debugging': card_num,
		}

	elif card_seq == 20:
		# 바른정당의 시도지사, 시군구청장, 국회의원 보궐선거 성적
		# 제 7회 지방선거에 단독 정당을 처음으로 출정한 바른미래당은 {현재 시간.시각} 현재, 시도지사 선거에서는 {선거구 수.바미당.전국.시도지사.순위1}개, 시군구청장 선거에서는 {선거구 수.바미당.전국.시군구청장.순위1}개의 선거구에서 1위를 달리고 있다. 과연 충분한 성과를 얻어 원내 3당의 입지를 확고히 할 수 있을지 귀추가 주목된다.
		texts = []
		# TODO: sub_ranks
		subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.gusigun=='합계').subquery()

		sub_ranks = sess.query(OpenProgress3).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))

		ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
		ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)	
		ranks_ttl = [] # one line
		for i, ranks in ranks_vote.iterrows():
			ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])
		
		for idx, ranks in enumerate(ranks_ttl): # 지역마다
			yet_cnt = ranksDf.loc[idx, 'tooTotal'] - ranksDf.loc[idx, 'n_total'] - ranksDf.loc[idx, 'invalid']
			rank1_cnt = ranksDf.loc[idx, ranks[0]+'_vote']
			rank2_cnt = ranksDf.loc[idx, ranks[1]+'_vote']
			confirm = True if (rank1_cnt-rank2_cnt) > yet_cnt else False
			ranking = []
			if confirm:
				rank1_candidate = {
							'idx': idx,
							'rank': 0,
							'sido': ranksDf.loc[idx, 'sido'],
							'huboid': ranksDf.loc[idx, ranks[0]+'_huboid'],
							'name': ranksDf.loc[idx, ranks[0]+'_name'],
							'current': sess.query(CandidateInfo.current).filter(CandidateInfo.huboid==int(ranksDf.loc[idx, ranks[0]+'_huboid'])).scalar(),
							'percent': ranksDf.loc[idx, ranks[0]+'_percent'],
						}
				rank2_candidate = {
							'idx': idx,
							'rank': 1,
							'sido': ranksDf.loc[idx, 'sido'],
							'huboid': ranksDf.loc[idx, ranks[1]+'_huboid'],
							'name': ranksDf.loc[idx, ranks[1]+'_name'],
							'current': sess.query(CandidateInfo.current).filter(CandidateInfo.huboid==int(ranksDf.loc[idx, ranks[1]+'_huboid'])).scalar(),
							'percent': ranksDf.loc[idx, ranks[1]+'_percent'],
						}
				for i, r in enumerate(ranks): # 한 지역
					if sess.query(CandidateInfo.current).filter(CandidateInfo.huboid==int(ranksDf.loc[idx, r+'_huboid'])).scalar() == 1:
						current_candidate = {
							'idx': idx,
							'rank': i,
							'sido': ranksDf.loc[idx, 'sido'],
							'huboid': ranksDf.loc[idx, r+'_huboid'],
							'name': ranksDf.loc[idx, r+'_name'],
							'current': 1,
							'percent': ranksDf.loc[idx, r+'_percent'],
						}
			try:
				if rank1_candidate['huboid'] == current_candidate['huboid']:
					# current = rank1
					data = {
						'region': rank1_candidate['sido'],
						'poll': regionPoll(rank1_candidate['sido'], 3),
						'current_name': rank1_candidate['name'],
						'rank2_name': rank2_candidate['name'],
						'diff_percent': round(abs(rank1_candidate['percent']-rank2_candidate['percent']), 2),
					}
					card_num = '20-2'
					texts.append(text_templates[card_num].format(**data))
				
				else:
					data = {
						'region': rank1_candidate['sido'],
						'poll': regionPoll(rank1_candidate['sido'], 3),
						'current_name': current_candidate['name'],
						'rank1_name': rank1_candidate['name'],
						'diff_percent': round(abs(rank1_candidate['percent']-current_candidate['percent']), 2),
					}
					card_num = '20-1'
					texts.append(text_templates[card_num].format(**data))
			except:
				pass

		# 구시군청장
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
			ranking_g = []
			if confirm:
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
					texts.append(text_templates[card_num].format(**data))
				
				else:
					data = {
						'region': rank1_candidate_g['gusigun'],
						'poll': regionPoll(rank1_candidate_g['gusigun'], 4),
						'current_name': current_candidate_g['name'],
						'rank1_name': rank1_candidate_g['name'],
						'diff_percent': round(abs(rank1_candidate_g['percent']-current_candidate_g['percent']), 2),
					}
					card_num = '20-1'
					texts.append(text_templates[card_num].format(**data))
			except:
				pass

				# current 없으면 패스
				# current 1인게 있으면
				# 그게 1등인지, 아닌지 판단해서
				# 1등이면 20-2, 1위, 2위 차이 구하기
				# 1등 아니면 20-1, 1위와 현직의 차이 구하기

		output_num = randint(0,2)

		if output_num == 0:
			text = choice(texts)

		elif output_num == 1: # 바른정당
			sido_rank1_party_num = 0
			for idx, ranks in enumerate(ranks_ttl):
				if ranksDf.loc[idx, ranks[0]+'_jdName'] == '바른미래당':
					sido_rank1_party_num += 1
			
			gusigun_rank1_party_num = 0
			for idx, ranks in enumerate(ranks_ttl_g):
				if ranksDf_g.loc[idx, ranks[0]+'_jdName'] == '바른미래당':
					gusigun_rank1_party_num += 1

			data = {
				'hour': hourConverter(time.hour),
				'sido_rank1_party_num': sido_rank1_party_num,
				'gusigun_rank1_party_num': gusigun_rank1_party_num,
			}
			card_num = '20-33'
			text = text_templates[card_num].format(**data)

		elif output_num == 2:
			# 지역주의
			# 전남 자유한국당 시군구청장 1위 + 광주
			# 전남 바른미래당 시군구청장 1위 + 가ㅗㅇ주
			# 자당+바른 / 전남+광주
			bsjbtexts = []
			sub_bs = sess.query(OpenProgress.serial, func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sido).filter(OpenProgress.electionCode.in_([3,4]), OpenProgress.sido.in_(['전라남도', '광주광역시']), OpenProgress.datatime<=time).subquery()
			query_bs = sess.query(OpenProgress).join(sub_bs, and_(OpenProgress.serial==sub_bs.c.serial, OpenProgress.datatime==sub_bs.c.maxtime))
			
			bsDf = pd.read_sql(query_bs.statement, query_bs.session.bind)
			bsDf_ranks = bsDf.filter(regex="n*_percent").dropna(axis=1)
			bsDf_ranks_ttl = []
			for i, ranks in bsDf_ranks.iterrows():
				bsDf_ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])

			gj_num = len(bsDf_ranks_ttl)
			bs_jayu = 0
			bs_bamin = 0
			for idx, ranks in enumerate(bsDf_ranks_ttl):
				for i, r in enumerate(ranks):
					if i == 0:
						if bsDf.loc[idx, r+'_jdName'] == '자유한국당':
							bs_jayu += 1
						elif bsDf.loc[idx, r+'_jdName'] == '바른미래당':
							bs_bamin += 1
			try:
				bs_ratio = round((bs_jayu + bs_bamin) / gj_num * 100, 2)
			except ZeroDivisionError:
				bs_ratio = 0
			card_num = '20-3'
			bsjbtexts.append(text_templates[card_num].format(bs_jayu=bs_jayu, bs_bamin=bs_bamin, bs_ratio=bs_ratio))
			# 대국경북 민주당
			# 대구 경국 정의당
			sub_jb = sess.query(OpenProgress.serial, func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sido).filter(OpenProgress.electionCode.in_([3,4]), OpenProgress.sido.in_(['경상북도', '대구광역시']), OpenProgress.datatime<=time).subquery()
			query_jb = sess.query(OpenProgress).join(sub_jb, and_(OpenProgress.serial==sub_jb.c.serial, OpenProgress.datatime==sub_jb.c.maxtime))
			
			jbDf = pd.read_sql(query_jb.statement, query_jb.session.bind)
			jbDf_ranks = jbDf.filter(regex="n*_percent").dropna(axis=1)
			jbDf_ranks_ttl = []
			for i, ranks in jbDf_ranks.iterrows():
				jbDf_ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])

			tk_num = len(jbDf_ranks_ttl)
			jb_minju = 0
			jb_jung = 0
			for idx, ranks in enumerate(jbDf_ranks_ttl):
				for i, r in enumerate(ranks):
					if i == 0:
						if jbDf.loc[idx, r+'_jdName'] == '더불어민주당':
							jb_minju += 1
						elif jbDf.loc[idx, r+'_jdName'] == '정의당':
							jb_jung += 1
			try:
				jb_ratio = round((jb_minju + jb_jung) / tk_num * 100, 2)
			except ZeroDivisionError:
				jb_ratio = 0
			
			card_num = '20-4'
			bsjbtexts.append(text_templates[card_num].format(jb_minju=jb_minju, jb_jung=jb_jung, jb_ratio=jb_ratio))

			text = choice(bsjbtexts)


		meta_card = {
			'order': order,
			'type': 'default',
			'party': 'default',
			'data': {
				'text': text,
			},
			'debugging': card_num,
		}

	elif card_seq == 21:
		# 당선확정, 이용자가 선택한 선거구에서 당선 확정자가 나왔을 경우
		if len(candidates) > 0:
			candidates_all = sess.query(CandidateInfo.name, CandidateInfo.sggName, CandidateInfo.sgTypecode).filter(CandidateInfo.huboid.in_(candidates)).all()
			# print(candidates_all)
			candidates_text = []
			for candidate, candidate_region, sgtype in candidates_all:
				candidate_poll = regionPoll(candidate_region, sgtype)

				# candidate_poll table 선택
				if sgtype == 2: 
					candidate_poll_openrate = sess.query(func.max(OpenProgress2.openPercent)).filter(OpenProgress2.datatime<=time, OpenProgress2.sgg==candidate_region).scalar()
					sub_ranks = sess.query(OpenProgress2).filter(OpenProgress2.datatime<=time, OpenProgress2.sgg==candidate_region).group_by(OpenProgress2.sgg)
					# candidate_poll_openrate = sess.query(func.max(OpenProgress2.openPercent)).filter(OpenProgress2.sgg==candidate_region).scalar()
					# sub_ranks = sess.query(OpenProgress2).filter( OpenProgress2.sgg==candidate_region)
				elif sgtype == 3:
					candidate_poll_openrate = sess.query(func.max(OpenProgress3.openPercent)).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==candidate_region, OpenProgress3.gusigun=='합계').scalar()
					sub_ranks = sess.query(OpenProgress3).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==candidate_region, OpenProgress3.gusigun=='합계').group_by(OpenProgress3.sido)
					# candidate_poll_openrate = sess.query(func.max(OpenProgress3.openPercent)).filter( OpenProgress3.sido==candidate_region, OpenProgress3.gusigun=='합계').scalar()
					# sub_ranks = sess.query(OpenProgress3).filter(OpenProgress3.sido==candidate_region, OpenProgress3.gusigun=='합계')
				elif sgtype == 4:
					candidate_poll_openrate = sess.query(func.max(OpenProgress4.openPercent)).filter(OpenProgress4.datatime<=time, OpenProgress4.gusigun==candidate_region).scalar()
					sub_ranks = sess.query(OpenProgress4).filter(OpenProgress4.datatime<=time, OpenProgress4.gusigun==candidate_region).group_by(OpenProgress4.gusigun)
					# candidate_poll_openrate = sess.query(func.max(OpenProgress4.openPercent)).filter( OpenProgress4.gusigun==candidate_region).scalar()
					# sub_ranks = sess.query(OpenProgress4).filter(OpenProgress4.gusigun==candidate_region)
				elif sgtype == 11:
					candidate_poll_openrate = sess.query(func.max(OpenProgress11.openPercent)).filter(OpenProgress11.datatime<=time,OpenProgress11.sido==candidate_region,OpenProgress11.gusigun=='합계').scalar()
					sub_ranks = sess.query(OpenProgress11).filter(OpenProgress11.datatime<=time, OpenProgress11.sido==candidate_region,OpenProgress11.gusigun=='합계').group_by(OpenProgress11.sido)
					# candidate_poll_openrate = sess.query(func.max(OpenProgress11.openPercent)).filter(OpenProgress11.sido==candidate_region, OpenProgress11.gusigun=='합계').scalar()
					# sub_ranks = sess.query(OpenProgress11).filter(OpenProgress11.sido==candidate_region, OpenProgress11.gusigun=='합계')

				ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
				if len(ranksDf) > 0:
					ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)

					ranks_ttl = []
					for i, ranks in ranks_vote.iterrows():
						ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])

					ranking = []
					candidate_confirm_name = ''
					for idx, ranks in enumerate(ranks_ttl):
						rank1_cnt = ranksDf.loc[idx, ranks[0]+'_vote']
						rank2_cnt = ranksDf.loc[idx, ranks[1]+'_vote']
						yet_cnt = ranksDf.loc[idx, 'tooTotal'] - ranksDf.loc[idx, 'n_total'] - ranksDf.loc[idx, 'invalid']
						confirm = 1 if (rank1_cnt-rank2_cnt) > yet_cnt else 0
						if confirm:
							candidate_confirm_name = ranksDf.loc[idx, ranks[0]+'_name']

					if candidate_confirm_name:
						candidates_text.append('{candidate_region} {candidate_poll} 선거에서 {candidate_confirm_name} 후보가'.format(candidate_region=candidate_region, candidate_poll=candidate_poll, candidate_confirm_name=candidate_confirm_name))
					else:
						pass
				else: # len(ranksDf) == 0
					pass
			
			candidates_text = ', '.join(candidates_text)

			if candidates_text:
				candidates_text += ', '
		else: # len(candidates) == 0:
			candidates_text = ''

		if len(regions) > 0:
			regions_all = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.townCode.in_(regions)).all()
			regions_all = list(set(regions_all))
			# print(regions_all)
			regions_text = []
			for region1, region2 in regions_all:
				region1Poll = regionPoll(region1, 3) # 시도지사
				sub_ranks = sess.query(OpenProgress3).filter(OpenProgress3.sido==region1, OpenProgress3.gusigun=='합계')

				ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
				if len(ranksDf) > 0:
					ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)	
					ranks_ttl = [] # one line
					for i, ranks in ranks_vote.iterrows():
						ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])
					ranking = []
					region1_confirm_name = ''
					for idx, ranks in enumerate(ranks_ttl):
						rank1_cnt = ranksDf.loc[idx, ranks[0]+'_vote']
						rank2_cnt = ranksDf.loc[idx, ranks[1]+'_vote']
						yet_cnt = ranksDf.loc[idx, 'tooTotal'] - ranksDf.loc[idx, 'n_total'] - ranksDf.loc[idx, 'invalid']
						confirm = 1 if (rank1_cnt-rank2_cnt) > yet_cnt else 0
						if confirm:
							region1_confirm_name = ranksDf.loc[idx, ranks[0]+'_name']
							print(region1_confirm_name)
					
					if region1_confirm_name:
						regions_text.append('{region1} {region1Poll} 선거에서 {region1_confirm_name} 후보가'.format(region1=region1, region1Poll=region1Poll, region1_confirm_name=region1_confirm_name))
						# print("ggggg:", regions_text)
					else:
						pass
				else:
					pass
				# print(regions_text)
				if region2 == '합계':
					region2 = None
				try:
					region2Poll = regionPoll(region2, 4) # 시도지사
					sub_ranks_g = sess.query(OpenProgress4).filter(OpenProgress4.sido==region1, OpenProgress4.gusigun==region2)
					ranksDf_g = pd.read_sql(sub_ranks_g.statement, sub_ranks_g.session.bind)
					if len(ranksDf_g) > 0:
						ranks_vote_g = ranksDf_g.filter(regex="n*_percent").dropna(axis=1)	
						ranks_ttl_g = [] # one line
						for i, ranks in ranks_vote_g.iterrows():
							ranks_ttl_g.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])
						ranking_g = []
						region2_confirm_name = ''
						for idx, ranks in enumerate(ranks_ttl_g):
							rank1_cnt = ranksDf_g.loc[idx, rank[0]+'_vote']
							rank2_cnt = ranksDf_g.loc[idx, rank[1]+'_vote']
							yet_cnt = ranksDf_g.loc[idx, 'tooTotal'] - ranksDf_g.loc[idx, 'n_total'] - ranksDf_g.loc[idx, 'invalid']
							confirm = 1 if (rank1_cnt-rank2_cnt) > yet_cnt else 0
							if confirm:
								region2_confirm_name = ranksDf_g.loc[idx, ranks[0]+'_name']
						if region2_confirm_name:
							regions_text.append('{region2} {region2Poll} 선거에서 {region2_confirm_name} 후보가'.format(region2=region2, region2Poll=region2Poll, region2_confirm_name=region2_confirm_name))
						else:
							pass
					else:
						pass

				except AttributeError:
					pass
			regions_text = ', '.join(regions_text)
			# print(regions_text)
		else:
			regions_text = ''
		
		# print(candidates_text)
		# print(regions_text)
		
		if (len(candidates_text) > 0) or (len(regions_text) > 0):
			text = hourConverter(time.hour) + ' 현재 ' + candidates_text + regions_text + ' 당선이 확정되었습니다.'
			meta_card = {
				'order': order,
				'type': 'winner',
				'party': 'default',
				'data': {
					'text': text,
				},
				'debugging': '21',
			}
		else:
			raise NoTextError

	elif card_seq == 22:
		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t = 23
		else:
			t = time.hour

		each_toorate = sess.query(func.max(VoteProgress.yooToday).label('yooToday'), func.max(VoteProgress.yooEarly).label('yooEarly'), func.max(VoteProgress.tooToday).label('tooToday'), func.max(VoteProgress.tooEarly).label('tooEarly')).filter(VoteProgress.timeslot<=t).group_by(VoteProgress.sido).subquery()
		yooToday, yooEarly, tooToday, tooEarly = sess.query(func.sum(each_toorate.c.yooToday), func.sum(each_toorate.c.yooEarly), func.sum(each_toorate.c.tooToday), func.sum(each_toorate.c.tooEarly)).first()
		if tooEarly == None:
			tooEarly = 0
		toorate_avg_nat = (tooToday+tooEarly) / (yooToday+yooEarly) * 100

		if toorate_avg_nat < 68.4:
			card_num = '22'
			text = text_templates[card_num].format(toorate_avg_nat=round(toorate_avg_nat, 2))
		elif toorate_avg_nat > 68.4:
			card_num = '22-20'
			text = text_templates[card_num].format(toorate_avg_nat=round(toorate_avg_nat, 2))

		else:
			card_num = '22-' + str(randint(0,7))
			text = text_templates[card_num]

		meta_card = {
			'order': order,
			'type': 'default',
			'party': 'default',
			'data': {
				'text': text,
			},
			'debugging': card_num,
		}

	elif card_seq == 23:
		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t = 23
		else:
			t = time.hour

		if t > 18:
			card_num = '23-' + str(randint(0,4))
		else: 
			card_num = '23-' + str(randint(0,3))
		text = text_templates[card_num].format(hour=hourConverter(time.hour))
		meta_card = {
			'order': order,
			'type': 'default',
			'party': 'default',
			'data': {
				'text': text,
			},
			'debugging': card_num,
		}
	# return text, RANK1, title, rate, name, graph, map
	return meta_card