from string import Formatter
import datetime

import pandas as pd

from templates import text_templates
from orm import *

from sqlalchemy.sql import func


def generateMeta(args):
	type = "시도지사"
	region = sess.query(District.sun_name1, District.sun_name2).filter(District.suncode==args['region']).first()
	party = args['party']
	candidate = args['candidate']
	time = datetime.datetime.now()

	card_seqs = getCardSeqs(type, region, party, candidate, time)

	meta = {}
	meta['card_count'] = len(card_seqs)
	meta_cards = []
	for i, card_seq in enumerate(card_seqs):
			meta_card = {}
			meta_card['order'] = i

			txt_vis, img_temp = generateTextsImgsViss(type, region, party, candidate, time, card_seq)
			meta_card['img'] = img_temp
			meta_card['data'] = txt_vis

			meta_cards.append(meta_card)
	meta['cards'] = meta_cards

	sess.close()
	return meta


def getCardSeqs(type, region, party, candidate, time):

	card_seqs = [1,2,4,5,7]
	return card_seqs


# each by card
def generateTextsImgsViss(type, region, party, candidate, time, card_seq):
	# db queries
	card_data, rank1 = query_card_data(type, region, party, candidate, time, card_seq)
	text = text_templates[card_seq].format(**card_data)

	# img template gen
	img_temp = {'type': card_seq, "bg_color": rank1}

	# vis gen
	vis = None

	txt_vis = {'text': text, 'vis': vis} #'raw': raw_data
	return txt_vis, img_temp


def query_card_data(type, region, party, candidate, time, card_seq):
	time = datetime.datetime(2017, 5, 9, 22, 10, 56, 970686)

	keys = [kw for _, kw, _, _ in Formatter().parse(text_templates[card_seq]) if kw]
	vals = []

	if card_seq is 1:
		vals.append(region[0])
		vals.append(region[1])
		vals.append('시도지사')

		rank1 = None

	elif card_seq is 2:
		each_toorate = sess.query(func.max(Vote13.toorate).label('max')).filter(Vote13.tootime<=time.hour).group_by(Vote13.sun_name1)
		toorate_avg_nat = sess.query(func.avg(each_toorate.subquery().columns.max)).first()
		vals.append(round(toorate_avg_nat[0], 2))

		rank1 = None

	# elif card_seq is 3:


	elif card_seq is 4:
		region1 = region[0]
		vals.append(region1)

		toorate_region1 = sess.query(func.max(Vote13.toorate)).filter(Vote13.tootime<=time.hour, Vote13.sun_name1==region1).first()
		vals.append(round(toorate_region1[0], 2))

		each_toorate = sess.query(func.max(Vote13.toorate).label('max')).filter(Vote13.tootime<=time.hour).group_by(Vote13.sun_name1)
		toorate_avg_nat = sess.query(func.avg(each_toorate.subquery().columns.max)).first()
		toorate_region1_toorate_avg_nat = toorate_region1[0] - toorate_avg_nat[0]
		vals.append(round(abs(toorate_region1_toorate_avg_nat),2))

		toorate_compare1 = '높은' if toorate_region1_toorate_avg_nat > 0 else '낮은'
		vals.append(toorate_compare1)

		region2 = region[1]
		vals.append(region2)

		toorate_region2 = sess.query(func.max(Vote13.toorate)).filter(Vote13.tootime<=time.hour, Vote13.sun_name1==region1).first()
		vals.append(round(toorate_region2[0],2))

		toorate_compare2 = '높은' if (toorate_region2[0] - toorate_avg_nat[0]) > 0 else '낮은'
		vals.append(toorate_compare2)

		rank1 = None

	elif card_seq is 5:
		vals.append(time.hour)

		each_openrate = sess.query(func.max(Open.openrate).label('max')).filter(Open.sendtime<=time).group_by(Open.sun_name1)
		openrate_avg_nat = sess.query(func.avg(each_openrate.subquery().columns.max)).first()
		vals.append(round(openrate_avg_nat[0], 2))

		openrate_seoul = sess.query(func.max(Open.openrate)).filter(Open.sendtime<=time, Open.sun_name1=='서울').first()
		vals.append(round(openrate_seoul[0], 2))

		openrate_gyeonggi = sess.query(func.max(Open.openrate)).filter(Open.sendtime<=time, Open.sun_name1=='경기').first()
		vals.append(round(openrate_gyeonggi[0], 2))

		rank1 = None

	# elif card_seq is 6:
	#

	elif card_seq is 7:
		vals.append(time.hour)

		region1 = region[0]
		vals.append(region1)

		openrate_region1 = sess.query(func.max(Open.openrate)).filter(Open.sendtime<=time, Open.sun_name1==region1).first()
		vals.append(round(openrate_region1[0], 2))

		each_openrate = sess.query(func.max(Open.openrate).label('max'), Open.sun_name1.label('name')).filter(Open.sendtime<=time).group_by(Open.sun_name1).subquery()
		openrate_avg_nat = sess.query(func.avg(each_openrate.c.max)).first()
		openrate_region1_openrate_avg_nat = openrate_region1[0] - openrate_avg_nat[0]
		vals.append(round(abs(openrate_region1_openrate_avg_nat),2))

		openrate_compare1 = '높은' if openrate_region1_openrate_avg_nat > 0 else '낮은'
		vals.append(openrate_compare1)

		region2 = region[1]
		vals.append(region2)

		openrate_region2 = sess.query(func.max(Open.openrate)).filter(Open.sendtime<=time, Open.sun_name2==region2).first()
		vals.append(round(openrate_region2[0], 2))

		openrate_compare2 = '높은' if (openrate_region2[0] - openrate_avg_nat[0]) > 0 else '낮은'
		vals.append(openrate_compare2)

		openrate_sido_rank1 = sess.query(each_openrate).order_by(each_openrate.c.max.desc()).first()
		vals.append(openrate_sido_rank1[1])

		vals.append(region1)

		each_openrate_region1 = sess.query(func.max(Open.openrate).label('max'), Open.sun_name2.label('name')).filter(Open.sendtime<=time, Open.sun_name1==region1).group_by(Open.sun_name2).subquery()
		openrate_region1_rank1 = sess.query(each_openrate_region1).order_by(each_openrate_region1.c.max.desc()).first()
		vals.append(openrate_region1_rank1[1]) # name
		vals.append(round(openrate_region1_rank1[0], 2)) # rate

		rank1 = None

	# elif card_seq is 8:
		# vals.append(time.hour)
		# ranks = sess.query(OpenView.rank01), OpenView.sun_name2).filter(OpenView.sendtime<=time).group_by(OpenView.suncode).subquery()
		# print(ranks)



	card_data = {}
	for k, v in zip(keys, vals):
		card_data[k] = v

	return card_data, rank1

# def get_count(q):
#     count_q = q.statement.with_only_columns([func.count()]).order_by(None)
#     count = q.session.execute(count_q).scalar()
# 	return count
