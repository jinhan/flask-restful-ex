from orm import *
import datetime
from sqlalchemy.sql import func, and_
import pandas as pd
from templates import text_templates, background_variations

with session_scope() as sess:
	t = '20180613230000'
	time = datetime.datetime.strptime(t, '%Y%m%d%H%M%S')
	index = 0
	regions = [1100]
	order = 0

	try:
		region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.townCode==regions[index]).first()
	except TypeError:
		raise NoTextError

	subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.townCode).filter(OpenProgress.datatime<=time, OpenProgress.gusigun!='합계', OpenProgress.electionCode==4, OpenProgress.sido==region1).subquery()

	sub_r = sess.query(OpenProgress.gusigun, OpenProgress.tooTotal, OpenProgress.n_total, OpenProgress.invalid).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxtime))
	map_data = []
	for r, tooTotal, n_total, invalid in sub_r.all():
		if invalid == None:
			invalid = 0
		v = (n_total + invalid) / tooTotal
		map_data.append({'name':r, 'value':v})
	map_data = list({v['name']:v for v in map_data}.values())
	print(map_data)

	# if polls[index] == 2: # 국회의원
	# 	poll, poll_num_sunname = sess.query(SgTypecode.sgName, func.count(PrecinctCode.sgg)).join(PrecinctCode, PrecinctCode.electionCode==SgTypecode.sgTypecode).filter(SgTypecode.sgTypecode==polls[index]).first()

	# 	subq = sess.query(func.max(OpenProgress2.serial).label('maxserial'), func.max(OpenProgress2.datatime).label('maxtime')).group_by(OpenProgress2.sgg).filter(OpenProgress2.datatime<=time).subquery()

	# 	sub = sess.query(OpenProgress2.sgg, OpenProgress2.tooTotal, OpenProgress2.n_total, OpenProgress2.invalid).join(subq, and_(OpenProgress2.serial==subq.c.maxserial, OpenProgress2.datatime==subq.c.maxtime))

	# 	tooTotal, n_total, invalid = sess.query(func.sum(OpenProgress2.tooTotal), func.sum(OpenProgress2.n_total), func.sum(OpenProgress2.invalid)).join(subq, and_(OpenProgress2.serial==subq.c.maxserial, OpenProgress2.datatime==subq.c.maxtime)).first()

	# elif polls[index] == 3:
	# 	poll, poll_num_sunname = sess.query(SgTypecode.sgName, func.count(PrecinctCode.cityCode)).join(PrecinctCode, PrecinctCode.electionCode==SgTypecode.sgTypecode).filter(SgTypecode.sgTypecode==polls[index]).first()

	# 	subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.gusigun=='합계').subquery()

	# 	sub = sess.query(OpenProgress3.sido, OpenProgress3.tooTotal, OpenProgress3.n_total, OpenProgress3.invalid).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))

	# 	tooTotal, n_total, invalid = sess.query(func.sum(OpenProgress3.tooTotal), func.sum(OpenProgress3.n_total), func.sum(OpenProgress3.invalid)).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime)).first()

	# elif polls[index] == 4:
	# 	poll, poll_num_sunname = sess.query(SgTypecode.sgName, func.count(PrecinctCode.gusigun)).join(PrecinctCode, PrecinctCode.electionCode==SgTypecode.sgTypecode).filter(SgTypecode.sgTypecode==polls[index]).first()

	# 	subq = sess.query(func.max(OpenProgress4.serial).label('maxserial'), func.max(OpenProgress4.datatime).label('maxtime')).group_by(OpenProgress4.townCode).filter(OpenProgress4.datatime<=time).subquery()

	# 	sub = sess.query(OpenProgress4.sido, OpenProgress4.tooTotal, OpenProgress4.n_total, OpenProgress4.invalid).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime))

	# 	tooTotal, n_total, invalid = sess.query(func.sum(OpenProgress4.tooTotal), func.sum(OpenProgress4.n_total), func.sum(OpenProgress4.invalid)).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime)).first()

	# elif polls[index] == 11:
	# 	poll, poll_num_sunname = sess.query(SgTypecode.sgName, func.count(PrecinctCode.cityCode)).join(PrecinctCode, PrecinctCode.electionCode==SgTypecode.sgTypecode).filter(SgTypecode.sgTypecode==polls[index]).first()

	# 	subq = sess.query(func.max(OpenProgress11.serial).label('maxserial'), func.max(OpenProgress11.datatime).label('maxtime')).group_by(OpenProgress11.sido).filter(OpenProgress11.datatime<=time, OpenProgress11.gusigun=='합계').subquery()

	# 	sub = sess.query(OpenProgress11.sido, OpenProgress11.tooTotal, OpenProgress11.n_total, OpenProgress11.invalid).join(subq, and_(OpenProgress11.serial==subq.c.maxserial, OpenProgress11.datatime==subq.c.maxtime))

	# 	tooTotal, n_total, invalid = sess.query(func.sum(OpenProgress11.tooTotal), func.sum(OpenProgress11.n_total), func.sum(OpenProgress11.invalid)).join(subq, and_(OpenProgress11.serial==subq.c.maxserial, OpenProgress11.datatime==subq.c.maxtime)).first()

	# else:
	# 	raise NoTextError

	# poll_openrate_ranks = []
	# if invalid == None:
	# 	invalid = 0

	# try:
	# 	poll_openrate_nat_avg = (n_total + invalid) / tooTotal * 100
		
	# 	for r, tooTotal, n_total, invalid in sub.all():
	# 		if invalid == None:
	# 			invalid = 0
	# 		v = (n_total + invalid) / tooTotal
	# 		poll_openrate_ranks.append({'name':r, 'value':v})
		
	# 	poll_openrate_ranks = sorted(poll_openrate_ranks, key=lambda x: x['value'], reverse=True)
	# 	# print(poll_openrate_ranks)
	# 	poll_openrate_ranks = list({v['name']:v for v in poll_openrate_ranks}.values())
	# 	print(poll_openrate_ranks)

	# 	if poll_openrate_nat_avg >= 100:
	# 		data = {
	# 			'hour': hourConverter(time.hour),
	# 			'poll': poll,
	# 		}
	# 		card_num = '11-2'
	# 		text = text_templates[card_num].format(**data)
	# 		meta_card = {
	# 			'order': order,
	# 			'type': 'rate',
	# 			'party': 'default',
	# 			'data': {
	# 				'title': poll + ', 개표 완료',
	# 				'rate': 100,
	# 				'text': text,
	# 			},
	# 			'debugging': card_num,
	# 		}
	# 	else:
	# 		data = {
	# 			'poll_num_sunname': poll_num_sunname,
	# 			'poll': poll,
	# 			'poll_openrate_rank1': poll_openrate_ranks[0]['name'],
	# 			'poll_openrate_rank1_rate': round(poll_openrate_ranks[0]['value'] * 100, 2),
	# 			'poll_openrate_rank2': poll_openrate_ranks[1]['name'],
	# 			'poll_openrate_rank2_rate': round(poll_openrate_ranks[1]['value'] * 100, 2),
	# 			'poll': poll, 
	# 			'poll_openrate_nat_avg': round(poll_openrate_nat_avg, 2),
	# 		}
	# 		card_num = '11'
	# 		text = text_templates[card_num].format(**data)
			
	# 		meta_card = {
	# 			'order': order,
	# 			'type': 'graph',
	# 			'party': 'default',
	# 			'data': {
	# 				'graph_data': {
	# 					'type': 'region',
	# 					'data': poll_openrate_ranks[:10],
	# 				},
	# 				'text': text,
	# 			}, 
	# 			'debugging': card_num,
	# 		}
	# except TypeError:
	# 	if tooTotal == None:
	# 		data = {
	# 			'hour': hourConverter(time.hour),
	# 			'poll': poll,
	# 			'josa': josaPick(poll, '은'),
	# 		}
	# 		card_num = '11-1'
	# 		text = text_templates[card_num].format(**data)
	# 		meta_card = {
	# 			'order': order,
	# 			'type': 'rate',
	# 			'party': 'default',
	# 			'data': {
	# 				'title': poll + ' 개표 준비중',
	# 				'rate': 0,
	# 				'text': text,
	# 			},
	# 			'debugging': card_num,
	# 		}
	# 	else:
	# 		raise NoTextError
	
	# # print(meta_card)