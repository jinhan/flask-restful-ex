from templates import background_variations
from orm import *
from sqlalchemy.sql import func, and_
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

def timeDisplay(t):
	return hourConverter(t.hour) + ' ' + str(t.minute) + '분'

def josaPick(word, josa):
	return tossi.pick(word, josa)

def regionPoll(r, code):
	if code == 3:
		if r.endswith('시'):
			poll = '시장'
		elif r.endswith('도'):
			poll = '도지사'
		else:
			poll = None
	elif code == 4:
		if r.endswith('구'):
			poll = '구청장'
		elif r.endswith('군'):
			poll = '군수'
		elif r.endswith('시'):
			poll = '시장'
		else:
			poll = None
	elif code == 2:
		poll = '국회의원'
	elif code == 11:
		poll = '교육감'
	else:
		poll = None

	return poll

def regionCodeCheck(r):
	if r in [4101, 4102, 4103, 4104]: # 수원시
		r = 4103
		r = int(str(4)+str(r)+str(0)*2)
	elif r in [4105,4106,4107]: # 성남
		r = 4105
		r = int(str(4)+str(r)+str(0)*2)
	elif r in [4109,4110]: #안양
		r = 4110
		r = int(str(4)+str(r)+str(0)*2)
	elif r in [4119,4118]: #안산
		r = 4119
		r = int(str(4)+str(r)+str(0)*2)
	elif r in [4120,4121,4122]: # 고양
		r = 4120
		r = int(str(4)+str(r)+str(0)*2)
	elif r in [4135,4136,4137]: #용인
		r = 4135
		r = int(str(4)+str(r)+str(0)*2)
	elif r in [4301,4302,4306,4314]: #청주
		r = 4301
		r = int(str(4)+str(r)+str(0)*2)
	elif r in [4417,4418]: # 천안
		r = 4417
		r = int(str(4)+str(r)+str(0)*2)
	elif r in [4701,4702]: # 포항
		r = 4701
		r = int(str(4)+str(r)+str(0)*2)
	elif r in [4821,4823,4822,4824,4825]: #창원
		r = 4821
		r = int(str(4)+str(r)+str(0)*2)
	elif r in [4501,4502]: #전주
		r = 4501
		r = int(str(4)+str(r)+str(0)*2)
	
	elif r == 4145: # 부천시
		r = 4411100
	elif r == 5100: # 세종
		r = 1510000
	elif r == 4901: #제주
		r = 1490100
	elif r == 4902: # 서귀포
		r = 1490200
	else: # 서울표시 
		r = int(str(4)+str(r)+str(0)*2)
	return r

def query_card_data(text_templates, sess, order, index, polls, regions, parties, candidates, time, card_seq, seqs_type, template):
	if card_seq == 1:
		if (len(candidates) > 0):
			card_num = '1'
			# **해당 변수가 2개 선택됐을 경우 먼저 선택한 변수를 출력, {투표율|득표율}에서는 해당 후보가 참여한 선거의 개표율이 10% 이하일 경우 투표율, 이상일 경우 득표율 출력
			candidate_names = sess.query(CandidateInfo.name).filter(CandidateInfo.huboid.in_(candidates)).first()
			candidate_names = candidate_names[0]
			data = {
				'candidate_names': candidate_names,
				'tooOrget': '득표율' if seqs_type else '투표율',
			}
			text = '당신이 선택한 {candidate_names} 후보가 참여한 선거의 {tooOrget} 현황'.format(**data)
		
		else:
			if len(regions) > 0:
				card_num = '1-1'
				# **해당 변수가 2개 선택됐을 경우 먼저 선택한 변수를 출력 {투표율|득표율}에서는 해당 지역 시도지사 선거의 개표율이 10% 이하일 경우 투표율, 이상일 경우 득표율 출력
				region_nums = []
				for r in regions:
					region_nums.append(regionCodeCheck(r))
			
				region_names = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.sggCityCode.in_(region_nums)).all()

				region_names = list(set(region_names))
				region_join = []
				for r1, r2 in region_names:
					if (r2 == '합계') or (r2 == None):
						region_join.append(r1)
					else:
						region_join.append(r1+ ' ' + r2)

				region_names = region_join[0]
				data = {
					'region_names': region_names,
					'tooOrget': '득표율' if seqs_type else '투표율',
				}
				text = '{region_names} 선거 {tooOrget} 현황'.format(**data)
			else:
				if len(parties) > 0:
					card_num = '1-2'
					# **해당 변수가 2개 선택됐을 경우 먼저 선택한 변수를 출력 {투표율|득표율}에서는 전체 시도지사 선거(17개), 시군구청장 선거(226개)에서 개표율이 10%가 넘는 지역의 수가 전체 선거구의 10%보다 적을 경우(2개, 23개) 투표율, 이상일 경우 득표율 출력
					party_names = sess.query(PartyCode.jdName).filter(PartyCode.pOrder.in_(parties)).first()
					party_names = party_names[0]
					data = {
						'party_names': party_names,
						'tooOrget': '득표율' if seqs_type else '투표율',
					}
					text = '{party_names}의 613 지방선거'.format(**data)
				
				else:
					if len(polls) > 0:
						card_num = '1-3'
						# **해당 변수가 2개 선택됐을 경우 먼저 선택한 변수를 출력 {투표율|득표율}에서는 선택한 선거 종류(시도지사/시군구청장/교육감/국회의원)별 전체 선거구 수의 10% 이상이 개표율 10%를 넘겼을 경우 득표율, 이하일 경우 투표율 출력
						poll_names = sess.query(SgTypecode.sgName).filter(SgTypecode.sgTypecode.in_(polls)).first()
						poll_names = poll_names[0]
						data = {
							'poll_names': poll_names,
							'tooOrget': '득표율' if seqs_type else '투표율',
						}
						text = '현재 {poll_names} {tooOrget} 현황'.format(**data)
					
					else:
						card_num = '1-4'
						text = '당신의 SNU 카드뉴스봇'

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
		if time > datetime.datetime(2018, 6, 13, 18, 59, 59):
			t = 18
		else:
			t = time.hour
		
		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t2 = 23
		else:
			t2 = time.hour

		toorate_avg_nat = sess.query(VoteProgress.tooRate).filter(VoteProgress.timeslot==t, VoteProgress.sido=='전국', VoteProgress.gusigun=='합계').scalar()

		data = {
			'toorate_avg_nat': round(toorate_avg_nat, 2),
		}
		if t2 > 18:
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
		if time > datetime.datetime(2018, 6, 13, 18, 59, 59):
			t = 18
		else:
			t = time.hour

		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t2 = 23
		else:
			t2 = time.hour

		if t in [8,10]:
			raise NoTextError

		past_toorate = sess.query(func.sum(PastVoteProgress.tooTotal) / func.sum(PastVoteProgress.yooTotal) * 100).filter(PastVoteProgress.timeslot==t, PastVoteProgress.gusigun=='합계').group_by(PastVoteProgress.timeslot).scalar()
		
		current_toorate = sess.query(VoteProgress.tooRate).filter(VoteProgress.timeslot==t, VoteProgress.sido=='전국', VoteProgress.gusigun=='합계').scalar()

		current_toorate_past_toorate = current_toorate - past_toorate
		toorate_compare = '높은' if current_toorate_past_toorate > 0 else '낮은'
		# TODO
		ranks =  sess.query(VoteProgress.tooRate, VoteProgress.sido).filter(VoteProgress.timeslot==t, VoteProgress.sido!='전국', VoteProgress.gusigun=='합계').order_by(func.max(VoteProgress.tooRate).desc()).group_by(VoteProgress.sido).all()
	
		toorate_rank1 = ranks[0][1]
		toorate_rank = ', '.join(rank[1] for rank in ranks[1:3])

		data = {
			'past_toorate': round(past_toorate, 2),
			'current_toorate_past_toorate': round(abs(current_toorate_past_toorate), 2),
			'toorate_compare': toorate_compare,
			'toorate_rank1': toorate_rank1,
			'toorate_rank': toorate_rank,
			'josa': josaPick(toorate_rank[-1], '이')
		}

		if t2 > 18:
			card_num = '3'
			text = text_templates[card_num].format(**data)
		else:
			card_num = '3-1'
			text = text_templates[card_num].format(**data)

		map_data = []
		for v, r in ranks:
			map_data.append({'name':r, 'value':float(v)*0.01})
		map_data = list({v['name']:v for v in map_data}.values())

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
		if time > datetime.datetime(2018, 6, 13, 18, 59, 59):
			t = 18
		else:
			t = time.hour

		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t2 = 23
		else:
			t2 = time.hour

		try:
			region_num = regionCodeCheck(regions[index])
			region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.sggCityCode==region_num).first()
		except TypeError:
			raise NoTextError

		if (region2 == '합계') or (region2 == None): # 시도만
			only_sido = True
		else: # 시 + 구시군
			only_sido = False

		toorate_avg_nat = sess.query(VoteProgress.tooRate).filter(VoteProgress.timeslot==t, VoteProgress.sido=='전국', VoteProgress.gusigun=='합계').scalar()

		if only_sido: # 경상남도 None
			toorate_region1 = sess.query(VoteProgress.tooRate).filter(VoteProgress.timeslot==t, VoteProgress.gusigun=='합계', VoteProgress.sido==region1).scalar()
			region_name = region1

		else: # 시 + 구시군
			toorate_region1 = sess.query(func.sum(VoteProgress.tooTotal) / func.sum(VoteProgress.yooTotal) * 100).outerjoin(PrecinctCode4, and_(VoteProgress.sido==PrecinctCode4.sido, VoteProgress.gusigun==PrecinctCode4.sgg)).filter(VoteProgress.timeslot==t, PrecinctCode4.sido==region1, PrecinctCode4.gusigun==region2).scalar()
			region_name = region1 + ' ' + region2
		
		toorate_region1_toorate_avg_nat = toorate_region1 - toorate_avg_nat
		toorate_compare1 = '높은' if toorate_region1_toorate_avg_nat > 0 else '낮은'

		data = {
			'region1': region_name,
			'toorate_region1': round(toorate_region1, 2),
			'toorate_region1_toorate_avg_nat': round(abs(toorate_region1_toorate_avg_nat),2),
			'toorate_compare1': toorate_compare1,
		}

		if t2 > 18:
			card_num = '4'
			text = text_templates[card_num].format(**data)
		else:
			card_num = '4-1'
			text = text_templates[card_num].format(**data)

		toorate_region1_sub = sess.query((func.sum(VoteProgress.tooTotal) / func.sum(VoteProgress.yooTotal) * 100), PrecinctCode4.gusigun).outerjoin(PrecinctCode4, and_(VoteProgress.sido==PrecinctCode4.sido, VoteProgress.gusigun==PrecinctCode4.sgg)).filter(VoteProgress.timeslot==t, VoteProgress.sido==region1, VoteProgress.gusigun!='합계').group_by(VoteProgress.sido, PrecinctCode4.gusigun)

		if region1 == '제주특별자치도':
			toorate_region1_sub = sess.query((func.sum(VoteProgress.tooTotal) / func.sum(VoteProgress.yooTotal) * 100), VoteProgress.gusigun).filter(VoteProgress.timeslot==t, VoteProgress.sido==region1, VoteProgress.gusigun!='합계').group_by(VoteProgress.sido, VoteProgress.gusigun)
		# print(toorate_region1_sub.all())

		map_data = []
		for v, r in toorate_region1_sub:
			map_data.append({'name':r, 'value':float(v) * 0.01})
		map_data = list({v['name']:v for v in map_data}.values())

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
		candidate, candidate_sgg, candidate_sd, candidate_wiw, sgtype = sess.query(CandidateInfo.name, CandidateInfo.sggName, CandidateInfo.sdName, CandidateInfo.wiwName, CandidateInfo.sgTypecode).filter(CandidateInfo.huboid==candidates[index]).first()

		if time > datetime.datetime(2018, 6, 13, 18, 59, 59):
			t = 18
		else:
			t = time.hour
		
		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t2 = 23
		else:
			t2 = time.hour

		if sgtype == 2:
			candidate_region_toorate = sess.query(VoteProgress.tooRate).filter(VoteProgress.timeslot==t, VoteProgress.sido==candidate_sd, VoteProgress.gusigun==candidate_wiw).scalar()
		elif sgtype == 4:
			candidate_region_toorate = sess.query(func.sum(VoteProgress.tooTotal) / func.sum(VoteProgress.yooTotal) * 100).outerjoin(PrecinctCode4, and_(VoteProgress.sido==PrecinctCode4.sido, VoteProgress.gusigun==PrecinctCode4.sgg)).filter(VoteProgress.timeslot==t, PrecinctCode4.sido==candidate_sd, PrecinctCode4.gusigun==candidate_sgg).scalar()
		elif sgtype in [3, 11]:
			candidate_region_toorate = sess.query(VoteProgress.tooRate).filter(VoteProgress.timeslot==t, VoteProgress.sido==candidate_sd, VoteProgress.gusigun=='합계').scalar()

		# if candidate_wiw != None:
		# 	candidate_region_toorate = sess.query(VoteProgress.tooRate).filter(VoteProgress.timeslot==t, VoteProgress.sido==candidate_sd, VoteProgress.gusigun==candidate_sgg).scalar()
		# else:
		# 	candidate_region_toorate = sess.query(VoteProgress.tooRate).filter(VoteProgress.timeslot==t, VoteProgress.sido==candidate_sd, VoteProgress.gusigun=='합계').scalar()
		# print(candidate_region_toorate)

		data = {
			'candidate': candidate,
			'candidate_region': candidate_sd,
			'candidate_region_toorate': float(round(candidate_region_toorate, 2)),
		}

		if t2 > 18:
			card_num = '5'
			text = text_templates[card_num].format(**data)
		else:
			card_num = '5-1'
			data['hour'] = hourConverter(time.hour)
			text = text_templates[card_num].format(**data)

		candidate_region_sub = sess.query((func.sum(VoteProgress.tooTotal) / func.sum(VoteProgress.yooTotal) * 100), PrecinctCode4.gusigun).outerjoin(PrecinctCode4, and_(VoteProgress.sido==PrecinctCode4.sido, VoteProgress.gusigun==PrecinctCode4.sgg)).filter(VoteProgress.gusigun!='합계', VoteProgress.sido==candidate_sd, VoteProgress.timeslot==t).group_by(VoteProgress.sido, PrecinctCode4.gusigun)

		map_data = []
		for v, r in candidate_region_sub:
			map_data.append({'name':r, 'value':float(v) * 0.01})
		map_data = list({v['name']:v for v in map_data}.values())

		meta_card = {
			'order': order,
			'type': 'map',
			'party': 'default',
			'data': {
				'map_data': {
					'area': candidate_sd,
					'party': 'default',
					'data': map_data,
				},
				'text': text,
			},
			'debugging': card_num,
		}
		

	elif card_seq == 6:
		if time > datetime.datetime(2018, 6, 13, 18, 59, 59):
			t = 18
		else:
			t = time.hour
		
		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t2 = 23
		else:
			t2 = time.hour
		
		if t in [8,10]:
			raise NoTextError

		past_toorate = sess.query(func.sum(PastVoteProgress.tooTotal) / func.sum(PastVoteProgress.yooTotal) * 100).filter(PastVoteProgress.timeslot==t, PastVoteProgress.gusigun=='합계').group_by(PastVoteProgress.timeslot).scalar()

		current_toorate = sess.query(VoteProgress.tooRate).filter(VoteProgress.timeslot==t, VoteProgress.sido=='전국', VoteProgress.gusigun=='합계').scalar()

		current_toorate_past_toorate = current_toorate - past_toorate

		past = sess.query(PastVoteProgress.tooRate.label('rate'), PastVoteProgress.gusigun).filter(PastVoteProgress.timeslot==t, PastVoteProgress.gusigun!='합계').group_by(PastVoteProgress.gusigun)
		
		current = sess.query((func.sum(VoteProgress.tooTotal) / func.sum(VoteProgress.yooTotal) * 100).label('rate'), PrecinctCode4.gusigun).outerjoin(PrecinctCode4, and_(VoteProgress.sido==PrecinctCode4.sido, VoteProgress.gusigun==PrecinctCode4.sgg)).filter(VoteProgress.timeslot==t, VoteProgress.gusigun!='합계').group_by(VoteProgress.gusigun)

		currentDf = pd.read_sql(current.statement, current.session.bind)
		pastDf = pd.read_sql(past.statement, past.session.bind)
		currentPastDf = pd.merge(currentDf, pastDf, on='gusigun')

		if t2 > 18:
			card_num = '6' if current_toorate_past_toorate > 0 else '6-0'
			text = text_templates[card_num]
		else:
			ratio = sum([1 for s in (currentPastDf['rate_x'] - currentPastDf['rate_y']).values if s > 0]) / len(currentDf['gusigun'])

			if current_toorate_past_toorate >= 5:
				card_num = '6-1'
			elif current_toorate_past_toorate <= -5:
				card_num = '6-3'
			elif (current_toorate_past_toorate > -5) and (current_toorate_past_toorate < 5):
				card_num = '6-4'
			elif ratio >= 0.8:
				card_num = '6-2'
			else:
				# text = None
				raise NoTextError

			text = text_templates[card_num]

		meta_card = {
			'order': order,
			'type': 'text',
			'party': 'default',
			'data': {
				'background': background_variations[card_num],
				'text': text,
			},
			'debugging': card_num,
		}

	elif card_seq == 7:
		s = sess.query(func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계').group_by(OpenProgress.sido).subquery()

		openrate_avg_nat = sess.query((func.sum(s.c.n_total) + func.sum(s.c.invalid)) / func.sum(s.c.tooTotal) * 100).scalar()

		data = {
			'hour': timeDisplay(time),
			'openrate_avg_nat': round(openrate_avg_nat, 2),
		}
		card_num = '7'
		text = text_templates[card_num].format(**data)

		meta_card = {
			'order': order,
			'type': 'rate',
			'party': 'default',
			'data': {
				'title': timeDisplay(time) + ', 평균 개표율',
				'rate': round(openrate_avg_nat),
				'text': text,
			},
			'debugging': card_num,
		}

	elif card_seq == 8:
		openrate_sunname1_ranks = sess.query(func.max(OpenProgress.openPercent).label('max'), OpenProgress.sido).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계').group_by(OpenProgress.sido).order_by(func.max(OpenProgress.openPercent).desc())
		# [(Decimal('28.97'), '세종특별자치시'), (Decimal('20.36'), '울산광역시'), (Decimal('67.41'), '제주특별자치도'), (Decimal('27.44'), '충청남도'), (Decimal('32.79'), '부산광역시'), (Decimal('22.56'), '대전광역시'), (Decimal('19.89'), '광주광역시'), (Decimal('22.39'), '전라북도'),
		map_data = []
		for v, r in openrate_sunname1_ranks:
			map_data.append({'name':r, 'value':float(v)*0.01})

		map_data = list({v['name']:v for v in map_data}.values())

		try:
			openDf = pd.read_sql(openrate_sunname1_ranks.statement, openrate_sunname1_ranks.session.bind)
		except AttributeError:
			raise NoTextError

		openDf = openDf.sort_values(by='max', ascending=False)
		openDf = openDf.reset_index(drop=True)

		if len(openDf.loc[openDf['max']==100,'sido']):
			open_finished = ', '.join(openDf.loc[openDf['max']==100,'sido'])
			try:
				openrate_sunname1_rank1 = openDf.loc[openDf['max']!=100,].iloc[0]
			except IndexError:
				raise NoTextError
			data = {
				'hour': timeDisplay(time),
				'open_finished': open_finished,
				'openrate_sunname1_rank1': openrate_sunname1_rank1['sido'],
				'openrate_sunname1_rank1_rate': openrate_sunname1_rank1['max'],
			}
			card_num = '8-1'
			text = text_templates[card_num].format(**data)
		else:
			data = {
				'hour': timeDisplay(time),
				'openrate_sunname1_rank1': openDf.loc[0,'sido'],
				'josa1': josaPick(openDf.loc[0,'sido'],'으로'),
				'openrate_sunname1_rank1_rate': round(openDf.loc[0,'max'], 2),
				'openrate_sunname1_rank2': openDf.loc[1,'sido'],
				'josa2': josaPick(openDf.loc[1,'sido'],'가'),
				'openrate_sunname1_rank2_rate': round(openDf.loc[1,'max'], 2),
			}
			card_num = '8'
			text = text_templates[card_num].format(**data)

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
		openrate_sunname2_ranks = sess.query(func.max(OpenProgress.openPercent).label('max'), OpenProgress.sido, OpenProgress.gusigun).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==4, OpenProgress.sggCityCode!=None).group_by(OpenProgress.gusigun).order_by(func.max(OpenProgress.openPercent).desc())
		
		graph_data = []
		for v, r1, r2 in openrate_sunname2_ranks[:10]:
			graph_data.append({'name':r1+' '+r2, 'value':float(v)*0.01})
		# print(graph_data[:10])
		graph_data = list({v['name']:v for v in graph_data}.values())
		
		try:
			openDf = pd.read_sql(openrate_sunname2_ranks.statement, openrate_sunname2_ranks.session.bind)
		except AttributeError:
			raise NoTextError

		openDf = openDf.sort_values(by='max', ascending=False)
		openDf = openDf.reset_index(drop=True)

		if len(openDf.loc[openDf['max']==100,'gusigun']):
			open_finished = ', '.join(openDf.loc[openDf['max']==100,'gusigun'])
			try:
				openrate_sunname2_rank1 = openDf.loc[openDf['max']!=100,].iloc[0]
			except IndexError:
				raise NoTextError
			# print(openrate_sunname2_rank1)
			# openrate_sunname2_rank1 = openrate_sunname2_rank1['sido'] + ' ' + openrate_sunname2_rank1['gusigun']
			data = {
				'hour': timeDisplay(time),
				'open_finished': open_finished,
				'openrate_sunname2_rank1': openrate_sunname2_rank1['gusigun'],
				'josa': josaPick(openrate_sunname2_rank1['gusigun'], '이'),
				'openrate_sunname2_rank1_rate': openrate_sunname2_rank1['max'],
			}
			card_num = '9-1'
			text = text_templates[card_num].format(**data)
		else:
			openrate_sunname2_rank1 = openDf.loc[0,'sido'] + ' ' + openDf.loc[0,'gusigun']
			openrate_sunname2_rank2 = openDf.loc[1,'sido'] + ' ' + openDf.loc[1,'gusigun']

			data = {
				'hour': timeDisplay(time),
				'openrate_sunname2_rank1': openrate_sunname2_rank1,
				'josa1': josaPick(openrate_sunname2_rank1, '이'),
				'openrate_sunname2_rank1_rate': round(openDf.loc[0,'max'], 2),
				'openrate_sunname2_rank2': openrate_sunname2_rank2,
				'josa2': josaPick(openrate_sunname2_rank2, '이'),
				'openrate_sunname2_rank2_rate': round(openDf.loc[1,'max'], 2),
			}
			card_num = '9'
			text = text_templates[card_num].format(**data)

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
		region_num = regionCodeCheck(regions[index])
		try:
			region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.sggCityCode==region_num).first()
		except TypeError:
			raise NoTextError

		if (region2 == '합계') or (region2 == None): # 시도만
			only_sido = True
		else: # 시 + 구시군
			only_sido = False

		if only_sido:
			openrate_region1 = sess.query(func.max(OpenProgress.openPercent).label('max'), OpenProgress.sido).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.sido==region1, OpenProgress.gusigun=='합계').scalar()
	
			region_name = region1
			# print(region_name, openrate_region1)
		else: # 시+도 : 도의 결과
			# TODO 시 + 도의 개표율
			# openrate_region1 = sess.query(((func.sum(OpenProgress.tooTotal)+func.sum(OpenProgress.invalid)) / func.sum(OpenProgress.yooTotal) * 100).label('rate')).outerjoin(PrecinctCode4, and_(OpenProgress.sido==PrecinctCode4.sido, OpenProgress.gusigun==PrecinctCode4.sgg)).filter(OpenProgress.datatime<=time, PrecinctCode4.gusigun!='합계', OpenProgress.sido==region1, PrecinctCode4.gusigun==region2).group_by(OpenProgress.sido).scalar()
			openrate_region1 = sess.query(func.max(OpenProgress.openPercent).label('max'), OpenProgress.sido).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.sido==region1, OpenProgress.gusigun==region2).scalar()
		
			region_name = region1 + ' ' + region2
			# print(region_name, openrate_region1)
			
		data = {
			'hour': timeDisplay(time),
			'region1': region_name,
			'josa1': josaPick(region_name, '은')
		}
		# print("page10", openrate_region1)
		if openrate_region1 == 0:
			card_num = '10-1'
			text = text_templates[card_num].format(**data)
			meta_card = {
				'order': order,
				'type': 'rate',
				'party': 'default',
				'data': {
					'title': region_name + ' 개표 준비중',
					'rate': 0,
					'text': text,
				},
				'debugging': card_num,
			}
		elif openrate_region1 >= 100:
			card_num = '10-2'
			text = text_templates[card_num].format(**data)
			meta_card = {
				'order': order,
				'type': 'rate',
				'party': 'default',
				'data': {
					'title': region_name + ' 개표 완료',
					'rate': 100,
					'text': text,
				},
				'debugging': card_num,
			}
		else:
			# openrate_avg_nat = sess.query((func.sum(OpenProgress.n_total)+func.sum(OpenProgress.invalid))/ func.sum(OpenProgress.tooTotal)*100).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계').group_by(OpenProgress.electionCode).scalar()
			s = sess.query(func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계').group_by(OpenProgress.sido).subquery()

			openrate_avg_nat = sess.query((func.sum(s.c.n_total) + func.sum(s.c.invalid)) / func.sum(s.c.tooTotal) * 100).scalar()

			openrate_region1_openrate_avg_nat = openrate_region1 - openrate_avg_nat
			compare_region1 = '높은' if openrate_region1_openrate_avg_nat > 0 else '낮은'

			data['openrate_region1'] = round(openrate_region1, 2)
			data['openrate_region1_openrate_avg_nat'] = round(abs(openrate_region1_openrate_avg_nat), 2)
			data['compare_region1'] = compare_region1

			card_num = '10'
			text = text_templates[card_num].format(**data)
			# 시 + 도 개표율의 각 
			# sub_r = sess.query(((func.sum(OpenProgress.tooTotal)+func.sum(OpenProgress.invalid)) / func.sum(OpenProgress.yooTotal) * 100).label('rate'), PrecinctCode4.sido, PrecinctCode4.gusigun).outerjoin(PrecinctCode4, and_(OpenProgress.sido==PrecinctCode4.sido, OpenProgress.gusigun==PrecinctCode4.sgg)).filter(OpenProgress.datatime<=time, PrecinctCode4.gusigun!='합계', OpenProgress.sido==region1).group_by(OpenProgress.sido, PrecinctCode4.gusigun)
			sub_r = sess.query(func.max(OpenProgress.openPercent).label('rate'), PrecinctCode4.sido, PrecinctCode4.gusigun).outerjoin(PrecinctCode4, and_(OpenProgress.sido==PrecinctCode4.sido, OpenProgress.gusigun==PrecinctCode4.sgg)).filter(OpenProgress.electionCode==3, OpenProgress.datatime<=time, PrecinctCode4.gusigun!='합계', OpenProgress.sido==region1).group_by(OpenProgress.sido, PrecinctCode4.gusigun)

			if region1 == '제주특별자치도':
				sub_r = sess.query(func.max(OpenProgress.openPercent).label('rate'), OpenProgress.sido, OpenProgress.gusigun).filter(OpenProgress.electionCode==3, OpenProgress.datatime<=time, OpenProgress.gusigun!='합계', OpenProgress.sido==region1).group_by(OpenProgress.sido, OpenProgress.gusigun)
			# print(sub_r.all())


			map_data = []
			for v, _, r in sub_r:
				map_data.append({'name':r, 'value':float(v) * 0.01})
			map_data = list({v['name']:v for v in map_data}.values())

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
		if polls[index] == 2: # 국회의원
			poll, poll_num_sunname = sess.query(SgTypecode.sgName, func.count(PrecinctCode.sgg)).join(PrecinctCode, PrecinctCode.electionCode==SgTypecode.sgTypecode).filter(SgTypecode.sgTypecode==polls[index]).first()

			# s = sess.query(OpenProgress.sido, OpenProgress.sgg, func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==2, OpenProgress.sggCityCode!=None).group_by(OpenProgress.sgg)
			subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxdate')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==2, OpenProgress.sggCityCode!=None).group_by(OpenProgress.sgg).subquery()

			s = sess.query(OpenProgress.sido, OpenProgress.gusigun, OpenProgress.n_total, OpenProgress.invalid, OpenProgress.tooTotal).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxdate))
			
			
		elif polls[index] == 3:
			poll, poll_num_sunname = sess.query(SgTypecode.sgName, func.count(PrecinctCode.cityCode)).join(PrecinctCode, PrecinctCode.electionCode==SgTypecode.sgTypecode).filter(SgTypecode.sgTypecode==polls[index]).first()

			# s = sess.query(OpenProgress.sido, OpenProgress.gusigun, func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계').group_by(OpenProgress.sido)

			subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxdate')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계').group_by(OpenProgress.sido).subquery()

			s = sess.query(OpenProgress.sido, OpenProgress.gusigun, OpenProgress.n_total, OpenProgress.invalid, OpenProgress.tooTotal).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxdate))

		elif polls[index] == 4:
			poll, poll_num_sunname = sess.query(SgTypecode.sgName, func.count(PrecinctCode.gusigun)).join(PrecinctCode, PrecinctCode.electionCode==SgTypecode.sgTypecode).filter(SgTypecode.sgTypecode==polls[index]).first()

			# s = sess.query(OpenProgress.sido, OpenProgress.gusigun, func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==4, OpenProgress.sggCityCode!=None).group_by(OpenProgress.gusigun)
			subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxdate')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==4, OpenProgress.sggCityCode!=None).group_by(OpenProgress.gusigun).subquery()

			s = sess.query(OpenProgress.sido, OpenProgress.gusigun, OpenProgress.n_total, OpenProgress.invalid, OpenProgress.tooTotal).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxdate))

		elif polls[index] == 11:
			poll, poll_num_sunname = sess.query(SgTypecode.sgName, func.count(PrecinctCode.cityCode)).join(PrecinctCode, PrecinctCode.electionCode==SgTypecode.sgTypecode).filter(SgTypecode.sgTypecode==polls[index]).first()

			# s = sess.query(OpenProgress.sido, OpenProgress.gusigun, func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==11, OpenProgress.gusigun=='합계').group_by(OpenProgress.sido)
			subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxdate')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==11, OpenProgress.gusigun=='합계').group_by(OpenProgress.sido).subquery()

			s = sess.query(OpenProgress.sido, OpenProgress.gusigun, OpenProgress.n_total, OpenProgress.invalid, OpenProgress.tooTotal).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxdate))
		
		# else:
		# 	poll, poll_num_sunname = sess.query(SgTypecode.sgName, func.count(PrecinctCode.cityCode)).join(PrecinctCode, PrecinctCode.electionCode==SgTypecode.sgTypecode).filter(SgTypecode.sgTypecode==polls[index]).first()
		# 	s = sess.query(OpenProgress.sido, OpenProgress.gusigun, func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==11, OpenProgress.gusigun=='합계').group_by(OpenProgress.sido)
		
		poll_openrate_nat_avg = sess.query((func.sum(s.subquery().c.n_total) + func.sum(s.subquery().c.invalid)) / func.sum(s.subquery().c.tooTotal) * 100).scalar()

		poll_openrate_ranks = []
		
		for r1, r2, n_total, invalid, tooTotal in s:
			if invalid == None:
				invalid = 0
			if r2 == '합계':
				r = r1
			else:
				r = r1 + ' ' + r2
			v = (n_total + invalid) / tooTotal
			poll_openrate_ranks.append({'name':r, 'value':v})
		
		poll_openrate_ranks = list({v['name']:v for v in poll_openrate_ranks}.values())
		poll_openrate_ranks = sorted(poll_openrate_ranks, key=lambda x: x['value'], reverse=True)
		# print("11", poll_openrate_ranks)
		if poll_openrate_nat_avg >= 100:
			data = {
				'hour': timeDisplay(time),
				'poll': poll,
			}
			card_num = '11-2'
			text = text_templates[card_num].format(**data)
			meta_card = {
				'order': order,
				'type': 'rate',
				'party': 'default',
				'data': {
					'title': poll + ', 개표 완료',
					'rate': 100,
					'text': text,
				},
				'debugging': card_num,
			}
		elif (poll_openrate_nat_avg < 100) and (poll_openrate_nat_avg > 0):
			try:
				d = poll_openrate_ranks[1]['name']
			except TypeError:
				raise NoTextError
			data = {
				'poll_num_sunname': poll_num_sunname,
				'poll': poll,
				'poll_openrate_rank1': poll_openrate_ranks[0]['name'],
				'poll_openrate_rank1_rate': round(poll_openrate_ranks[0]['value'] * 100, 2),
				'poll_openrate_rank2': poll_openrate_ranks[1]['name'],
				'poll_openrate_rank2_rate': round(poll_openrate_ranks[1]['value'] * 100, 2),
				'poll': poll, 
				'poll_openrate_nat_avg': round(poll_openrate_nat_avg, 2),
			}
			card_num = '11'
			text = text_templates[card_num].format(**data)
			
			meta_card = {
				'order': order,
				'type': 'graph',
				'party': 'default',
				'data': {
					'graph_data': {
						'type': 'region',
						'data': poll_openrate_ranks[:10],
					},
					'text': text,
				}, 
				'debugging': card_num,
			}
		else:
			data = {
				'hour': timeDisplay(time),
				'poll': poll,
				'josa': josaPick(poll, '은'),
			}
			card_num = '11-1'
			text = text_templates[card_num].format(**data)
			meta_card = {
				'order': order,
				'type': 'rate',
				'party': 'default',
				'data': {
					'title': poll + ' 개표 준비중',
					'rate': 0,
					'text': text,
				},
				'debugging': card_num,
			}
		

	elif card_seq == 12:
		candidate, candidate_sggName, candidate_sdName, candidate_wiwName, candidate_poll_code = sess.query(CandidateInfo.name, CandidateInfo.sggName, CandidateInfo.sdName, CandidateInfo.wiwName, CandidateInfo.sgTypecode).filter(CandidateInfo.huboid==candidates[index]).first()

		candidate_poll = regionPoll(candidate_sggName, candidate_poll_code)
	
		if candidate_poll_code == 2: # 국회의원
			s = sess.query(OpenProgress.sgg, func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==2, OpenProgress.sggCityCode!=None, OpenProgress.sgg==candidate_sggName).group_by(OpenProgress.sgg)
		
		elif candidate_poll_code == 4:
			s = sess.query(OpenProgress.gusigun, func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==4, OpenProgress.sggCityCode!=None, OpenProgress.sido==candidate_sdName, OpenProgress.gusigun==candidate_sggName).group_by(OpenProgress.gusigun)

		elif candidate_poll_code == 3:
			s = sess.query(OpenProgress.sido, func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계', OpenProgress.sido==candidate_sdName).group_by(OpenProgress.sido)

		elif candidate_poll_code == 11:
			s = sess.query(OpenProgress.sido, func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==11, OpenProgress.gusigun=='합계', OpenProgress.sido==candidate_sdName).group_by(OpenProgress.sido)
		# print(s.all())
		candidate_poll_openrate = sess.query((func.sum(s.subquery().c.n_total) + func.sum(s.subquery().c.invalid)) / func.sum(s.subquery().c.tooTotal) * 100).scalar()

		# try:
		if candidate_poll_code in [2,4]:
			candidate_region_name = candidate_sdName + ' ' + candidate_sggName
		# except TypeError:
		else:
			candidate_region_name = candidate_sdName

		# print(candidate_poll_openrate)
		data = {
			'candidate': candidate,
			'candidate_region': candidate_region_name,
			'candidate_poll': candidate_poll,
			'candidate_poll_openrate': float(round(candidate_poll_openrate, 2)),
		}
		# print(candidate_region_name)
		# print(candidate_poll)
		if candidate_poll_openrate == None:
			card_num = '12-1'	
			text = text_templates[card_num].format(**data)
			meta_card = {
				'order': order,
				'type': 'rate',
				'party': 'default',
				'data': {
					'title': candidate_region_name + ' 지역의 ' + candidate_poll + ' 선거 개표 준비중',
					'rate': 0,
					'text': text,
				},
				'debugging': card_num,
			}		
		elif candidate_poll_openrate >= 100:
			card_num = '12-2'
			text = text_templates[card_num].format(**data)
			meta_card = {
				'order': order,
				'type': 'rate',
				'party': 'default',
				'data': {
					'title': candidate_region_name + ' 지역의 ' + candidate_poll + ' 선거 개표 완료',
					'rate': 100,
					'text': text,
				},
				'debugging': card_num,
			}
		else:
			card_num = '12'
			text = text_templates[card_num].format(**data)
			meta_card = {
				'order': order,
				'type': 'rate',
				'party': 'default',
				'data': {
					'title': candidate_region_name + ' 지역의 ' + candidate_poll + ' 선거 개표율',
					'rate': float(round(candidate_poll_openrate)),
					'text': text,
				},
				'debugging': card_num,
			}
		

	elif card_seq == 13:
		# TODO 9 similar
		s = sess.query(func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계').group_by(OpenProgress.sido).subquery()

		openrate_avg_nat = sess.query((func.sum(s.c.n_total) + func.sum(s.c.invalid)) / func.sum(s.c.tooTotal) * 100).scalar()

		if openrate_avg_nat < 100:
			openrate_sido = sess.query(OpenProgress.sido).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계', OpenProgress.openPercent==100).group_by(OpenProgress.sido).order_by(OpenProgress.datatime.asc()).all()
			if len(openrate_sido) > 0:
				data = {
					'hour': timeDisplay(time),
					'open_finished_sido': ', '.join(sido[0] for sido in openrate_sido[:5]),
				}
				card_num = '13'
				text = text_templates[card_num].format(**data)
			else:
				text = ''

			openrate_gusigun = sess.query(OpenProgress.gusigun).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==4, OpenProgress.sggCityCode!=None, OpenProgress.openPercent==100).group_by(OpenProgress.gusigun).order_by(OpenProgress.datatime.asc()).all()

			if len(openrate_gusigun) > 0:
				data = {
					'hour': timeDisplay(time),
					'open_finished_gusigun': ', '.join(gusigun[0] for gusigun in openrate_gusigun[:5]),
				}
				card_num = '13-1'
				if text:
					gusigun_text = text_templates[card_num].format(**data)
					gusigun_text = gusigun_text.rsplit('현재',1)[1]
				else: # nothing
					gusigun_text = text_templates[card_num].format(**data)
				text += gusigun_text
			else:
				text += ''
			
			if text == '':
				raise NoTextError
			else:
				meta_card = {
					'order': order,
					'type': 'rate',
					'party': 'default',
					'data': {
						'title': '개표 완료 지역',
						'rate': round(openrate_avg_nat),
						'text': text,
					},
					'debugging': card_num,
				}	
		else:
			raise NoTextError


	elif card_seq == 15:
		try:
			poll_code = sess.query(CandidateInfo.sgTypecode).filter(CandidateInfo.huboid==candidates[index]).first()[0]
		except IndexError:
			try:
				poll_code = polls[index]
			except IndexError:
				raise NoTextError

		if len(regions) == 0:
			openrate_rank1_region = None
			if poll_code == 3: # 시도지사
				subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sido).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계').subquery()
		
			elif poll_code == 4: # 시군구청장
				subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sggCityCode).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==4, OpenProgress.sggCityCode!=None).subquery()

			elif poll_code == 2: # 국회의원
				subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sggCityCode).filter(OpenProgress.datatime<=time,OpenProgress.electionCode==2, OpenProgress.sggCityCode!=None).subquery()

			elif poll_code == 11: # 교육감			
				subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sido).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==11, OpenProgress.gusigun=='합계').subquery()

			# else: 
			# 	sub_ranks = None

			sub_ranks = sess.query(OpenProgress).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxtime))

			if sub_ranks == None:
				raise NoTextError

			ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
			ranksDf = ranksDf.sort_values(by=['openPercent', 'n_total'], ascending=False)
			ranksDf = ranksDf.reset_index(drop=True)

			openrate_rank1_region = ranksDf.loc[0,'sido']
			openrate_rank2_region = ranksDf.loc[1,'sido']
			# print(r)
			if openrate_rank1_region == None:
				raise NoTextError

			ranks_vote = ranksDf.filter(regex="n*_percent")
			ranks_ttl = []
			for i, ranks in ranks_vote.iterrows():
				ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])
			ranking = []
			for idx, ranks in enumerate(ranks_ttl):
				for i, r in enumerate(ranks):
					if ranksDf.loc[idx, r+'_name'] != None:
						ranking.append({
							'idx': idx,
							'rank': i,
							'jdName':ranksDf.loc[idx, r+'_jdName'],
							'name': ranksDf.loc[idx, r+'_name'],
							'percent': ranksDf.loc[idx, r+'_percent'],
							})
			rank1_count = Counter([r['jdName'] for r in ranking if r['rank']==0]).most_common()
			rank1_party = rank1_count[0][0]
			rank1_party_num = rank1_count[0][1]
			ranks_party = ', '.join(r[0] for r in rank1_count[1:3] if r[0] != None)
			# print(ranking)
			# try:
			openrate_rank1_region_candidate = [r['name'] for r in ranking if (r['idx']==0) and (r['rank']==0)][0]
			openrate_rank2_region_candidate = [r['name'] for r in ranking if (r['idx']==1) and (r['rank']==0)][0]
			# except IndexError:
			# 	raise NoTextError

			data = {
				'hour': timeDisplay(time),
				'rank1_party': rank1_party, 
				'josa1': josaPick(rank1_party, '이'),
				'rank1_party_num': rank1_party_num,
				'ranks_party': ranks_party,
				'josa2': josaPick(ranks_party, '이'),
				'openrate_rank1_region': openrate_rank1_region,
				'openrate_rank1_region_candidate': openrate_rank1_region_candidate, 
				'openrate_rank2_region': openrate_rank2_region,
				'openrate_rank2_region_candidate': openrate_rank2_region_candidate,
			}

			if poll_code == 11:
				card_num = '15-11'
				# {'hour': '오전 9시 0분', 'rank1_party': None, 'josa1': '이(가)', 'rank1_party_num': 17, 'ranks_party': '', 'josa2': '이(가)', 'openrate_rank1_region': '경기도', 'openrate_rank1_region_candidate': '이재정', 'openrate_rank2_region_candidate': '임해규'}
				text = text_templates[card_num].format(**data)
				meta_card = {
					'order': order,
					'type': 'rank2',
					'party': 'default',
					'data': {
						'title': openrate_rank1_region + ' 교육감 선거 개표 1·2위',
						'rank1': openrate_rank1_region_candidate,
						'rank2': openrate_rank2_region_candidate,
						'text': text,
					},
					'debugging': card_num,
				}
			else:
				card_num = '15-' + str(poll_code)
				text = text_templates[card_num].format(**data)

				meta_card = {
					'order': order,
					'type': 'rank2',
					'party': rank1_party,
					'data': {
						'title': sess.query(SgTypecode.sgName).filter(SgTypecode.sgTypecode==poll_code).scalar() + ' 개표 1·2위',
						'rank1': rank1_party,
						'rank2': rank1_count[1][0],
						'text': text,
					},
					'debugging': card_num,
				}

		else: # 지역선택이 있으면, 선거선택이 없으면
			if poll_code == 3:
				subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sido).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계').subquery()

				sub_ranks = sess.query(OpenProgress).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxtime))

				ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
				ranksDf = ranksDf.reset_index(drop=True)
				
				if len(ranksDf) == 0:
					raise NoTextError

				ranks_vote = ranksDf.filter(regex="n*_percent")	
				ranks_ttl = []
				for i, ranks in ranks_vote.iterrows():
					ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])
				# 각 group 마다 랭킹 만들기
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
				rank1_party = rank1_count[0][0]
				rank1_party_num = rank1_count[0][1]

				data = {
					'hour': timeDisplay(time),
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
						'title': '시도지사 선거 개표 1위',
						'name': rank1_party,
						'text': text,
					},
					'debugging': card_num,
				}
			else:
				raise NoTextError

	elif card_seq == 16:
		region_num = regionCodeCheck(regions[index])
		try:
			region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.sggCityCode==region_num).first()
		except TypeError:
			raise NoTextError

		if (region2 == '합계') or (region2 == None): # 시도만
			only_sido = True
		else: # 시 + 구시군
			only_sido = False
		
		if only_sido:
			region1_poll = regionPoll(region1, 3)

			region1_openrate = sess.query(func.max(OpenProgress.openPercent).label('max'), OpenProgress.sido).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.sido==region1, OpenProgress.gusigun=='합계').scalar()

			subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sido).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.sido==region1, OpenProgress.gusigun=='합계').subquery()


			region_name = region1
		
		else:
			region1_poll = regionPoll(region2, 4)

			subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sggCityCode).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==4, OpenProgress.sido==region1, OpenProgress.gusigun==region2, OpenProgress.sggCityCode!=None).subquery()

			region1_openrate = sess.query(OpenProgress.openPercent).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxtime)).scalar()

			region_name = region1 + ' ' + region2

		sub_ranks = sess.query(OpenProgress).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxtime))

		if sub_ranks == None:
			raise NoTextError

		ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
		ranksDf = ranksDf.reset_index(drop=True)
		if len(ranksDf) == 0:
			raise NoTextError

		ranks_vote = ranksDf.filter(regex="n*_percent")	
		ranks_ttl = [] # one line
		for i, ranks in ranks_vote.iterrows():
			ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])
		ranking = []
		for idx, ranks in enumerate(ranks_ttl):
			for i, r in enumerate(ranks):
				if ranksDf.loc[idx, r+'_jdName'] != None:
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
			'hour': timeDisplay(time),
			'region1': region_name,
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
		# print(ranking)
		for r in ranking:
			graph_data.append({
				'name': r['name'],
				'party': r['jdName'],
				'value': float(r['percent']) * 0.01,
			})
		# print(graph_data)
		graph_data = list({v['name']:v for v in graph_data}.values())

		meta_card = {
			'order': order,
			'type': 'graph',
			'party': region1_rank1_party,
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
		candidate, candidate_sggName, candidate_sdName, candidate_wiwName, candidate_poll_code = sess.query(CandidateInfo.name, CandidateInfo.sggName, CandidateInfo.sdName, CandidateInfo.wiwName, CandidateInfo.sgTypecode).filter(CandidateInfo.huboid==candidates[index]).first()

		candidate_poll = regionPoll(candidate_sggName, candidate_poll_code)
		# print(candidate_poll)
		# candidate_poll table 선택
		if candidate_poll_code == 2:
			s = sess.query(OpenProgress.sgg, func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==2, OpenProgress.sggCityCode!=None, OpenProgress.sgg==candidate_sggName).group_by(OpenProgress.sgg)

			subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sggCityCode).filter(OpenProgress.datatime<=time,OpenProgress.electionCode==2, OpenProgress.sgg==candidate_sggName, OpenProgress.sggCityCode!=None).subquery()

		elif candidate_poll_code == 3:
			s = sess.query(OpenProgress.sido, func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계', OpenProgress.sido==candidate_sdName).group_by(OpenProgress.sido)

			subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sido).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.sido==candidate_sdName, OpenProgress.gusigun=='합계').subquery()

		elif candidate_poll_code == 4:
			s = sess.query(OpenProgress.gusigun, func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==4, OpenProgress.sggCityCode!=None, OpenProgress.sido==candidate_sdName, OpenProgress.gusigun==candidate_sggName).group_by(OpenProgress.gusigun)
			
			subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sggCityCode).filter(OpenProgress.datatime<=time, OpenProgress.sido==candidate_sdName, OpenProgress.gusigun==candidate_sggName, OpenProgress.electionCode==4, OpenProgress.sggCityCode!=None).subquery()

		elif candidate_poll_code == 11:
			s = sess.query(OpenProgress.sido, func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==11, OpenProgress.gusigun=='합계', OpenProgress.sido==candidate_sdName).group_by(OpenProgress.sido)

			subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sido).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==11, OpenProgress.sido==candidate_sdName, OpenProgress.gusigun=='합계').subquery()


		candidate_poll_openrate = sess.query((func.sum(s.subquery().c.n_total) + func.sum(s.subquery().c.invalid)) / func.sum(s.subquery().c.tooTotal) * 100).scalar()
		
		sub_ranks = sess.query(OpenProgress).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxtime))

		if sub_ranks == None:
			raise NoTextError

		ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
		ranksDf = ranksDf.reset_index(drop=True)

		if len(ranksDf) == 0:
			raise NoTextError
		ranks_vote = ranksDf.filter(regex="n*_percent")
		ranks_ttl = []
		for i, ranks in ranks_vote.iterrows():
			ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])
		ranking = []
		for idx, ranks in enumerate(ranks_ttl):
			for i, r in enumerate(ranks):
				if ranksDf.loc[idx, r+'_name'] != None:
					ranking.append({
						'jdName':ranksDf.loc[idx, r+'_jdName'],
						'name': ranksDf.loc[idx, r+'_name'],
						'percent': ranksDf.loc[idx, r+'_percent'],
						'vote': ranksDf.loc[idx, r+'_vote'],
					})
		# print(ranking)
		try:
			candidate_rate = [r['percent'] for r in ranking if r['name']==candidate][0]
			candidate_poll_rank1_party = ranking[0]['jdName']
			candidate_poll_rank1_name = ranking[0]['name']
			candidate_poll_rank1_rate = ranking[0]['percent']

			candidate_poll_rank2_party = ranking[1]['jdName']
			candidate_poll_rank2_name = ranking[1]['name']
			candidate_poll_rank2_rate = ranking[1]['percent']
		except IndexError:
			raise NoTextError

		data = {
			'hour': timeDisplay(time),
			'candidate': candidate,
			'candidate_rate': candidate_rate,
			'candidate_region': candidate_sggName,
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
		open_finished = True if candidate_poll_openrate >= 100 else False
		if candidate_poll_rank1_name == candidate: 
			if (candidate_poll_rank1_rate - candidate_poll_rank2_rate) >= 15:
				if open_finished:
					card_num = '17-6'
				else:
					card_num = '17-3'
			elif (candidate_poll_rank1_rate - candidate_poll_rank2_rate) < 5:
				if open_finished:
					card_num = '17-6'
				else:
					card_num = '17-1'
			elif confirm or open_finished:
				card_num = '17-6'
			else:
				if open_finished:
					card_num = '17-6'
				else:
					card_num = '17'

		elif candidate_poll_rank2_name == candidate:
			if abs(candidate_poll_rank1_rate - candidate_poll_rank2_rate) >= 15:
				if open_finished:
					card_num = '17-7'
				else:
					card_num = '17-4'
			elif abs(candidate_poll_rank1_rate - candidate_poll_rank2_rate) < 5:
				if open_finished:
					card_num = '17-7'
				else:
					card_num = '17-2'
			elif confirm or open_finished:
				card_num = '17-7'
			else:
				if open_finished:
					card_num = '17-7'
				else:
					card_num = '17'

		else:
			if abs(candidate_poll_rank1_rate - candidate_poll_rank2_rate) < 5:
				if open_finished:
					card_num = '17-7'
				else:
					card_num = '17-5'
			else:
				if open_finished:
					card_num = '17-7'
				else:
					card_num = '17'
		
		text = text_templates[card_num].format(**data)
		
		graph_data = []
		# print(ranking)
		for r in ranking:
			graph_data.append({
				'name': r['name'],
				'party': r['jdName'],
				'value': float(r['percent']) * 0.01,
			})
		# print(graph_data)
		graph_data = list({v['name']:v for v in graph_data}.values())

		meta_card = {
			'order': order,
			'type': 'graph',
			'party': ranking[0]['jdName'],
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
		subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sido).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계').subquery()

		sub_ranks = sess.query(OpenProgress).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxtime))

		if sub_ranks == None:
			raise NoTextError

		ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
		ranksDf = ranksDf.reset_index(drop=True)
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
		

	elif card_seq == 19:
		# TODO: sub with time
		if polls[index] == 2:
			sub = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sgg).filter(OpenProgress.datatime<=time,OpenProgress.electionCode==2, OpenProgress.sggCityCode!=None)

		elif polls[index] == 3:
			sub = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sido).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계')
		
		elif polls[index] == 4:
			sub = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.gusigun).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==4, OpenProgress.sggCityCode!=None)
		
		elif polls[index] == 11:
			sub = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sido).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==11, OpenProgress.gusigun=='합계')

		if polls[index] in [2,3,4]:
			if sub == None:
				raise NoTextError

			ranksDf = pd.read_sql(sub.statement, sub.session.bind)
			ranksDf = ranksDf.reset_index(drop=True)
			if len(ranksDf) == 0:
				raise NoTextError

			ranks_vote = ranksDf.filter(regex="n*_percent")

			ranks_ttl = [] # 각 지역 - 순위
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
							'vote': ranksDf.loc[idx, r+'_vote'],
							})
			rank1_count = Counter([r['jdName'] for r in ranking if r['rank']==0]).most_common()
			# print(rank1_count)
			try:
				rank1_party = rank1_count[0][0] # (key, count)
				rank1_party_num = rank1_count[0][1]
				rank2_party = rank1_count[1][0]
				rank2_party_num = rank1_count[1][1]
			except IndexError:
				raise NoTextError

			confirms = []
			for idx, rank in enumerate(ranks_ttl):
				rank1_cnt = ranksDf.loc[idx, rank[0]+'_vote']
				rank2_cnt = ranksDf.loc[idx, rank[1]+'_vote']
				yet_cnt = ranksDf.loc[idx, 'tooTotal'] - ranksDf.loc[idx, 'n_total'] - ranksDf.loc[idx, 'invalid']
				confirm = 1 if (rank1_cnt-rank2_cnt) > yet_cnt else 0
				if confirm:
					confirms.append(ranksDf.loc[idx, rank[0]+'_jdName'])
			confirms_count = Counter(confirms).most_common()

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
				'hour': timeDisplay(time),
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
			}

		else: # 11 type
			if sub == None:
				raise NoTextError

			ranksDf = pd.read_sql(sub.statement, sub.session.bind)
			if len(ranksDf) == 0:
				raise NoTextError

			ranksDf = ranksDf.sort_values(by='openPercent', ascending=False)
			ranksDf = ranksDf.reset_index(drop=True)
			ranks_vote = ranksDf.filter(regex="n*_percent")

			ranks_ttl = []
			for i, ranks in ranks_vote.iterrows(): # 가로 등수, 세로 지역수: 지역끼리
				ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])
			
			ranking = []
			for idx, ranks in enumerate(ranks_ttl):
				for i, r in enumerate(ranks):
					if ranksDf.loc[idx, r+'_jdName'] != None:
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
				'hour': timeDisplay(time),
				'open_rank1_region': open_rank1_region,
				'open_rank1_region_candidate': open_rank1_region_candidate,
				'open_rank2': open_rank2,
				'confirms_open_rank1_region': confirms_open_rank1_region, 
				'confirms_open_rank1_region_candidate': confirms_open_rank1_region_candidate,
				'confirms_open_ranks': confirms_open_ranks,
			}	
			
		compare_data = []
		for r in rank1_count:
			compare_data.append({
				'party': r[0],
				'value': r[1],
				'unit': '개',
			})
			
		if polls[index] == 2:
			if (abs(rank1_party_num-rank2_party_num) / len(ranking) < 0.05):
				card_num = '19-4'
				text = text_templates[card_num].format(**data)
				meta_card = {
					'order': order,
					'type': 'rank2',
					'party': rank1_party,
					'data': {
						'title': '국회의원 선거 개표 1·2위',
						'rank1': rank1_party,
						'rank2': rank2_party,
						'text': text,
					},
					'debugging': card_num,
				}
			elif (abs(rank1_party_num-rank2_party_num) / len(ranking) > 0.15):
				card_num = '19-7'
				text = text_templates[card_num].format(**data)
				meta_card = {
					'order': order,
					'type': 'compare',
					'party': rank1_party,
					'data': {
						'compare_data': {
							'type': 'party',
							'data': compare_data,
						},
						'text': text,
					},
					'debugging': card_num,
				}
			elif (confirms_rank1_party_num + confirms_rank2_party_num) > 2:
				card_num = '19-14'
				text = text_templates[card_num].format(**data)
				meta_card = {
					'order': order,
					'type': 'win1',
					'party': confirms_rank1_party,
					'data': {
						'win_data': {
							'name': '국회의원 선거',
							'value': confirms_rank1_party_num,
							'total': 6,
						},
						'text': text,
						'title': confirms_rank1_party + ', 국회의원 선거',
					},
					'debugging': card_num,
				}
			else:
				card_num = '19'
				text = text_templates[card_num].format(**data)
				meta_card = {
					'order': order,
					'type': 'rank2',
					'party': rank1_party,
					'data': {
						'rank1':rank1_party,
						'rank2':rank2_party,
						'text': text,
						'title': '국회의원 선거 개표 1·2위',
					},
					'debugging': card_num,
				}
			
		elif polls[index] == 3:
			if (abs(rank1_party_num-rank2_party_num) / len(ranking) < 0.05):
				card_num = '19-5'
				text = text_templates[card_num].format(**data)
				meta_card = {
					'order': order,
					'type': 'compare',
					'party': rank1_party,
					'data': {
						'compare_data': {
							'type': 'party',
							'data': compare_data,
						},
						'text': text,
					},
					'debugging': card_num,
				}
			elif (abs(rank1_party_num-rank2_party_num) / len(ranking) > 0.15):
				card_num = '19-8'
				text = text_templates[card_num].format(**data)
				meta_card = {
					'order': order,
					'type': 'compare',
					'party': rank1_party,
					'data': {
						'compare_data': {
							'type': 'party',
							'data': compare_data,
						},
						'text': text,
					},
					'debugging': card_num,
				}
			elif (confirms_rank1_party_num + confirms_rank2_party_num) > 2:
				card_num = '19-15'
				text = text_templates[card_num].format(**data)
				meta_card = {
					'order': order,
					'type': 'win1',
					'party': confirms_rank1_party,
					'data': {
						'win_data': {
							'name': '시도지사 선거',
							'value': confirms_rank1_party_num,
							'total': 17,
						},
						'text': text,
						'title': confirms_rank1_party + ', 시도지사 선거',
					},
					'debugging': card_num,
				}
			else:
				card_num = '19-1'
				text = text_templates[card_num].format(**data)
				meta_card = {
					'order': order,
					'type': 'rank2',
					'party': rank1_party,
					'data': {
						'rank1':rank1_party,
						'rank2':rank2_party,
						'text': text,
						'title': '시도지사 선거 개표 1·2위',
					},
					'debugging': card_num,
				}
		
		elif polls[index] == 4:
			if (abs(rank1_party_num-rank2_party_num) / len(ranking) < 0.05):
				card_num = '19-6'
				text = text_templates[card_num].format(**data)
				meta_card = {
					'order': order,
					'type': 'rank2',
					'party': rank1_party,
					'data': {
						'title': '시군구청장 선거 개표 1·2위',
						'rank1': rank1_party,
						'rank2': rank2_party,
						'text': text,
					},
					'debugging': card_num,
				}
			elif (abs(rank1_party_num-rank2_party_num) / len(ranking) > 0.15):
				card_num = '19-9'
				text = text_templates[card_num].format(**data)
				meta_card = {
					'order': order,
					'type': 'compare',
					'party': rank1_party,
					'data': {
						'compare_data': {
							'type': 'party',
							'data': compare_data,
						},
						'text': text,
					},
					'debugging': card_num,
				}
			elif (confirms_rank1_party_num + confirms_rank2_party_num) > 2:
				card_num = '19-16'
				text = text_templates[card_num].format(**data)
				meta_card = {
					'order': order,
					'type': 'win1',
					'party': confirms_rank1_party,
					'data': {
						'win_data': {
							'name': '시군구청장 선거',
							'value': confirms_rank1_party_num,
							'total': 225,
						},
						'text': text,
						'title': confirms_rank1_party + ', 시군구청장 선거'
					},
					'debugging': card_num,
				}
			else:
				card_num = '19-2'
				text = text_templates[card_num].format(**data)
				meta_card = {
					'order': order,
					'type': 'rank2',
					'party': rank1_party,
					'data': {
						'title': '시군구청장 선거 개표 1·2위',
						'rank1': rank1_party,
						'rank2': rank2_party,
						'text': text,
					},
					'debugging': card_num,
				}
		
		elif polls[index] == 11:
			if len(confirms) > 2:
				card_num = '19-17'
			else:
				card_num = '19-3'

			text = text_templates[card_num].format(**data)
			meta_card = {
				'order': order,
				'type': 'winner',
				'party': 'default',
				'data': {
					'title': confirms_open_rank1_region + ', 교육감 선거',
					'name': open_rank1_region_candidate,
					'text': text,
				},
				'debugging': card_num,
			}


	elif card_seq == 20:
		rnum = str(randint(1,5))
		rnum = str(1)
		meta_card = None

		if rnum == '1':
			meta_cards = []
			subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sido).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계').subquery()

			sub_ranks = sess.query(OpenProgress).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxtime))

			ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
			ranksDf = ranksDf.reset_index(drop=True)
			ranks_vote = ranksDf.filter(regex="n*_percent")	
			ranks_ttl = [] # one line
			for i, ranks in ranks_vote.iterrows():
				ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])
			
			for idx, ranks in enumerate(ranks_ttl): # 지역마다
				yet_cnt = ranksDf.loc[idx, 'tooTotal'] - ranksDf.loc[idx, 'n_total'] - ranksDf.loc[idx, 'invalid']
				rank1_cnt = ranksDf.loc[idx, ranks[0]+'_vote']
				rank2_cnt = ranksDf.loc[idx, ranks[1]+'_vote']
				confirm = True if (rank1_cnt-rank2_cnt) > yet_cnt else False

				open_finished = True if ranksDf.loc[idx,'openPercent'] == 100 else False
				ranking = []
				if confirm or open_finished:
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
						try:
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
							else:
								current_candidate = None
								pass
						except ValueError:
							pass
				else:
					rank1_candidate = None
					rank2_candidate = None
					current_candidate = None

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
						text = text_templates[card_num].format(**data)
						meta_card = {
							'debugging': '20_2',
							'type': 'difference',
							'order': order,
							'party': 'default',
							'data': {
								'difference_data': {
									'first': rank1_candidate['name'],
									'second': rank2_candidate['name'],
									'difference': float(round(abs(rank1_candidate['percent']-rank2_candidate['percent']), 2)),
								},
								'text': text,
								'title': '오늘 선거의 이슈 - ' + rank1_candidate['sido'] + ' 시도지사 선거 결과'
							}
						}

					else:
						data = {
							'region': rank1_candidate['sido'],
							'poll': regionPoll(rank1_candidate['sido'], 3),
							'current_name': current_candidate['name'],
							'rank1_name': rank1_candidate['name'],
							'diff_percent': round(abs(rank1_candidate['percent']-current_candidate['percent']), 2),
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
									'first': rank1_candidate['name'],
									'second': rank2_candidate['name'],
									'difference': float(round(abs(rank1_candidate['percent']-rank2_candidate['percent']), 2))
								},
								'text': text,
								'title': '오늘 선거의 이슈 - ' + rank1_candidate['sido'] + ' 시도지사 선거 결과'
							}
						}
				except TypeError: # 20-6
					pass
				meta_cards.append(meta_card)
			try:
				meta_cards = list({v['data']['difference_data']['first']:v for v in meta_cards}.values())
			except TypeError:
				meta_cards = meta_cards

			try:
				meta_card = choice(meta_cards)
			except IndexError:
				meta_card = None
				pass
		
		elif rnum == '2':
			# 구시군청장
			meta_cards = []
			subq_g = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sggCityCode).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==4, OpenProgress.sggCityCode!=None).subquery()

			sub_ranks_g = sess.query(OpenProgress).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxtime))

			ranksDf_g = pd.read_sql(sub_ranks_g.statement, sub_ranks_g.session.bind)
			ranksDf_g = ranksDf_g.reset_index(drop=True)
			ranks_vote_g = ranksDf_g.filter(regex="n*_percent")	
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
							current_candidate = None
							pass
				else:
					rank1_candidate = None
					rank2_candidate = None
					current_candidate = None
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
			try:
				meta_card = choice(meta_cards)
			except IndexError:
				meta_card = None
				pass

		# elif rnum == '5': # 바른정당
		# 	sido_rank1_party_num = 0
		# 	for idx, ranks in enumerate(ranks_ttl):
		# 		if ranksDf.loc[idx, ranks[0]+'_jdName'] == '바른미래당':
		# 			sido_rank1_party_num += 1
			
		# 	gusigun_rank1_party_num = 0
		# 	for idx, ranks in enumerate(ranks_ttl_g):
		# 		if ranksDf_g.loc[idx, ranks[0]+'_jdName'] == '바른미래당':
		# 			gusigun_rank1_party_num += 1
			
		# 	if (sido_rank1_party_num == 0) and (gusigu_rank1_party_num == 0):
		# 		pass
		# 	else:
		# 		data = {
		# 			'hour': timeDisplay(time),
		# 			'sido_rank1_party_num': sido_rank1_party_num,
		# 			'gusigun_rank1_party_num': gusigun_rank1_party_num,
		# 		}
		# 		card_num = '20-5'
		# 		text = text_templates[card_num].format(**data)
		# 		meta_card = {
		# 			'order': order,
		# 			'type': 'wins',
		# 			'party': 'default',
		# 			'win_data': win_data,
		# 			'text': text,
		# 			'title': '바른미래당 선거 결과',
		# 			'debugging': card_num,
		# 		}

		# elif rnum == '3':
		# 	# 지역주의
		# 	bsjbtexts = []
		# 	sub_bs = sess.query(OpenProgress.serial, func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sido).filter(OpenProgress.electionCode.in_([3,4]), OpenProgress.sido.in_(['전라남도', '광주광역시']), OpenProgress.datatime<=time).subquery()
		# 	query_bs = sess.query(OpenProgress).join(sub_bs, and_(OpenProgress.serial==sub_bs.c.serial, OpenProgress.datatime==sub_bs.c.maxtime))
			
		# 	bsDf = pd.read_sql(query_bs.statement, query_bs.session.bind)
		# 	bsDf_ranks = bsDf.filter(regex="n*_percent").dropna(axis=1)
		# 	bsDf_ranks_ttl = []
		# 	for i, ranks in bsDf_ranks.iterrows():
		# 		bsDf_ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])

		# 	gj_num = len(bsDf_ranks_ttl)
		# 	bs_jayu = 0
		# 	bs_bamin = 0
		# 	for idx, ranks in enumerate(bsDf_ranks_ttl):
		# 		for i, r in enumerate(ranks):
		# 			if i == 0:
		# 				if bsDf.loc[idx, r+'_jdName'] == '자유한국당':
		# 					bs_jayu += 1
		# 				elif bsDf.loc[idx, r+'_jdName'] == '바른미래당':
		# 					bs_bamin += 1
		# 	try:
		# 		bs_ratio = round((bs_jayu + bs_bamin) / gj_num * 100, 2)
		# 	except ZeroDivisionError:
		# 		bs_ratio = 0
		# 	card_num = '20-3'
		# 	# bsjbtexts.append(text_templates[card_num].format(bs_jayu=bs_jayu, bs_bamin=bs_bamin, bs_ratio=bs_ratio))
		# 	if bs_ratio > 0:
		# 		text = text_templates[card_num].format(bs_jayu=bs_jayu, bs_bamin=bs_bamin, bs_ratio=bs_ratio)
		# 		meta_card = {
		# 			'order': order,
		# 			'type': 'compare',
		# 			'party': 'default',
		# 			'data': {
		# 				'compare_data': {
		# 					'type': 'party',
		# 					'data': [{
		# 						'party': '자유한국당',
		# 						'value': bs_jayu,
		# 						'unit': '개',
		# 					}, {
		# 						'party': '바른미래당',
		# 						'value': bs_bamin,
		# 						'unit': '개',
		# 					}]
		# 				},
		# 				'text': text,
		# 			},
		# 			'debugging': card_num,
		# 		}
		# 	else:
		# 		pass

		elif rnum == '4':
			# 대국경북 민주당 # 대구 경국 정의당
			sub_jb = sess.query(OpenProgress.serial, func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sido).filter(OpenProgress.electionCode.in_([3,4]), OpenProgress.sido.in_(['경상북도', '대구광역시']), OpenProgress.datatime<=time).subquery()
			query_jb = sess.query(OpenProgress).join(sub_jb, and_(OpenProgress.serial==sub_jb.c.serial, OpenProgress.datatime==sub_jb.c.maxtime))
			
			jbDf = pd.read_sql(query_jb.statement, query_jb.session.bind)
			jbDf = jdDf.reset_index(drop=True)
			jbDf_ranks = jbDf.filter(regex="n*_percent")
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

			if jb_ratio > 0:
				text = text_templates[card_num].format(jb_minju=jb_minju, jb_jung=jb_jung, jb_ratio=jb_ratio)
				meta_card = {
					'order': order,
					'type': 'compare',
					'party': 'default',
					'data': {
						'compare_data': {
							'type': 'party',
							'data': [{
								'party': '더불어민주당',
								'value': jb_minju,
								'unit': '개',
							}, {
								'party': '정의당',
								'value': jb_jung,
								'unit': '개',
							}]
						},
						'text': text,
					},
					'debugging': card_num,
				}
			else:
				pass

		if meta_card == None:
			subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sido).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계').subquery()

			sub_ranks = sess.query(OpenProgress).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxtime))

			ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
			ranksDf = ranksDf.reset_index(drop=True)
			if len(ranksDf) == 0:
				raise NoTextError

			ranks_vote = ranksDf.filter(regex="n*_percent")
			ranks_ttl = []
			for i, ranks in ranks_vote.iterrows():
				ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])

			ranking = []
			for idx, ranks in enumerate(ranks_ttl):
				ranking.append(ranksDf.loc[idx, ranks[0]+'_jdName'])
			rank1_count = Counter(ranking).most_common()

			try:
				minju_num = [r[1] for r in rank1_count if r[0]=='더불어민주당'][0]
			except IndexError:
				minju_num = 0
			
			try:	
				jayu_num = [r[1] for r in rank1_count if r[0]=='자유한국당'][0]
			except IndexError:
				jayu_num = 0
			
			card_num = '20-6'
			text = text_templates[card_num].format(minju_num=minju_num, jayu_num=jayu_num)
			meta_card = {
				'order': order,
				'type': 'compare',
				'party': 'default',
				'data': {
					'compare_data': {
						'type': 'party',
						'data': [{
							'party': '더불어민주당',
							'value': minju_num,
							'unit': '개',
						}, {
							'party': '자유한국당',
							'value': jayu_num,
							'unit': '개',
						}]
					},
					'text': text,
				},
				'debugging': card_num,
			}

	elif card_seq == 21:
		# 당선확정, 이용자가 선택한 선거구에서 당선 확정자가 나왔을 경우
		if len(candidates) > 0:
			candidates_all = sess.query(CandidateInfo.name, CandidateInfo.sdName, CandidateInfo.sggName, CandidateInfo.sgTypecode).filter(CandidateInfo.huboid.in_(candidates))
			# print(candidates_all)
			candidates_text = []
			for candidate, candidate_sido, candidate_region, sgtype in candidates_all:
				candidate_poll = regionPoll(candidate_region, sgtype)

				# candidate_poll table 선택
				if sgtype == 2: 
					candidate_poll_openrate, candidate_poll_openrate_serial = sess.query(OpenProgress.openPercent, OpenProgress.serial).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==2, OpenProgress.sggCityCode!=None, OpenProgress.sgg==candidate_region).order_by(OpenProgress.openPercent.desc()).first()

				elif sgtype == 3:
					candidate_poll_openrate, candidate_poll_openrate_serial = sess.query(OpenProgress.openPercent, OpenProgress.serial).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계', OpenProgress.sido==candidate_region).order_by(OpenProgress.openPercent.desc()).first()
					
				elif sgtype == 4:
					candidate_poll_openrate, candidate_poll_openrate_serial = sess.query(OpenProgress.openPercent, OpenProgress.serial).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==4, OpenProgress.sido==candidate_sido, OpenProgress.gusigun==candidate_region, OpenProgress.sggCityCode!=None).order_by(OpenProgress.openPercent.desc()).first()

				elif sgtype == 11:
					candidate_poll_openrate, candidate_poll_openrate_serial = sess.query(OpenProgress.openPercent, OpenProgress.serial).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==11, OpenProgress.gusigun=='합계', OpenProgress.sido==candidate_region).order_by(OpenProgress.openPercent.desc()).first()
				
				sub_ranks = sess.query(OpenProgress).filter(OpenProgress.serial==candidate_poll_openrate_serial)

				ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
				ranksDf = ranksDf.reset_index(drop=True)
				if len(ranksDf) > 0:
					ranks_vote = ranksDf.filter(regex="n*_percent")

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
			candidates_text = list(set(candidates_text))
			# candidates_text = ', '.join(candidates_text)

			# if candidates_text:
			# 	candidates_text += ', '
		else: # len(candidates) == 0:
			candidates_text = []

		if len(regions) > 0:
			region_nums = []
			for r in regions:
				region_nums.append(regionCodeCheck(r))

			regions_all = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.sggCityCode.in_(region_nums)).all()
			regions_all = list(set(regions_all))

			regions_text = []
			for region1, region2 in regions_all:
				region1Poll = regionPoll(region1, 3) # 시도지사
				
				region_serial = sess.query(OpenProgress.serial).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계', OpenProgress.sido==region1).order_by(OpenProgress.openPercent.desc()).first()[0]

				sub_ranks = sess.query(OpenProgress).filter(OpenProgress.serial==region_serial)

				ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
				ranksDf = ranksDf.reset_index(drop=True)
				if len(ranksDf) > 0:
					ranks_vote = ranksDf.filter(regex="n*_percent")	
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
					
					if region1_confirm_name:
						regions_text.append('{region1} {region1Poll} 선거에서 {region1_confirm_name} 후보가'.format(region1=region1, region1Poll=region1Poll, region1_confirm_name=region1_confirm_name))
					else:
						pass
				else:
					pass

				if (region2 == '합계') or (region2 == None):
					region2 = None
				try:
					region2Poll = regionPoll(region2, 4) # 구시군장
					# print(region2Poll)
					
					region2_serial = sess.query(OpenProgress.serial).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==4, OpenProgress.sido==region1, OpenProgress.gusigun==region2, OpenProgress.sggCityCode!=None).order_by(OpenProgress.openPercent.desc()).first()[0]
					# print(region2_serial)
					sub_ranks_g = sess.query(OpenProgress).filter(OpenProgress.serial==region2_serial)

					ranksDf_g = pd.read_sql(sub_ranks_g.statement, sub_ranks_g.session.bind)
					ranksDf_g = ranksDf_g.reset_index(drop=True)
					# print(ranksDf_g)
					if len(ranksDf_g) > 0:
						ranks_vote_g = ranksDf_g.filter(regex="n*_percent")	
						ranks_ttl_g = [] # one line
						for i, ranks in ranks_vote_g.iterrows():
							ranks_ttl_g.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])
						ranking_g = []
						region2_confirm_name = ''
						for idx, ranks in enumerate(ranks_ttl_g):
							rank1_cnt = ranksDf_g.loc[idx, ranks[0]+'_vote']
							rank2_cnt = ranksDf_g.loc[idx, ranks[1]+'_vote']
							yet_cnt = ranksDf_g.loc[idx, 'tooTotal'] - ranksDf_g.loc[idx, 'n_total'] - ranksDf_g.loc[idx, 'invalid']
							confirm = 1 if (rank1_cnt-rank2_cnt) > yet_cnt else 0
							if confirm:
								region2_confirm_name = ranksDf_g.loc[idx, ranks[0]+'_name']
						# print(region2_confirm_name)
						if region2_confirm_name:
							regions_text.append('{region2} {region2Poll} 선거에서 {region2_confirm_name} 후보가'.format(region2=region2, region2Poll=region2Poll, region2_confirm_name=region2_confirm_name))
						else:
							pass
					else:
						pass

				except AttributeError:
					pass
			regions_text = list(set(regions_text))
			# print(regions_text)
			# regions_text = ', '.join([r for r in regions_text if r != ''])
		else:
			regions_text = []
		
		if candidates_text or regions_text:
			# print(candidates_text, regions_text)
			texts = candidates_text + regions_text
			texts = list(set(texts))
			texts = ', '.join([t for t in texts if t])
			# if regions_text == '':
			# 	candidates_text = candidates_text[:-2]
			
			text = timeDisplay(time) + ' 현재 ' + texts + ' 당선이 확정되었다.'
			meta_card = {
				'order': order,
				'type': 'final',
				'party': 'default',
				'data': {
					'text': text,
				},
				'debugging': '21',
			}
		else:
			raise NoTextError


	elif card_seq == 22:
		if time > datetime.datetime(2018, 6, 13, 18, 59, 59):
			t = 18
		else:
			t = time.hour

		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t2 = 23
		else:
			t2 = time.hour
		
		toorate_avg_nat = sess.query(VoteProgress.tooRate).filter(VoteProgress.timeslot==t, VoteProgress.sido=='전국', VoteProgress.gusigun=='합계').scalar()

		if (toorate_avg_nat < 68.4) and (toorate_avg_nat >= 50):
			card_num = '22'
			text = text_templates[card_num].format(toorate_avg_nat=round(toorate_avg_nat, 2))
			meta_card = {
				'type': 'compare',
				'order': order,
				'party': 'default',
				'data': {
					'compare_data': {
						'type': 'rate',
						'data': [{
							'name': '1대 투표율',
							'value': 68.4,
							'unit': '%',
						}, {
							'name': '7대 투표율',
							'value': float(round(toorate_avg_nat, 1)),
							'unit': '%',
						}]
					},
					'text': text,
				},
				'debugging': card_num,
			}

		elif toorate_avg_nat > 68.4:
			card_num = '22-20'
			text = text_templates[card_num].format(toorate_avg_nat=round(toorate_avg_nat, 2))
			meta_card = {
				'debugging': '22-20',
				'type': 'compare',
				'order': order,
				'party': 'default',
				'data': {
					'compare_data': {
						'type': 'rate',
						'data': [{
							'name': '1대 투표율',
							'value': 68.4,
							'unit': '%',
						}, {
							'name': '7대 투표율',
							'value': float(round(toorate_avg_nat, 1)),
							'unit': '%',
						}]
					},
					'text': text,
				}
			}
		elif toorate_avg_nat < 50:
			card_num = '22-22'
			text = text_templates[card_num]
			meta_card = {
				'debugging': '22-22',
				'type': 'text',
				'order': order,
				'party': 'default',
				'data': {
					'background': background_variations[card_num],
					'text': text
				}
			}
		else: # 1,2,3,21,23,24,25	
			if t2 < 18:
				rnum = str(randint(1,3))
			else:
				if len(sess.query(VoteProgressLatest.timeslot).group_by(VoteProgressLatest.timeslot).all()) == 1:
					rnum = str(randint(1,7))
				else:
					rnum = str(randint(1,3))

			card_num = '22-' + rnum
			if rnum == '1':
				text = text_templates[card_num]
				meta_card = {
					'debugging': card_num,
					'type': 'semifinal',
					'order': order,
					'party': 'default',
					'data': {
						'text': text
					}
				}
			elif rnum == '2':
				text = text_templates[card_num]
				meta_card = {
					'debugging': card_num,
					'type': 'compare',
					'order': order,
					'party': 'default',
					'data': {
						'compare_data': {
							'type': 'rate',
							'data': [{
								'name': '4회 경쟁률',
								'value': 3.2,
								'unit': ':1',
							}, {
								'name': '7회 경쟁률',
								'value': 2.3,
								'unit': ':1',
							}]
						},
						'text': text,
					}
				}
			elif rnum == '3':	
				text = text_templates[card_num]
				meta_card = {
					'debugging': card_num,
					'type': 'compare',
					'order': order,
					'party': 'default',
					'data': {
						'compare_data': {
							'type': 'party',
							'data': [{
								'party': '더불어민주당',
								'value': 135,
								'unit': '억',
							}, {
								'party': '자유한국당',
								'value': 138,
								'unit': '억',
							}, {
								'party': '바른미래당',
								'value': 99,
								'unit': '억',
							}, {
								'party': '정의당',
								'value': 27,
								'unit': '억',
							}, {
								'party': '민주평화당',
								'value': 25,
								'unit': '억',
							}]
						},
						'text': text,
					}
				}
			elif rnum == '4':
				text = text_templates[card_num].format(yoo=yooTotal, too=tooTotal)
				meta_card = {
					'debugging': card_num,
					'type': 'text',
					'order': order,
					'party': 'default',
					'data': {
						'background': background_variations[card_num],
						'text': text,
					}
				}
			elif rnum == '5':
				
				sido_rank1 = sess.query(VoteProgress.tooRate, VoteProgress.sido).filter(VoteProgress.timeslot==t, VoteProgress.sido!='전국', VoteProgress.gusigun=='합계').group_by(VoteProgress.sido).order_by(func.max(VoteProgress.tooRate).desc()).first()[0]

				josa1 = josaPick(sido_rank1, '이며')

				gusigun_rank1 = sess.query(VoteProgress.gusigun).filter(VoteProgress.sido!='전국', VoteProgress.gusigun!='합계').group_by(VoteProgress.gusigun).order_by(func.max(VoteProgress.tooRate).desc()).first()[0]

				josa2 = josaPick(gusigun_rank1, '으로')
				text = text_templates[card_num].format(sido_rank1=sido_rank1, josa1=josa1, gusigun_rank1=gusigun_rank1, josa2=josa2)

				meta_card = {
					'debugging': card_num,
					'type': 'text',
					'order': order,
					'party': 'default',
					'data': {
						'background': background_variations[card_num],
						'text': text,
					}
				}
			elif rnum == '6':
				rank1, rank1_num, toorate = sess.query(VoteProgress.sido, VoteProgress.yooTotal, VoteProgress.tooRate).filter(VoteProgress.timeslot==t, VoteProgress.sido!='전국', VoteProgress.gusigun=='합계').group_by(VoteProgress.sido).order_by(func.max(VoteProgress.yooTotal).desc()).first()

				josa1 = josaPick(rank1, '으로')

				text = text_templates[card_num].format(rank1=rank1, josa1=josa1, rank1_num=rank1_num, toorate=toorate)

				meta_card = {
					'debugging': card_num,
					'type': 'text',
					'order': order,
					'party': 'default',
					'data': {
						'background': background_variations[card_num],
						'text': text,
					}
				}
			elif rnum == '7':
				rank1, rank1_num, toorate = sess.query(VoteProgress.sido, VoteProgress.yooTotal, VoteProgress.tooRate).filter(VoteProgress.timeslot==t, VoteProgress.sido!='전국',  VoteProgress.gusigun=='합계').group_by(VoteProgress.sido).order_by(func.max(VoteProgress.yooTotal).asc()).first()

				josa1 = josaPick(rank1, '으로')

				text = text_templates[card_num].format(rank1=rank1, josa1=josa1, rank1_num=rank1_num, toorate=toorate)

				meta_card = {
					'debugging': card_num,
					'type': 'text',
					'order': order,
					'party': 'default',
					'data': {
						'background': background_variations[card_num],
						'text': text,
					}
				}


	elif card_seq == 23:
		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t = 23
		else:
			t = time.hour

		if template == 1:
			card_num = '23-' + str(choice([5,6]))
		elif template == 2:
			card_num = '23-' + str(choice([0,1,3]))
		elif template == 3:
			card_num = '23-' + str(choice([7,8]))	
		elif template == 4:
			card_num = '23-' + str(choice([2,9,10,11,12]))
		elif template == 5:
			card_num = '23-' + str(2)

		text = text_templates[card_num].format(hour=timeDisplay(time))
		meta_card = {
			'order': order,
			'type': 'closing',
			'party': 'default',
			'data': {
				'text': text,
			},
			'debugging': card_num,
		}

	return meta_card