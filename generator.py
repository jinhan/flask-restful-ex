# from string import Formatter
import datetime
# from templates import text_templates
from orm import *
from sqlalchemy.sql import func
from random import randint
# from graph import generateMap, generateGraph
# import pandas as pd
from timeit import default_timer as timer
from queries import query_card_data

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

	each_openrate = sess.query(func.max(OpenProgress.openPercent).label('max')).filter(OpenProgress.datatime<=time).group_by(OpenProgress.sido).subquery()
	openrate = sess.query(func.avg(each_openrate.c.max)).scalar()
	# print(openrate)

	if time.hour < 18: # 투표중
		card_seqs.extend([1, 2, 3, 6, 23]) # 6 특이사항
		card_seqs.extend([4] * len(regions))
		card_seqs.extend([5] * len(candidates))
		card_seqs.sort()
	# 어떤 선거의 개표율 10 기준?
	elif time.hour > 18 and openrate < 10: # 투표마감이후
		card_seqs.extend([1, 2, 3, 6, 22, 23]) # 6 특이사항
		card_seqs.extend([4] * len(regions))
		card_seqs.extend([5] * len(candidates))
		card_seqs.sort()
	
	elif time.hour > 18 and openrate >= 10 and openrate < 30: # 개표율 10% 이상
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

	elif time.hour > 18 and openrate >= 30: # 개표율 30% 이상
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

	return card_seqs

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

	# card_seqs = getCardSeqs(polls, regions, parties, candidates, time)
	# card_seqs = [2,3,4,5,6,7,10,12,13]
	card_seqs = [2,3,4,5,6]
	print(card_seqs)

	start = timer()
	meta = {}
	meta['card_count'] = len(card_seqs)
	meta['design_variation'] = randint(0,3)
	meta_cards = []
	# index = 0
	# TODO: 멀티로 생성할 수 있도록 
	# TODO: 한번에 여러 쿼리가 들어오는 경우, 같은 데이터 쿼리가 불러오지 않도록 
	
	for i, card_seq in enumerate(card_seqs):
		if card_seqs[i-1] is card_seq:
			index += 1
		else:
			index = 0

		# meta_card = {}
		# meta_card['order'] = i+1
		order = i+1
		
		# try:
		# 	img_type, img_party, data = generateTextsImgsViss(order, index, polls, regions, parties, candidates, time, card_seq)
		# except TypeError:
		# 	print("pass:    ", card_seq)
		# 	continue # go to next loop


		# meta_card['type'] = img_type
		# meta_card['party'] = img_party
		# meta_card['data'] = data
		# meta_card['debug'] = card_seq
		try:
			meta_card = query_card_data(order, index, polls, regions, parties, candidates, time, card_seq)
		except TypeError:
			continue

		meta_cards.append(meta_card)
	meta['cards'] = meta_cards
	end = timer()
	print(end - start)

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
	
	sess.close()
	return meta





