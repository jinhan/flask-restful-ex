# from string import Formatter
import datetime
# from templates import text_templates
from orm import *
from sqlalchemy.sql import func
from random import randint
# from graph import generateMap, generateGraph
# import pandas as pd
from timeit import default_timer as timer
from queries import query_card_data, NoTextError

# from multiprocessing import Pool
# import os

# def gen_meta_cards(x):
# 	# print(x)
# 	print(os.getpid())
# 	# print(x[1][0], x[1][1], x[1][2], x[1][3], x[1][4], x[1][5], x[1][6])
# 	img_type, img_party, data = generateTextsImgsViss(x[1][0], x[1][1], x[1][2], x[1][3], x[1][4], x[1][5], x[1][6]) # index, polls, regions, parties, candidates, time, card_seq
# 	# print(img_type)
# 	return 1
# 	# return {'order': x[0]+1, 'type': img_type, 'party': img_party, 'data': data, 'debug': x[1][6]}

def getCardSeqs(polls, regions, parties, candidates, time):
	card_seqs = []

	if (len(candidates) > 0) and (len(regions) > 0) and (len(parties) > 0) and (len(polls) > 0):
		candidate, candidate_region, candidate_poll_code = sess.query(CandidateInfo.name, CandidateInfo.sggName, CandidateInfo.sgTypecode).filter(CandidateInfo.huboid==candidates[0]).first()

		if candidate_poll_code == 2: # 국회의원
			openrate = sess.query(func.max(OpenProgress2.openPercent)).filter(OpenProgress2.sgg==candidate_region).scalar() # OpenProgress2.datatime<=time, 
		elif candidate_poll_code == 3:
			openrate = sess.query(func.max(OpenProgress3.openPercent)).filter(OpenProgress3.sido==candidate_region, OpenProgress3.gusigun=='합계').scalar() # OpenProgress3.datatime<=time,  
		elif candidate_poll_code == 4:
			openrate = sess.query(func.max(OpenProgress4.openPercent)).filter(OpenProgress4.gusigun==candidate_region).scalar() # OpenProgress4.datatime<=time, 
		elif candidate_poll_code == 11:
			openrate = sess.query(func.max(OpenProgress11.openPercent)).filter(OpenProgress11.sido==candidate_region, OpenProgress11.gusigun=='합계').scalar() # OpenProgress11.datatime<=time, 
		else:
			openrate = sess.query(func.max(OpenProgress.openPercent)).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==candidate_poll_code, OpenProgress.sido==candidate_region).scalar()

	elif (len(candidates) == 0) and (len(regions) > 0) and (len(parties) > 0) and (len(polls) > 0):
		region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.sggCityCode==regions[0]).first()

		openrate = sess.query(func.max(OpenProgress3.openPercent)).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==region1).scalar()

	# elif (len(candidates) == 0) and (len(regions) == 0) and (len(parties) > 0) and (len(polls) > 0):
	# 	parites
	elif (len(candidates) == 0) and (len(regions) == 0) and (len(parties) == 0) and (len(polls) > 0):
		if polls[0] == 2:
			sub = sess.query(func.max(OpenProgress2.tooTotal).label('tooTotal'), func.max(OpenProgress2.n_total).label('n_total'), func.max(OpenProgress2.invalid).label('invalid')).subquery() # .filter(OpenProgress2.datatime<=time)
			tooTotal, n_total, invalid = sess.query(func.sum(sub.c.tooTotal), func.sum(sub.c.n_total), func.sum(sub.c.invalid)).first()
		
			openrate = (n_total + invalid) / tooTotal * 100

		elif polls[0] is 3:
			sub = sess.query(func.max(OpenProgress3.tooTotal).label('tooTotal'), func.max(OpenProgress3.n_total).label('n_total'), func.max(OpenProgress3.invalid).label('invalid')).filter(OpenProgress3.gusigun=='합계').subquery() # .filter(OpenProgress2.datatime<=time)
			tooTotal, n_total, invalid = sess.query(func.sum(sub.c.tooTotal), func.sum(sub.c.n_total), func.sum(sub.c.invalid)).first()
		
			openrate = (n_total + invalid) / tooTotal * 100
		
		elif polls[0] is 4:
			sub = sess.query(func.max(OpenProgress4.tooTotal).label('tooTotal'), func.max(OpenProgress4.n_total).label('n_total'), func.max(OpenProgress4.invalid).label('invalid')).subquery() # .filter(OpenProgress2.datatime<=time)
			tooTotal, n_total, invalid = sess.query(func.sum(sub.c.tooTotal), func.sum(sub.c.n_total), func.sum(sub.c.invalid)).first()
		
			openrate = (n_total + invalid) / tooTotal * 100
		
		elif polls[0] is 11:
			sub = sess.query(func.max(OpenProgress11.tooTotal).label('tooTotal'), func.max(OpenProgress11.n_total).label('n_total'), func.max(OpenProgress11.invalid).label('invalid')).filter(OpenProgress11.gusigun=='합계').subquery() # .filter(OpenProgress2.datatime<=time)
			tooTotal, n_total, invalid = sess.query(func.sum(sub.c.tooTotal), func.sum(sub.c.n_total), func.sum(sub.c.invalid)).first()
		
			openrate = (n_total + invalid) / tooTotal * 100
	
	else:
		openrate = 0
	
	print(openrate)
	
	if time.hour < 18: # 투표중
		card_seqs.extend([1, 2, 3, 6, 23]) # 6 특이사항
		card_seqs.extend([4] * len(regions))
		card_seqs.extend([5] * len(candidates))
		card_seqs.sort()
		seqs_type = 0
	# 어떤 선거의 개표율 10 기준?
	elif time.hour > 18 and openrate < 10: # 투표마감이후
		card_seqs.extend([1, 2, 3, 6, 22, 23]) # 6 특이사항
		card_seqs.extend([4] * len(regions))
		card_seqs.extend([5] * len(candidates))
		card_seqs.sort()
		seqs_type = 0
	elif time.hour > 18 and openrate >= 10 and openrate < 30: # 개표율 10% 이상
		card_seqs.extend([1, 2, 3, 7, 8, 9, 20, 23]) # 6, 13, 20 특이사항
		card_seqs.extend([4] * len(regions))
		card_seqs.extend([5] * len(candidates))
		card_seqs.extend([10] * len(regions))
		card_seqs.extend([11] * len(polls))
		card_seqs.extend([12] * len(candidates))
		card_seqs.extend([16] * len(regions))
		card_seqs.extend([17] * len(candidates))
		card_seqs.extend([18] * len(parties))
		card_seqs.sort()
		seqs_type = 1
	elif time.hour > 18 and openrate >= 30: # 개표율 30% 이상
		card_seqs.extend([1, 2, 7, 13, 14, 15, 20, 23]) # 13, 20 특이사항
		card_seqs.extend([10] * len(regions))
		card_seqs.extend([11] * len(polls))
		card_seqs.extend([12] * len(candidates))
		card_seqs.extend([16] * len(regions))
		card_seqs.extend([17] * len(candidates))
		card_seqs.extend([18] * len(parties))
		card_seqs.sort()
		card_seqs.insert(1, 21)
		seqs_type = 1
	# 내가 선택한 선거에서 한명이라도 당선 확정이 나오는 경우 21번을 index 1에 insert
	return card_seqs, seqs_type

# each by card
# def generateTextsImgsViss(index, polls, regions, parties, candidates, time, card_seq):
# 	index = 0

# 	text, RANK1, title, rate, name, graph, map = query_card_data(index, polls, regions, parties, candidates, time, card_seq)
# 	if text is None:
# 		raise TypeError
	
# 	img_type = seq2type[card_seq]
# 	img_party = RANK1

# 	data = {'title': title, 'rate': rate, 'name': name, 'text': text, 'graph': graph, 'map': map} #'raw': raw_data
	
# 	return img_type, img_party, data

def generateMeta(args):
	polls = args['type']
	regions = args['region']
	parties = args['party']
	candidates = args['candidate']

	time = datetime.datetime.strptime(args['time'], '%Y%m%d%H%M%S')
	# time = datetime.datetime.now()

	# args가 같고, 데이터 기록 시간이 업데이트 되지 않으면 아래를 실행하지 않고, 고유 아이디 전송
	# 고유아이디, 시간
	# 시간: 어떤 시간?

	card_seqs, seqs_type = getCardSeqs(polls, regions, parties, candidates, time)
	# card_seqs = [2,3,4,5,6,7,8,9,10,11,12,13]
	# card_seqs = [2,3,4,5,6]
	# card_seqs = [19]
	print(card_seqs)

	# start = timer()
	meta = {}
	meta['card_count'] = len(card_seqs)
	meta['design_variation'] = randint(0,3)
	meta_cards = []
	# TODO: 멀티로 생성할 수 있도록 
	# TODO: 한번에 여러 쿼리가 들어오는 경우, 같은 데이터 쿼리가 불러오지 않도록 
	# TODO: parallel, 중복 쿼리 가지 않도록 새로운 데이터 있는지 체크

	index = 0
	for i, card_seq in enumerate(card_seqs):
		if card_seqs[i-1] is card_seq:
			index += 1
		else:
			index = 0

		order = i+1
		
		try:
			meta_card = query_card_data(order, index, polls, regions, parties, candidates, time, card_seq, seqs_type)
		except NoTextError:
			print("pass:    ", card_seq)
			continue
		meta_card['debugging'] = card_seq
		meta_cards.append(meta_card)

	meta['cards'] = meta_cards
	# end = timer()
	# print(end - start)

	#################
	# multiprocessing
	# start = timer()
	# meta = {}
	# meta['card_count'] = len(card_seqs)
	# meta['design_variation'] = randint(0,3)
	# d = {}
	# for i, card_seq in enumerate(card_seqs):
	# 	if card_seqs[i-1] is card_seq:
	# 		index += 1
	# 	else:
	# 		index = 0
	# 	d[i] = (index, polls, regions, parties, candidates, time, card_seq)
	# # print(d.items())
	# p = Pool()
	# # meta_cards = p.map(gen_meta_cards, [1,2,3])
	# meta_cards = p.map_async(gen_meta_cards, d.items())
	# # print(meta_cards)
	# meta['cards'] = meta_cards.get()
	# p.close()
	# end = timer()
	# print(end-start)
	
	# sess.close()
	return meta





