from string import Formatter
import datetime as dt

import pandas as pd
from sqlalchemy import create_engine
import traceback

from templates import text_templates, img_templates, party2bg
import dbinfo


def generateMeta(args):
		hour = dt.datetime.now().hour
		card_seqs = getCardSeqs(args, hour)

		meta = {}
		meta['card_count'] = len(card_seqs)
		meta_cards = []
		for i, card_seq in enumerate(card_seqs):
				meta_card = {}
				meta_card['order'] = i

				txt_vis, img_temp = generateTextsImgsViss(args, hour, card_seq)
				meta_card['type'] = img_temp
				meta_card['data'] = txt_vis

				meta_cards.append(meta_card)
		meta['cards'] = meta_cards

		return meta


def getCardSeqs(args, hour):

	card_seqs = [1,2,1,2]
	return card_seqs


# each by card
def generateTextsImgsViss(args, hour, card_seq):
		# db connection
		try:
			engine = create_engine('mysql+pymysql://{id}:{pw}@{host}/election2018?charset=utf8mb4'.format(id=dbinfo.id, pw=dbinfo.pw, host=dbinfo.host), convert_unicode=True, echo=False)
			conn = engine.connect()
			print("db connected")
		except:
			traceback.print_exc()

		# db queries
		# 한번에 필요한 걸 다 쿼리해서 가지고 있는것
		# 카드 타입별로 쿼리를 작성해서 가지고 있는 것
		# 미리미리 aggregation해서 테이블에 가지고 있는 것

		# vis gen


		# db to fields
		kws = [kw for _, kw, _, _ in Formatter().parse(text_templates[card_seq]) if kw]
		data = {}
		for kw in kws:
				data[kw] = '아이유'
		text = text_templates[card_seq].format(**data)

		# img template gen
		img_temp = img_templates[card_seq]
		# img_temp['bg'] = party2bg[party]

		vis = "path.png"

		try:
			conn.close()
		except:
			pass

		txt_vis = {'text': text, 'vis': vis} #'raw': raw_data
		return txt_vis, img_temp
