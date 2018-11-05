import datetime
from orm import *
from sqlalchemy.sql import func, and_
from random import randint
from timeit import default_timer as timer
from queries import query_card_data, NoTextError, regionCodeCheck
import uuid
import ast
# from templates_parser import templates_parser
from text_templates import text_templates


deploy_mode = False

def generateMeta(args):
	with session_scope() as sess:
		# text_templates = templates_parser()
		
		polls = args['type']
		regions = args['region']
		parties = args['party']
		candidates = args['candidate']
		# TODO
		time = datetime.datetime.strptime(args['time'], '%Y%m%d%H%M%S')
		# print(datetime.datetime.now())
		# time = datetime.datetime.now()

		serial_current = str(uuid.uuid4().hex)
		arguments = args
		# if 'time' in arguments:
		# 	del arguments['time']

		# 데이터가 업데이트 되는 시간
		# 쿼리로 임의로 시간을 시뮬레이셔할때는
		if time > datetime.datetime(2018, 6, 13, 18, 59, 59):
			t = 18
		else:
			t = time.hour

		time_update = []
		# TODO:
		try:
			time_update.append(sess.query(VoteProgressLatest.datatime).order_by(VoteProgressLatest.datatime.desc()).first()[0])
		except TypeError:
			pass
		try:
			time_update.append(sess.query(OpenProgress2.datatime).order_by(OpenProgress2.datatime.desc()).first()[0])
		except TypeError:
			pass
		try:
			time_update.append(sess.query(OpenProgress3.datatime).order_by(OpenProgress3.datatime.desc()).first()[0])
		except TypeError:
			pass
		try:
			time_update.append(sess.query(OpenProgress4.datatime).order_by(OpenProgress4.datatime.desc()).first()[0])
		except TypeError:
			pass
		try:
			time_update.append(sess.query(OpenProgress11.datatime).order_by(OpenProgress11.datatime.desc()).first()[0])
		except TypeError:
			pass

		serial_ontable = sess.query(QueryTime.serial).filter(QueryTime.args==str(arguments), QueryTime.times==str(time_update)).first() # 값이 나오면 같은게 있다는 것
		
		if deploy_mode:
			if serial_ontable != None:
				serial_ontable = serial_ontable[0]
			# print("serial:  ", serial_ontable)
			meta_previous = sess.query(MetaCards.meta).filter(MetaCards.serial==serial_ontable).scalar()
		else:
			serial_ontable = None
			mete_previous = None

		if (serial_ontable != None) and (meta_previous != None): # 전에 있으면
			meta = ast.literal_eval(meta_previous)
			meta['updated'] = False
		else: # 전에 없으면
			if deploy_mode:
				row = QueryTime(serial=serial_current, args=str(arguments), times=str(time_update))
				sess.add(row)
				# sess.commit()

			card_seqs, seqs_type, template = getCardSeqs(sess, polls, regions, parties, candidates, time)
			# print(template, card_seqs)
			
			meta = {}
			meta['scenario'] = str(card_seqs)
			meta['updated'] = True
			meta['serial'] = serial_current
			meta['card_count'] = len(card_seqs)
			meta['design_variation'] = randint(1,4)
			meta_cards = []

			index = 0
			for i, card_seq in enumerate(card_seqs):
				if card_seqs[i-1] is card_seq:
					index += 1
				else:
					index = 0

				order = i+1
				
				try:
					meta_card = query_card_data(text_templates, sess, order, index, polls, regions, parties, candidates, time, card_seq, seqs_type, template)
				except NoTextError:
					print("pass:    ", card_seq)
					continue
				meta_cards.append(meta_card)
			# end for
			# try:
			meta_cards = list({v['data']['text']:v for v in meta_cards}.values())
			meta['cards'] = meta_cards
			
			if deploy_mode:
				meta_row = MetaCards(serial=serial_current, meta=str(meta))
				sess.add(meta_row)
				# sess.commit()

	return meta


def getCardSeqs(sess, polls, regions, parties, candidates, time):
	# vote에서 중요
	if time > datetime.datetime(2018, 6, 13, 18, 59, 59):
		t = 18
	else:
		t = time.hour
	
	if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
		t2 = 23
	else:
		t2 = time.hour

	card_seqs = []

	if t2 > 18:
		if (len(candidates) > 0):
			# print(1)
			try:
				candidate, candidate_region, candidate_poll_code = sess.query(CandidateInfo.name, CandidateInfo.sggName, CandidateInfo.sgTypecode).filter(CandidateInfo.huboid==candidates[0]).first()
				# print(candidate_region)
			except TypeError:
				raise NoTextError

			if candidate_poll_code == 2: # 국회의원
				openrate = sess.query(func.max(OpenProgress.openPercent)).filter(OpenProgress.sgg==candidate_region, OpenProgress.datatime<=time, OpenProgress.sggCityCode!=None).scalar() # , 
			elif candidate_poll_code == 3:
				openrate = sess.query(func.max(OpenProgress.openPercent)).filter(OpenProgress.sido==candidate_region, OpenProgress.gusigun=='합계',OpenProgress.datatime<=time).scalar() # ,  
			elif candidate_poll_code == 4:
				openrate = sess.query(func.max(OpenProgress.openPercent)).filter(OpenProgress.gusigun==candidate_region, OpenProgress.datatime<=time, OpenProgress.sggCityCode!=None).scalar() # , 
			elif candidate_poll_code == 11:
				openrate = sess.query(func.max(OpenProgress.openPercent)).filter(OpenProgress.sido==candidate_region, OpenProgress.gusigun=='합계',OpenProgress.datatime<=time).scalar() # , 
			else:
				openrate = None
			# print(candidate_poll_code, openrate)

		elif (len(candidates) == 0) and (len(regions) > 0):
			# print(2)
			region_num = regionCodeCheck(regions[0])
			try:
				region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.sggCityCode==region_num).first()
			except TypeError:
				raise NoTextError

			openrate = sess.query(func.max(OpenProgress.openPercent)).filter(OpenProgress.datatime<=time, OpenProgress.sido==region1, OpenProgress.gusigun=='합계').scalar()
			# print(openrate)

		# 	parites
		elif (len(candidates) == 0) and (len(regions) == 0) and (len(polls) > 0):
			# print(3)
			if polls[0] == 2:
				s = sess.query(OpenProgress.sgg, func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==2, OpenProgress.sggCityCode!=None).group_by(OpenProgress.sgg)

			elif polls[0] == 3:
				s = sess.query(OpenProgress.sido, func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계').group_by(OpenProgress.sido)
			
			elif polls[0] == 4:
				s = sess.query(OpenProgress.gusigun, func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==4, OpenProgress.sggCityCode!=None).group_by(OpenProgress.gusigun)
			
			elif polls[0] == 11:
				s = sess.query(OpenProgress.sido, func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==11, OpenProgress.gusigun=='합계').group_by(OpenProgress.sido)
			
			openrate = sess.query((func.sum(s.subquery().c.n_total) + func.sum(s.subquery().c.invalid)) / func.sum(s.subquery().c.tooTotal) * 100).scalar()
	
		else:
			# print(4)
			s = sess.query(OpenProgress.sido, func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계').group_by(OpenProgress.sido)

			openrate = sess.query((func.sum(s.subquery().c.n_total) + func.sum(s.subquery().c.invalid)) / func.sum(s.subquery().c.tooTotal) * 100).scalar()
	else:
		openrate = 0

	if openrate == None:
		openrate = 0

	# print("openrate:     ", openrate)
	
	if t2 <= 18: # 투표중
		card_seqs.extend([1, 2, 3, 6, 23]) # 6 특이사항
		card_seqs.extend([4] * len(regions))
		card_seqs.extend([5] * len(candidates))
		card_seqs.sort()
		seqs_type = 0
		template = 1
	# 어떤 선거의 개표율 10 기준?
	elif (t2 > 18) and (openrate < 10): # 투표마감이후
		card_seqs.extend([1, 2, 3, 6, 22, 23]) # 6 특이사항
		card_seqs.extend([4] * len(regions))
		card_seqs.extend([5] * len(candidates))
		card_seqs.sort()
		seqs_type = 0
		template = 2
	elif (t2 > 18) and (openrate >= 10) and (openrate < 30): # 개표율 10% 이상
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
		template = 3
	elif (t2 > 18) and (openrate >= 30): # 개표율 30% 이상
		card_seqs.extend([1, 2, 7, 15, 20, 23]) # 13, 20 특이사항
		card_seqs.extend([10] * len(regions))
		card_seqs.extend([11] * len(polls))
		card_seqs.extend([12] * len(candidates))
		card_seqs.extend([16] * len(regions))
		card_seqs.extend([17] * len(candidates))
		card_seqs.extend([18] * len(parties))
		card_seqs.sort()
		card_seqs.insert(1, 21)
		seqs_type = 1
		if openrate < 100:
			template = 4
		else:
			template = 5
		# 내가 선택한 선거에서 한명이라도 당선 확정이 나오는 경우 21번을 index 1에 insert
	# else:
	# 	seqs_type = 0
	return card_seqs, seqs_type, template


if __name__ == '__main__':
	# print(VoteProgressLatest)




