from templates import text_templates, background_variations
from orm import *
from sqlalchemy.sql import func, and_
# from graph import generateMap, generateGraph
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

def query_card_data(sess, order, index, polls, regions, parties, candidates, time, card_seq, seqs_type, template):
	if card_seq == 1:
		if (len(candidates) > 0):
			card_num = '1'
			# **해당 변수가 2개 선택됐을 경우 먼저 선택한 변수를 출력, {투표율|득표율}에서는 해당 후보가 참여한 선거의 개표율이 10% 이하일 경우 투표율, 이상일 경우 득표율 출력
			candidate_names = sess.query(CandidateInfo.name).filter(CandidateInfo.huboid.in_(candidates)).first()
			# candidate_names = ', '.join([r[0] for r in candidate_names])
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
				# print(region_nums)
				# region_names = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.townCode.in_(region_nums)).all()
				region_names = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.sggCityCode.in_(region_nums)).all()

				region_names = list(set(region_names))
				region_join = []
				for r1, r2 in region_names:
					if (r2 == '합계') or (r2 == None):
						region_join.append(r1)
					else:
						region_join.append(r1+ ' ' + r2)
				# region_names = ', '.join(region_join)
				region_names = region_join[0]
				data = {
					'region_names': region_names,
					'tooOrget': '득표율' if seqs_type else '투표율',
				}
				text = '{region_names} 선거 {tooOrget} 현황'.format(**data)
				# TODO: region_name 출략 안됨 : 테스트 
			else:
				if len(parties) > 0:
					card_num = '1-2'
					# **해당 변수가 2개 선택됐을 경우 먼저 선택한 변수를 출력 {투표율|득표율}에서는 전체 시도지사 선거(17개), 시군구청장 선거(226개)에서 개표율이 10%가 넘는 지역의 수가 전체 선거구의 10%보다 적을 경우(2개, 23개) 투표율, 이상일 경우 득표율 출력
					party_names = sess.query(PartyCode.jdName).filter(PartyCode.pOrder.in_(parties)).first()
					# party_names = ', '.join([r[0] for r in party_names])
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
						# poll_names = ', '.join([r[0] for r in poll_names])
						poll_names = poll_names[0]
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
		
		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t = 23
		else:
			t = time.hour

		each_toorate = sess.query((VoteProgressLatest.yooTotal).label('yooTotal'), (VoteProgressLatest.tooTotal).label('tooTotal')).filter( VoteProgressLatest.gusigun!='합계').subquery()

		yooTotal, tooTotal = sess.query(func.sum(each_toorate.c.yooTotal), func.sum(each_toorate.c.tooTotal)).first()
	
		try:	
			toorate_avg_nat = (tooTotal) / (yooTotal) * 100
		except TypeError:
			raise NoTextError
		# print(toorate_avg_nat)
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
		if t in [8,10]:
			raise NoTextError
		# past = sess.query(func.max(PastVoteProgress.tooRate).label('max')).filter(PastVoteProgress.timeslot <= time.hour).group_by(PastVoteProgress.sido).subquery()
		# past_toorate = sess.query(func.avg(past.c.max)).scalar()
		each_toorate_p = sess.query(func.max(PastVoteProgress.yooTotal).label('yooTotal'), func.max(PastVoteProgress.tooTotal).label('tooTotal')).filter(PastVoteProgress.timeslot<=t, PastVoteProgress.gusigun=='합계').group_by(PastVoteProgress.sido).subquery()

		yooTotal_p, tooTotal_p = sess.query(func.sum(each_toorate_p.c.yooTotal), func.sum(each_toorate_p.c.tooTotal)).first()
		
		try:
			past_toorate = (tooTotal_p) / (yooTotal_p) * 100
		except TypeError:
			raise NoTextError

		each_toorate = sess.query((VoteProgressLatest.yooTotal).label('yooTotal'), (VoteProgressLatest.tooTotal).label('tooTotal')).filter(VoteProgressLatest.gusigun!='합계').subquery()
		yooTotal, tooTotal = sess.query(func.sum(each_toorate.c.yooTotal), func.sum(each_toorate.c.tooTotal)).first()
		
		current_toorate = (tooTotal) / (yooTotal) * 100

		current_toorate_past_toorate = current_toorate - past_toorate
		# print(past_toorate, current_toorate)
		toorate_compare = '높은' if current_toorate_past_toorate > 0 else '낮은'

		ranks = sess.query(func.max(VoteProgressLatest.tooRate).label('max'), VoteProgressLatest.sido).filter(VoteProgressLatest.timeslot<=t).group_by(VoteProgressLatest.sido, VoteProgressLatest.gusigun!='합계').order_by(func.max(VoteProgressLatest.tooRate).desc(), func.max(VoteProgressLatest.tooTotal).desc()).all()
		# print(ranks)
		ranks_map = sess.query(func.max(VoteProgressLatest.tooRate).label('max'), VoteProgressLatest.sido).group_by(VoteProgressLatest.sido, VoteProgressLatest.gusigun!='합계').order_by(func.max(VoteProgressLatest.tooRate).desc(), func.max(VoteProgressLatest.tooTotal).desc()).all()

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

		if t > 18:
			card_num = '3'
			text = text_templates[card_num].format(**data)
		else:
			card_num = '3-1'
			text = text_templates[card_num].format(**data)
		# 전국단위 문제 없음
		map_data = []
		for v, r in ranks_map:
			if r == '합계':
				pass
			else:
				map_data.append({'name':r, 'value':float(v)*0.01})
		# print(map_data)
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
		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t = 23
		else:
			t = time.hour
		# print(t)
		try:
			# region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.townCode==regions[index]).first()
			region_num = regionCodeCheck(regions[index])
			region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.sggCityCode==region_num).first()
		except TypeError:
			raise NoTextError
		print(region1, region2)
		if (region2 == '합계') or (region2 == None): # 시도만
			only_sido = True
		else: # 시 + 구시군
			only_sido = False

		if only_sido:
			# toorate_region1 = sess.query(func.max(VoteProgressLatest.tooRate)).filter( VoteProgressLatest.sido==region1, VoteProgressLatest.gusigun!='합계').scalar()
			yoo, too = sess.query(func.sum(VoteProgressLatest.yooTotal).label('yooTotal'), func.sum(VoteProgressLatest.tooTotal).label('tooTotal')).filter(VoteProgressLatest.sido==region1, VoteProgressLatest.gusigun!='합계').first()
			try:
				toorate_region1 = too/yoo*100
			except TypeError:
				raise NoTextError

			# print(toorate_region1)
			# if toorate_region1 == None: # toorate_region1 없으면
			# 	raise NoTextError
			
			each_toorate = sess.query((VoteProgressLatest.yooTotal).label('yooTotal'), (VoteProgressLatest.tooTotal).label('tooTotal')).filter(VoteProgressLatest.gusigun!='합계').subquery()
		
			yooTotal, tooTotal = sess.query(func.sum(each_toorate.c.yooTotal), func.sum(each_toorate.c.tooTotal)).first()
			
			try:
				toorate_avg_nat = (tooTotal) / (yooTotal) * 100
			except TypeError:
				raise NoTextError
			# print(toorate_avg_nat)
			toorate_region1_toorate_avg_nat = toorate_region1 - toorate_avg_nat

			toorate_compare1 = '높은' if toorate_region1_toorate_avg_nat > 0 else '낮은'

			region_name = region1


		else: # 시 + 구시군
			try:
				_, _, yooTotal, tooTotal = sess.query(VoteProgressLatest.townCode, PrecinctCode4.gusigun,  func.sum(VoteProgressLatest.yooTotal).label('yooTotal'), func.sum(VoteProgressLatest.tooTotal).label('tooTotal')).outerjoin(PrecinctCode4, and_(VoteProgressLatest.sido==PrecinctCode4.sido, VoteProgressLatest.gusigun==PrecinctCode4.sgg)).filter(VoteProgressLatest.timeslot<=t, PrecinctCode4.gusigun==region2, VoteProgressLatest.sido==region1).group_by(VoteProgressLatest.sido, PrecinctCode4.gusigun).first()
			except TypeError:
				raise NoTextError

			try:
				toorate_region1 = (tooTotal) / (yooTotal) * 100
			except TypeError:
				raise NoTextError
	
			# if toorate_region1 == None: # toorate_region1 없으면
			# 	raise NoTextError
			
			each_toorate = sess.query((VoteProgressLatest.yooTotal).label('yooTotal'), (VoteProgressLatest.tooTotal).label('tooTotal')).filter(VoteProgressLatest.gusigun!='합계').subquery()

			yooTotal_a, tooTotal_a = sess.query(func.sum(each_toorate.c.yooTotal), func.sum(each_toorate.c.tooTotal)).first()
			
			try:
				toorate_avg_nat = (tooTotal_a) / (yooTotal_a) * 100
			except TypeError:
				raise NoTextError
			print(toorate_avg_nat)

			toorate_region1_toorate_avg_nat = toorate_region1 - toorate_avg_nat

			toorate_compare1 = '높은' if toorate_region1_toorate_avg_nat > 0 else '낮은'

			region_name = region1 + ' ' + region2


		data = {
			'region1': region_name,
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

		toorate_region1_sub = sess.query(VoteProgressLatest.townCode, PrecinctCode4.gusigun,  func.sum(VoteProgressLatest.yooTotal).label('yooTotal'), func.sum(VoteProgressLatest.tooTotal).label('tooTotal')).outerjoin(PrecinctCode4, and_(VoteProgressLatest.sido==PrecinctCode4.sido, VoteProgressLatest.gusigun==PrecinctCode4.sgg)).filter(VoteProgressLatest.gusigun!='합계', VoteProgressLatest.sido==region1).group_by(VoteProgressLatest.sido, PrecinctCode4.gusigun)
		# (4144, '가평군', Decimal('100000'), Decimal('1000'), Decimal('54364'), None),

		# print(region1)
		# print(toorate_region1_sub)
		map_data = []
		for tc, r, yooTotal, tooTotal in toorate_region1_sub:
			if tc == 4901:
				r = '제주특별자치도'
			elif tc == 5101:
				r = '세종특별자치시'
			
			try:
				v = (tooTotal) / (yooTotal)
			except TypeError:
				v = 0
			map_data.append({'name':r, 'value':float(v)})
		# print(map_data)
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
		candidate, candidate_region, candidate_sdName = sess.query(CandidateInfo.name, CandidateInfo.sggName, CandidateInfo.sdName).filter(CandidateInfo.huboid==candidates[index]).first()
		# print(candidate_sdName)

		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t = 23
		else:
			t = time.hour

		# candidate_region_toorate = sess.query(func.max(VoteProgressLatest.tooRate)).filter(VoteProgressLatest.sido==candidate_sdName, VoteProgressLatest.gusigun!='합계').scalar()
		yoo, too = sess.query(func.sum(VoteProgressLatest.yooTotal).label('yooTotal'), func.sum(VoteProgressLatest.tooTotal).label('tooTotal')).filter(VoteProgressLatest.sido==candidate_sdName, VoteProgressLatest.gusigun!='합계').first()
		try:
			candidate_region_toorate = too/yoo*100
		except TypeError:
			raise NoTextError

		# VoteProgress에 sggName 필요함
		# if candidate_region_toorate == None:
		# 	raise NoTextError

		data = {
			'candidate': candidate,
			'candidate_region': candidate_region,
			'candidate_region_toorate': float(round(candidate_region_toorate, 2)),
		}
		if t > 18:
			card_num = '5'
			text = text_templates[card_num].format(**data)
		else:
			card_num = '5-1'
			data['hour'] = hourConverter(time.hour)
			text = text_templates[card_num].format(**data)


		candidate_region_sub = sess.query(VoteProgressLatest.townCode, PrecinctCode4.gusigun,  func.sum(VoteProgressLatest.yooTotal).label('yooTotal'), func.sum(VoteProgressLatest.tooTotal).label('tooTotal')).outerjoin(PrecinctCode4, and_(VoteProgressLatest.sido==PrecinctCode4.sido, VoteProgressLatest.gusigun==PrecinctCode4.sgg)).filter(VoteProgressLatest.gusigun!='합계', VoteProgressLatest.sido==candidate_sdName).group_by(VoteProgressLatest.sido, PrecinctCode4.gusigun)
		# print(candidate_sdName)
		# print(candidate_region_sub)
		map_data = []
		for tc, r, yooTotal, tooTotal in candidate_region_sub:
			if tc == 4901:
				r = '제주특별자치도'
			elif tc == 5101:
				r = '세종특별자치시'
			
			try:
				v = (tooTotal) / (yooTotal)
			except TypeError:
				v = 0
			map_data.append({'name':r, 'value':float(v)})
		# print(map_data)
		map_data = list({v['name']:v for v in map_data}.values())
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

		each_toorate_p = sess.query(PastVoteProgress.sido, func.max(PastVoteProgress.yooTotal).label('yooTotal'), func.max(PastVoteProgress.tooTotal).label('tooTotal')).filter(PastVoteProgress.timeslot<=t, PastVoteProgress.gusigun=='합계').group_by(PastVoteProgress.sido).subquery()

		yooTotal_p, tooTotal_p = sess.query(func.sum(each_toorate_p.c.yooTotal), func.sum(each_toorate_p.c.tooTotal)).first()
		
		try:
			past_toorate = (tooTotal_p) / (yooTotal_p) * 100
		except TypeError:
			raise NoTextError

		each_toorate = sess.query((VoteProgressLatest.yooTotal).label('yooTotal'), (VoteProgressLatest.tooTotal).label('tooTotal')).filter(VoteProgressLatest.gusigun!='합계').subquery()
		
		yooTotal, tooTotal = sess.query(func.sum(each_toorate.c.yooTotal), func.sum(each_toorate.c.tooTotal)).first()
		
		try:
			current_toorate = (tooTotal) / (yooTotal) * 100
		except TypeError:
			raise NoTextError

		current_toorate_past_toorate = current_toorate - past_toorate

		past = sess.query(PastVoteProgress.sido, func.max(PastVoteProgress.tooRate).label('max')).filter(PastVoteProgress.timeslot <= t, PastVoteProgress.gusigun=='합계').group_by(PastVoteProgress.sido)
		
		current = sess.query(VoteProgressLatest.sido, func.max(VoteProgressLatest.tooRate).label('max')).filter(VoteProgressLatest.timeslot <= t).group_by(VoteProgressLatest.sido)

		currentDf = pd.DataFrame(current.all())
		pastDf = pd.DataFrame(past.all())
		currentPastDf = pd.merge(currentDf, pastDf, on='sido')
		# print(currentPastDf['max_x'] - currentPastDf['max_y'])
		if t > 18:
			card_num = '6' if current_toorate_past_toorate > 0 else '6-0'
			text = text_templates[card_num]
		else:
			ratio = sum([1 for s in (currentPastDf['max_x'] - currentPastDf['max_y']).values if s > 0]) / len(currentDf['sido'])
			# print(ratio)
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
		# subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.townCode).filter(OpenProgress.datatime<=time, OpenProgress.gusigun!='합계', OpenProgress.electionCode==3).subquery()
		subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.gusigun=='합계').subquery()

		tooTotal, n_total, invalid = sess.query(func.sum(OpenProgress.tooTotal), func.sum(OpenProgress.n_total), func.sum(OpenProgress.invalid)).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxtime)).first()
		
		if invalid == None:
			invalid = 0
		try:		
			openrate_avg_nat = (n_total + invalid) / tooTotal * 100
		except TypeError:
			raise NoTextError

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
		openrate_sunname1_ranks = sess.query(OpenProgress3.openPercent.label('max'), OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.gusigun=='합계').group_by(OpenProgress3.cityCode).order_by(func.max(OpenProgress3.openPercent).desc(), func.max(OpenProgress3.n_total).desc()).all()
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

	elif card_seq == 9:
		openrate_sunname2_ranks = sess.query(func.max(OpenProgress4.openPercent).label('max'),  OpenProgress4.gusigun).filter(OpenProgress4.datatime<=time).group_by(OpenProgress4.sggCityCode).order_by(func.max(OpenProgress4.openPercent).desc(), func.max(OpenProgress4.n_total).desc()).all()
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
					'hour': timeDisplay(time),
					'open_finished': open_finished,
					'openrate_sunname2_rank1': openrate_sunname2_rank1['gusigun'],
					'josa': josaPick(openrate_sunname2_rank1['gusigun'], '이'),
					'openrate_sunname2_rank1_rate': openrate_sunname2_rank1['max'],
				}
				card_num = '9-1'
				text = text_templates[card_num].format(**data)
			else:
				data = {
					'hour': timeDisplay(time),
					'openrate_sunname2_rank1': openrate_sunname2_ranks[0][1],
					'josa1': josaPick(openrate_sunname2_ranks[0][1], '이'),
					'openrate_sunname2_rank1_rate': round(openrate_sunname2_ranks[0][0], 2),
					'openrate_sunname2_rank2': openrate_sunname2_ranks[1][1],
					'josa2': josaPick(openrate_sunname2_ranks[1][1], '이'),
					'openrate_sunname2_rank2_rate': round(openrate_sunname2_ranks[1][0], 2),
				}
				card_num = '9'
				text = text_templates[card_num].format(**data)
		else:
			raise NoTextError

		graph_data = []
		for v, r in openrate_sunname2_ranks:
			graph_data.append({'name':r, 'value':float(v)*0.01})
		# print(graph_data[:10])
		graph_data = list({v['name']:v for v in graph_data}.values())

		meta_card = {
			'order': order,
			'type': 'graph',
			'party': 'default',
			'data': {
				'graph_data': {
					'type': 'region',
					'data': graph_data[:10],
				},
				'text': text,
			},
			'debugging': card_num,
		}

	elif card_seq == 10:
		region_num = regionCodeCheck(regions[index])
		try:
			# region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.townCode==region_num).first()
			region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.sggCityCode==region_num).first()
		except TypeError:
			raise NoTextError

		if (region2 == '합계') or (region2 == None): # 시도만
			only_sido = True
		else: # 시 + 구시군
			only_sido = False

		if only_sido:
			subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.gusigun=='합계').subquery()

			sub_r = sess.query(OpenProgress3.gusigun, OpenProgress3.tooTotal, OpenProgress3.n_total, OpenProgress3.invalid).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))
			# print(sub_r.all())

			tooTotal_r, n_total_r, invalid_r = sess.query(func.sum(OpenProgress3.tooTotal), func.sum(OpenProgress3.n_total), func.sum(OpenProgress3.invalid)).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime)).first()

			region_name = region1
			if invalid_r == None:
				invalid_r = 0
			try:
				openrate_region1 = (n_total_r + invalid_r) / tooTotal_r * 100
			except TypeError:
				openrate_region1 = 0


		else: # 시+도 : 도의 결과
			subq = sess.query(func.max(OpenProgress4.serial).label('maxserial'), func.max(OpenProgress4.datatime).label('maxtime')).group_by(OpenProgress4.sggCityCode).filter(OpenProgress4.datatime<=time, OpenProgress4.sido==region1, OpenProgress4.sggCityCode!=None).subquery()

			sub_r = sess.query(OpenProgress4.gusigun, OpenProgress4.tooTotal, OpenProgress4.n_total, OpenProgress4.invalid).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime))
			# print(sub_r.all())

			tooTotal_r, n_total_r, invalid_r = sess.query(func.sum(OpenProgress4.tooTotal), func.sum(OpenProgress4.n_total), func.sum(OpenProgress4.invalid)).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime)).first()

			region_name = region1 + ' ' + region2
			if invalid_r == None:
				invalid_r = 0
			try:
				openrate_region1 = (n_total_r + invalid_r) / tooTotal_r * 100
			except TypeError:
				openrate_region1 = 0

		# print(sub_r.all())
		data = {
			'hour': timeDisplay(time),
			'region1': region_name,
			'josa1': josaPick(region_name, '은')
		}

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
			sub = sess.query(func.max(OpenProgress.tooTotal).label('tooTotal'), func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid')).filter(OpenProgress.datatime<=time).group_by(OpenProgress.townCode).subquery()

			tooTotal, n_total, invalid = sess.query(func.sum(sub.c.tooTotal), func.sum(sub.c.n_total), func.sum(sub.c.invalid)).first()

			if invalid == None:
				invalid = 0
			# openrate_avg_nat = (n_total + invalid) / tooTotal * 100
			try:		
				openrate_avg_nat = (n_total + invalid) / tooTotal * 100
			except TypeError:
				raise NoTextError

			openrate_region1_openrate_avg_nat = openrate_region1 - openrate_avg_nat
			compare_region1 = '높은' if openrate_region1_openrate_avg_nat > 0 else '낮은'

			data['openrate_region1'] = round(openrate_region1, 2)
			data['openrate_region1_openrate_avg_nat'] = round(abs(openrate_region1_openrate_avg_nat), 2)
			data['compare_region1'] = compare_region1
			
			card_num = '10'
			text = text_templates[card_num].format(**data)

			map_data = []
			for r, tooTotal, n_total, invalid in sub_r.all():
				if invalid == None:
					invalid = 0
				v = (n_total + invalid) / tooTotal
				map_data.append({'name':r, 'value':v})
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

			subq = sess.query(func.max(OpenProgress2.serial).label('maxserial'), func.max(OpenProgress2.datatime).label('maxtime')).group_by(OpenProgress2.sggCityCode).filter(OpenProgress2.datatime<=time, OpenProgress2.sggCityCode!=None).subquery()

			sub = sess.query(OpenProgress2.sgg, OpenProgress2.tooTotal, OpenProgress2.n_total, OpenProgress2.invalid).join(subq, and_(OpenProgress2.serial==subq.c.maxserial, OpenProgress2.datatime==subq.c.maxtime))

			tooTotal, n_total, invalid = sess.query(func.sum(OpenProgress2.tooTotal), func.sum(OpenProgress2.n_total), func.sum(OpenProgress2.invalid)).join(subq, and_(OpenProgress2.serial==subq.c.maxserial, OpenProgress2.datatime==subq.c.maxtime)).first()

		elif polls[index] == 3:
			poll, poll_num_sunname = sess.query(SgTypecode.sgName, func.count(PrecinctCode.cityCode)).join(PrecinctCode, PrecinctCode.electionCode==SgTypecode.sgTypecode).filter(SgTypecode.sgTypecode==polls[index]).first()

			subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.gusigun=='합계').subquery()

			sub = sess.query(OpenProgress3.sido, OpenProgress3.tooTotal, OpenProgress3.n_total, OpenProgress3.invalid).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))

			tooTotal, n_total, invalid = sess.query(func.sum(OpenProgress3.tooTotal), func.sum(OpenProgress3.n_total), func.sum(OpenProgress3.invalid)).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime)).first()

		elif polls[index] == 4:
			poll, poll_num_sunname = sess.query(SgTypecode.sgName, func.count(PrecinctCode.gusigun)).join(PrecinctCode, PrecinctCode.electionCode==SgTypecode.sgTypecode).filter(SgTypecode.sgTypecode==polls[index]).first()

			subq = sess.query(func.max(OpenProgress4.serial).label('maxserial'), func.max(OpenProgress4.datatime).label('maxtime')).group_by(OpenProgress4.sggCityCode).filter(OpenProgress4.datatime<=time, OpenProgress4.sggCityCode!=None).subquery()

			sub = sess.query(OpenProgress4.sido, OpenProgress4.tooTotal, OpenProgress4.n_total, OpenProgress4.invalid).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime))

			tooTotal, n_total, invalid = sess.query(func.sum(OpenProgress4.tooTotal), func.sum(OpenProgress4.n_total), func.sum(OpenProgress4.invalid)).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime)).first()

		elif polls[index] == 11:
			poll, poll_num_sunname = sess.query(SgTypecode.sgName, func.count(PrecinctCode.cityCode)).join(PrecinctCode, PrecinctCode.electionCode==SgTypecode.sgTypecode).filter(SgTypecode.sgTypecode==polls[index]).first()

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
				if invalid == None:
					invalid = 0
				v = (n_total + invalid) / tooTotal
				poll_openrate_ranks.append({'name':r, 'value':v})
			
			poll_openrate_ranks = sorted(poll_openrate_ranks, key=lambda x: x['value'], reverse=True)
			# print(poll_openrate_ranks)
			poll_openrate_ranks = list({v['name']:v for v in poll_openrate_ranks}.values())

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
			else:
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
		except TypeError:
			if tooTotal == None:
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
			else:
				raise NoTextError

	elif card_seq == 12:
		candidate, candidate_region, candidate_sdName, candidate_wiwName, candidate_poll_code = sess.query(CandidateInfo.name, CandidateInfo.sggName, CandidateInfo.sdName, CandidateInfo.wiwName, CandidateInfo.sgTypecode).filter(CandidateInfo.huboid==candidates[index]).first()
		# print(candidate_poll_code)
		# sggName에서 regionPoll 
		

		candidate_poll = regionPoll(candidate_region, candidate_poll_code)
		# print(candidate_region)
		# candidate_poll에 맞게 테이블 선택		
		if candidate_poll_code == 2: # 국회의원
			candidate_poll_openrate = sess.query(func.max(OpenProgress2.openPercent)).filter(OpenProgress2.sgg==candidate_region,OpenProgress2.datatime<=time, OpenProgress2.sggCityCode!=None).scalar()
		
		elif candidate_poll_code == 4:
			candidate_poll_openrate = sess.query(func.max(OpenProgress4.openPercent)).filter(OpenProgress4.gusigun==candidate_region,OpenProgress4.datatime<=time, OpenProgress4.sggCityCode!=None).scalar()

		elif candidate_poll_code == 3:
			candidate_poll_openrate = sess.query(func.max(OpenProgress3.openPercent)).filter(OpenProgress3.sido==candidate_region, OpenProgress3.gusigun=='합계',OpenProgress3.datatime<=time).scalar()

			candidate_poll_openrate_sub = sess.query(OpenProgress3.openPercent, OpenProgress3.gusigun).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==candidate_sdName, OpenProgress3.gusigun!='합계').all()

		elif candidate_poll_code == 11:
			candidate_poll_openrate = sess.query(func.max(OpenProgress11.openPercent)).filter(OpenProgress11.sido==candidate_region, OpenProgress11.gusigun=='합계',OpenProgress11.datatime<=time).scalar()
			# print(candidate_poll_openrate)
			candidate_poll_openrate_sub = sess.query(OpenProgress11.openPercent, OpenProgress11.gusigun).filter(OpenProgress11.datatime<=time, OpenProgress11.sido==candidate_sdName, OpenProgress11.gusigun!='합계').all()

		# else:
		# 	raise NoTextError
		try:
			candidate_region_name = candidate_sdName + ' ' + candidate_wiwName
		except TypeError:
			candidate_region_name = candidate_sdName
		data = {
			'candidate': candidate,
			'candidate_region': candidate_region_name,
			'candidate_poll': candidate_poll,
			'candidate_poll_openrate': candidate_poll_openrate,
		}
		
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
		subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.gusigun=='합계').subquery()

		sub = sess.query(OpenProgress3.sido, OpenProgress3.tooTotal, OpenProgress3.n_total, OpenProgress3.invalid).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))

		tooTotal, n_total, invalid = sess.query(func.sum(OpenProgress3.tooTotal), func.sum(OpenProgress3.n_total), func.sum(OpenProgress3.invalid)).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime)).first()

		if invalid == None:
			invalid = 0
		# openrate_avg_nat = (n_total + invalid) / tooTotal * 100
		try:		
			openrate_avg_nat = (n_total + invalid) / tooTotal * 100
		except TypeError:
			raise NoTextError

		if openrate_avg_nat < 100:
			openrate_sido = sess.query(OpenProgress3.sido).filter(OpenProgress3.openPercent==100, OpenProgress3.gusigun=='합계').group_by(OpenProgress3.sido).all()
			if len(openrate_sido) > 0:
				data = {
					'hour': timeDisplay(time),
					'open_finished_sido': ', '.join(sido[0] for sido in openrate_sido),
				}
				card_num = '13'
				text = text_templates[card_num].format(**data)
			else:
				text = ''

			openrate_gusigun = sess.query(OpenProgress4.gusigun).filter(OpenProgress4.openPercent==100).group_by(OpenProgress4.gusigun).all()
			if len(openrate_gusigun) > 0:
				data = {
					'hour': timeDisplay(time),
					'open_finished_gusigun': ', '.join(gusigun[0] for gusigun in openrate_gusigun),
				}
				card_num = '13-1'
				text += text_templates[card_num].format(**data)
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
			# card_num = '13-2'
			# text = text_templates[card_num].format(hour=hourConverter(time.hour))
			# meta_card = {
			# 	'order': order,
			# 	'type': 'rate',
			# 	'party': 'default',
			# 	'data': {
			# 		'title': '전국 개표 완료',
			# 		'rate': 100,
			# 		'text': text,
			# 	},
			# 	'debugging': card_num,
			# }	

	elif card_seq == 15:
		try:
			candidate_poll_code = sess.query(CandidateInfo.sgTypecode).filter(CandidateInfo.huboid==candidates[index]).first()[0]
		except IndexError:
			candidate_poll_code = None
		# print("candidate_poll_code", candidate_poll_code)
		try:
			poll_num = polls[index]
		except IndexError:
			poll_num = 9

		if len(regions) == 0:
			openrate_rank1_region = None
			if (candidate_poll_code == 3) or (poll_num == 3): # 시도지사
				subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.gusigun=='합계').subquery()

				sub_ranks = sess.query(OpenProgress3).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))
		
			elif (candidate_poll_code == 4) or (poll_num == 4): # 시군구청장
				subq = sess.query(func.max(OpenProgress4.serial).label('maxserial'), func.max(OpenProgress4.datatime).label('maxtime')).group_by(OpenProgress4.sggCityCode).filter(OpenProgress4.datatime<=time, OpenProgress4.sggCityCode!=None).subquery()

				sub_ranks = sess.query(OpenProgress4).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime))

			elif (candidate_poll_code == 2) or (poll_num == 2): # 국회의원
				subq = sess.query(func.max(OpenProgress2.serial).label('maxserial'), func.max(OpenProgress2.datatime).label('maxtime')).group_by(OpenProgress2.sggCityCode).filter(OpenProgress2.datatime<=time, OpenProgress2.sggCityCode!=None).subquery()

				sub_ranks = sess.query(OpenProgress2).join(subq, and_(OpenProgress2.serial==subq.c.maxserial, OpenProgress2.datatime==subq.c.maxtime))

			elif (candidate_poll_code == 11) or (poll_num == 11): # 교육감			
				subq = sess.query(func.max(OpenProgress11.serial).label('maxserial'), func.max(OpenProgress11.datatime).label('maxtime')).group_by(OpenProgress11.sido).filter(OpenProgress11.datatime<=time, OpenProgress11.gusigun=='합계').subquery()

				sub_ranks = sess.query(OpenProgress11).join(subq, and_(OpenProgress11.serial==subq.c.maxserial, OpenProgress11.datatime==subq.c.maxtime))
			else: 
				sub_ranks = None

			if sub_ranks == None:
				raise NoTextError

			ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
			ranksDf = ranksDf.sort_values(by=['openPercent', 'n_total'], ascending=False)
			# print(len(ranksDf))

			openrate_rank1_region = ranksDf.loc[0,'sido']
			if openrate_rank1_region == None:
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
				'hour': timeDisplay(time),
				'rank1_party': rank1_party, 
				'josa1': josaPick(rank1_party, '이'),
				'rank1_party_num': rank1_party_num,
				'ranks_party': ranks_party,
				'josa2': josaPick(ranks_party, '이'),
				'openrate_rank1_region': openrate_rank1_region,
				'openrate_rank1_region_candidate': openrate_rank1_region_candidate, 
				'openrate_rank2_region_candidate': openrate_rank2_region_candidate,
			}

			if (candidate_poll_code == 11) or (poll_num == 11):
				card_num = '15-11'
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
				pnum = candidate_poll_code or poll_num
				card_num = '15-' + str(pnum)
				text = text_templates[card_num].format(**data)

				meta_card = {
					'order': order,
					'type': 'rank2',
					'party': rank1_party,
					'data': {
						'title': sess.query(SgTypecode.sgName).filter(SgTypecode.sgTypecode==pnum).scalar() + ' 개표 1·2위',
						'rank1': rank1_party,
						'rank2': rank1_count[1][0],
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
			rank1_count = Counter([r['jdName'] for r in ranking if r['rank']==0]).most_common()
			# TODO: count 개수가 같아서 동률일때 
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

	elif card_seq == 16:
		region_num = regionCodeCheck(regions[index])
		try:
			# region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.townCode==region_num).first()
			region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.sggCityCode==region_num).first()
		except TypeError:
			raise NoTextError

		if (region2 == '합계') or (region2 == None): # 시도만
			only_sido = True
		else: # 시 + 구시군
			only_sido = False
		
		if only_sido:
			region1_poll = regionPoll(region1, 3)

			region1_openrate = sess.query(func.max(OpenProgress3.openPercent)).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==region1).scalar()

			subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==region1, OpenProgress3.gusigun=='합계').subquery()

			sub_ranks = sess.query(OpenProgress3).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))

			region_name = region1
		
		else:
			region1_poll = regionPoll(region2, 4)

			region1_openrate = sess.query(func.max(OpenProgress4.openPercent)).filter(OpenProgress4.datatime<=time, OpenProgress4.sido==region1, OpenProgress4.gusigun==region2).scalar()

			subq = sess.query(func.max(OpenProgress4.serial).label('maxserial'), func.max(OpenProgress4.datatime).label('maxtime')).group_by(OpenProgress4.sggCityCode).filter(OpenProgress4.datatime<=time, OpenProgress4.sido==region1, OpenProgress4.gusigun==region2, OpenProgress4.sggCityCode!=None).subquery()

			sub_ranks = sess.query(OpenProgress4).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime))

			region_name = region1 + ' ' + region2

		if sub_ranks == None:
			raise NoTextError
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
		candidate, candidate_region, sgtype = sess.query(CandidateInfo.name, CandidateInfo.sggName, CandidateInfo.sgTypecode).filter(CandidateInfo.huboid==candidates[index]).first()
		candidate_poll = regionPoll(candidate_region, sgtype)

		# candidate_poll table 선택
		if sgtype == 2: 
			candidate_poll_openrate = sess.query(func.max(OpenProgress2.openPercent)).filter(OpenProgress2.datatime<=time, OpenProgress2.sgg==candidate_region).scalar()

			subq = sess.query(func.max(OpenProgress2.serial).label('maxserial'), func.max(OpenProgress2.datatime).label('maxtime')).group_by(OpenProgress2.sggCityCode).filter(OpenProgress2.datatime<=time, OpenProgress2.sgg==candidate_region, OpenProgress2.sggCityCode!=None).subquery()

			sub_ranks = sess.query(OpenProgress2).join(subq, and_(OpenProgress2.serial==subq.c.maxserial, OpenProgress2.datatime==subq.c.maxtime))

		elif sgtype == 3:
			candidate_poll_openrate = sess.query(func.max(OpenProgress3.openPercent)).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==candidate_region).scalar()

			subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==candidate_region, OpenProgress3.gusigun=='합계').subquery()

			sub_ranks = sess.query(OpenProgress3).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))

		elif sgtype == 4:
			candidate_poll_openrate = sess.query(func.max(OpenProgress4.openPercent)).filter(OpenProgress4.datatime<=time, OpenProgress4.gusigun==candidate_region).scalar()
			
			subq = sess.query(func.max(OpenProgress4.serial).label('maxserial'), func.max(OpenProgress4.datatime).label('maxtime')).group_by(OpenProgress4.sggCityCode).filter(OpenProgress4.datatime<=time, OpenProgress4.gusigun==candidate_region, OpenProgress4.sggCityCode!=None).subquery()

			sub_ranks = sess.query(OpenProgress4).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime))

		elif sgtype == 11:
			candidate_poll_openrate = sess.query(func.max(OpenProgress11.openPercent)).filter(OpenProgress11.sido==candidate_region, OpenProgress11.gusigun=='합계').scalar()

			subq = sess.query(func.max(OpenProgress11.serial).label('maxserial'), func.max(OpenProgress11.datatime).label('maxtime')).group_by(OpenProgress11.sido).filter(OpenProgress11.datatime<=time, OpenProgress11.sido==candidate_region, OpenProgress11.gusigun=='합계').subquery()

			sub_ranks = sess.query(OpenProgress11).join(subq, and_(OpenProgress11.serial==subq.c.maxserial, OpenProgress11.datatime==subq.c.maxtime))

		if sub_ranks == None:
			raise NoTextError
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
		candidate_rate = [r['percent'] for r in ranking if r['name']==candidate][0]
		candidate_poll_rank1_party = ranking[0]['jdName']
		candidate_poll_rank1_name = ranking[0]['name']
		candidate_poll_rank1_rate = ranking[0]['percent']

		candidate_poll_rank2_party = ranking[1]['jdName']
		candidate_poll_rank2_name = ranking[1]['name']
		candidate_poll_rank2_rate = ranking[1]['percent']

		data = {
			'hour': timeDisplay(time),
			'candidate': candidate,
			'candidate_rate': candidate_rate,
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
		# print(party)
		
		# 시도지사
		subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.gusigun=='합계').subquery()

		sub_ranks = sess.query(OpenProgress3).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))

		if sub_ranks == None:
			raise NoTextError
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
		# print(rank1_count)
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
			if sub == None:
				raise NoTextError
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
			# print(rank1_count)
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
			# print(confirms_count)
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
				# 'confirms_rank2_party': confirms_rank2_party,
				# 'josa4': josaPick(confirms_rank2_party, '가'),			
				# 'confirms_rank2_party_num': confirms_rank2_party_num,
			}
		else: # 11 type
			if sub == None:
				raise NoTextError
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
				'hour': timeDisplay(time),
				'open_rank1_region': open_rank1_region,
				'open_rank1_region_candidate': open_rank1_region_candidate,
				# 'open_rank2_region': open_rank2_region,
				# 'open_rank2_region_candidate': open_rank2_region_candidate,
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
		# print("index:    ", index)
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
		# texts = []
		# TODO: sub_ranks
		rnum = str(randint(1,5))
		rnum = str(1)
		meta_card = None

		if rnum == '1':
			meta_cards = []
			subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.gusigun=='합계').subquery()

			sub_ranks = sess.query(OpenProgress3).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))

			# if sub_ranks == None:
				# raise NoTextError
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

			meta_cards = list({v['data']['difference_data']['first']:v for v in meta_cards}.values())
			try:
				meta_card = choice(meta_cards)
			except IndexError:
				meta_card = None
				pass
		
		elif rnum == '2':
			# 구시군청장
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
							current_candidate = None
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
			try:
				meta_card = choice(meta_cards)
			except IndexError:
				meta_card = None
				pass

		elif rnum == '5': # 바른정당
			sido_rank1_party_num = 0
			for idx, ranks in enumerate(ranks_ttl):
				if ranksDf.loc[idx, ranks[0]+'_jdName'] == '바른미래당':
					sido_rank1_party_num += 1
			
			gusigun_rank1_party_num = 0
			for idx, ranks in enumerate(ranks_ttl_g):
				if ranksDf_g.loc[idx, ranks[0]+'_jdName'] == '바른미래당':
					gusigun_rank1_party_num += 1
			
			if (sido_rank1_party_num == 0) and (gusigu_rank1_party_num == 0):
				pass
			else:
				data = {
					'hour': timeDisplay(time),
					'sido_rank1_party_num': sido_rank1_party_num,
					'gusigun_rank1_party_num': gusigun_rank1_party_num,
				}
				card_num = '20-5'
				text = text_templates[card_num].format(**data)
				meta_card = {
					'order': order,
					'type': 'wins',
					'party': 'default',
					'win_data': win_data,
					'text': text,
					'title': '바른미래당 선거 결과',
					'debugging': card_num,
				}

		elif rnum == '3':
			# 지역주의
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
			# bsjbtexts.append(text_templates[card_num].format(bs_jayu=bs_jayu, bs_bamin=bs_bamin, bs_ratio=bs_ratio))
			if bs_ratio > 0:
				text = text_templates[card_num].format(bs_jayu=bs_jayu, bs_bamin=bs_bamin, bs_ratio=bs_ratio)
				meta_card = {
					'order': order,
					'type': 'compare',
					'party': 'default',
					'data': {
						'compare_data': {
							'type': 'party',
							'data': [{
								'party': '자유한국당',
								'value': bs_jayu,
								'unit': '개',
							}, {
								'party': '바른미래당',
								'value': bs_bamin,
								'unit': '개',
							}]
						},
						'text': text,
					},
					'debugging': card_num,
				}
			else:
				pass

		elif rnum == '4':
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
			# bsjbtexts.append(text_templates[card_num].format(jb_minju=jb_minju, jb_jung=jb_jung, jb_ratio=jb_ratio))

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

		# print(meta_card)
		if meta_card == None:
			subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.gusigun=='합계').subquery()

			sub_ranks = sess.query(OpenProgress3).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))

			ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
			# print(len(ranksDf))
			if len(ranksDf) == 0:
				raise NoTextError
			ranks_vote = ranksDf.filter(regex="n*_percent").dropna(axis=1)
			ranks_ttl = []
			for i, ranks in ranks_vote.iterrows():
				ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])

			ranking = []
			for idx, ranks in enumerate(ranks_ttl):
				ranking.append(ranksDf.loc[idx, ranks[0]+'_jdName'])
			rank1_count = Counter(ranking).most_common()
			# print(rank1_count)
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
			candidates_text = list(set(candidates_text))
			candidates_text = ', '.join(candidates_text)

			if candidates_text:
				candidates_text += ', '
		else: # len(candidates) == 0:
			candidates_text = ''

		if len(regions) > 0:
			region_nums = []
			for r in regions:
				region_nums.append(regionCodeCheck(r))

			# regions_all = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.townCode.in_(region_nums)).all()
			regions_all = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.sggCityCode.in_(region_nums)).all()
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
							# print(region1_confirm_name)
					
					if region1_confirm_name:
						regions_text.append('{region1} {region1Poll} 선거에서 {region1_confirm_name} 후보가'.format(region1=region1, region1Poll=region1Poll, region1_confirm_name=region1_confirm_name))
						# print("ggggg:", regions_text)
					else:
						pass
				else:
					pass
				# print(regions_text)
				if (region2 == '합계') or (region2 == None):
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
							rank1_cnt = ranksDf_g.loc[idx, ranks[0]+'_vote']
							rank2_cnt = ranksDf_g.loc[idx, ranks[1]+'_vote']
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
			regions_text = list(set(regions_text))
			regions_text = ', '.join([r for r in regions_text if r != ''])
			# print(regions_text)
		else:
			regions_text = ''
		
		# print(candidates_text)
		# print(regions_text)
		
		if (len(candidates_text) > 0) or (len(regions_text) > 0):
			text = timeDisplay(time) + ' 현재 ' + candidates_text + regions_text + ' 당선이 확정되었다.'
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
		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t = 23
		else:
			t = time.hour

		each_toorate = sess.query((VoteProgressLatest.yooTotal).label('yooTotal'), (VoteProgressLatest.tooTotal).label('tooTotal')).filter( VoteProgressLatest.gusigun!='합계').subquery()

		yooTotal, tooTotal = sess.query(func.sum(each_toorate.c.yooTotal), func.sum(each_toorate.c.tooTotal)).first()
		
		toorate_avg_nat = (tooTotal) / (yooTotal) * 100

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
			if t < 18:
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
				
				sido_rank1 = sess.query(VoteProgressLatest.sido).filter(VoteProgressLatest.gusigun=='합계').group_by(VoteProgressLatest.sido).order_by(func.max(VoteProgressLatest.tooRate).desc()).first()[0]

				josa1 = josaPick(sido_rank1, '이며')

				gusigun_rank1 = sess.query(VoteProgressLatest.gusigun).filter(VoteProgressLatest.gusigun!='합계').group_by(VoteProgressLatest.gusigun).order_by(func.max(VoteProgressLatest.tooRate).desc()).first()[0]

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
				rank1, rank1_num, toorate = sess.query(VoteProgressLatest.sido, VoteProgressLatest.yooTotal, VoteProgressLatest.tooRate).filter( VoteProgressLatest.gusigun=='합계').group_by(VoteProgressLatest.sido).order_by(func.max(VoteProgressLatest.yooTotal).desc()).first()

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
				rank1, rank1_num, toorate = sess.query(VoteProgressLatest.sido, VoteProgressLatest.yooTotal, VoteProgressLatest.tooRate).filter( VoteProgressLatest.gusigun=='합계').group_by(VoteProgressLatest.sido).order_by(func.max(VoteProgressLatest.yooTotal).asc()).first()
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

		# meta_card = {
		# 	'order': order,
		# 	'type': 'default',
		# 	'party': 'default',
		# 	'data': {
		# 		'text': text,
		# 	},
		# 	'debugging': card_num,
		# }

	elif card_seq == 23:
		if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
			t = 23
		else:
			t = time.hour

		# if t > 18:
		# 	card_num = '23-' + str(randint(0,4))
		# else: 
		# 	card_num = '23-' + str(randint(0,3))
		if template == 1:
			card_num = '23-' + str(choice([5,6]))
		elif template == 2:
			card_num = '23-' + str(choice([0,1,3]))
		elif template == 3:
			card_num = '23-' + str(choice([7,8]))	
		elif template == 4:
			card_num = '23-' + str(choice([2,9,10,11,12]))

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
	# return text, RANK1, title, rate, name, graph, map
	return meta_card