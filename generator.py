from string import Formatter
import datetime as dt

import pandas as pd

from templates import text_templates, img_templates, party2bg
from orm import *

from sqlalchemy.sql import func

# num2type = {1:"시도지사"}
# num2region = {1:"서울"}
# num2party =
# num2candidate

def generateMeta(args):
	type = "시도지사"
	region = sess.query(District.sun_name1, District.sun_name2).filter(District.suncode==args['region']).first()
	party = args['party']
	candidate = args['candidate']
	hour = dt.datetime.now().hour

	card_seqs = getCardSeqs(type, region, party, candidate, hour)

	meta = {}
	meta['card_count'] = len(card_seqs)
	meta_cards = []
	for i, card_seq in enumerate(card_seqs):
			meta_card = {}
			meta_card['order'] = i

			txt_vis, img_temp = generateTextsImgsViss(type, region, party, candidate, hour, card_seq)
			meta_card['type'] = img_temp
			meta_card['data'] = txt_vis

			meta_cards.append(meta_card)
	meta['cards'] = meta_cards

	return meta


def getCardSeqs(type, region, party, candidate, hour):

	card_seqs = [1,2,4]
	return card_seqs


# each by card
def generateTextsImgsViss(type, region, party, candidate, hour, card_seq):
	# db queries
	# 한번에 필요한 걸 다 쿼리해서 가지고 있는것
	# 카드 타입별로 쿼리를 작성해서 가지고 있는 것
	# 미리미리 aggregation해서 테이블에 가지고 있는 것
	card_data = query_card_data(type, region, party, candidate, hour, card_seq)
	text = text_templates[card_seq].format(**card_data)

	# img template gen
	img_temp = img_templates[card_seq]
	# img_temp['bg'] = party2bg[party]

	# vis gen
	vis = "path.png"

	txt_vis = {'text': text, 'vis': vis} #'raw': raw_data
	return txt_vis, img_temp
	# return txt_vis

def query_card_data(type, region, party, candidate, hour, card_seq):
	hour = 13

	keys = [kw for _, kw, _, _ in Formatter().parse(text_templates[card_seq]) if kw]
	vals = []
	if card_seq is 1:
		vals.append('서울시')
		vals.append('관악구')
		vals.append('시도지사')

	elif card_seq is 2:
		toorate_avg_net = sess.query(func.avg(Vote13.toorate).label('avg')).filter(Vote13.tootime <= hour).first()
		vals.append(round(toorate_avg_net.avg, 2))

	# elif card_seq is 3:
	# 	pass

	elif card_seq is 4:
		region1 = region[0]
		vals.append(region1)

		toorate_region1 = sess.query(func.avg(Vote13.toorate).label('avg')).filter(Vote13.tootime <= hour, Vote13.sun_name1==region1).first()
		vals.append(round(toorate_region1.avg, 2))

		toorate_avg_nat = sess.query(func.avg(Vote13.toorate).label('avg')).filter(Vote13.tootime <= hour).first()
		toorate_region1_toorate_avg_nat = toorate_region1.avg - toorate_avg_nat.avg
		vals.append(round(abs(toorate_region1_toorate_avg_nat),2))

		toorate_compare1 = '높은' if toorate_region1_toorate_avg_nat > 0 else '낮은'
		vals.append(toorate_compare1)

		region2 = region[1]
		vals.append(region2)

		toorate_region2 = sess.query(func.avg(Vote13.toorate).label('avg')).filter(Vote13.tootime <= hour, Vote13.sun_name1==region1).first()
		vals.append(round(toorate_region2.avg,2))

		toorate_compare2 = '높은' if (toorate_region2.avg - toorate_avg_nat.avg) > 0 else '낮은'
		vals.append(toorate_compare2)
		print(vals)



	card_data = {}
	for k, v in zip(keys, vals):
		card_data[k] = v

	return card_data
