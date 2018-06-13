from orm import *
import datetime
from sqlalchemy.sql import func, and_, label
import pandas as pd
from templates import text_templates, background_variations
from queries import NoTextError, josaPick, regionPoll, regionCodeCheck
from collections import Counter
from random import choice

with session_scope() as sess:
	# t = '20180613180000'
	# time = datetime.datetime.strptime(t, '%Y%m%d%H%M%S')
	time = datetime.datetime.now()
	index = 0
	# regions = [1100]
	order = 0
	candidates = [100128761]

	if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
		t = 23
	else:
		t = time.hour

	polls = [4]
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

	# try:
	poll_openrate_nat_avg = (n_total) / tooTotal * 100
	# sss = sess.query(func.max(OpenProgress11.serial).label('maxserial'), func.max(OpenProgress11.datatime).label('maxtime')).group_by(OpenProgress11.sido).filter(OpenProgress11.datatime<=time, OpenProgress11.gusigun=='합계')

	for r, tooTotal, n_total, invalid in sub.all():
		if invalid == None:
			invalid = 0
		v = (n_total) / tooTotal
		poll_openrate_ranks.append({'name':r, 'value':v})
	
	
	poll_openrate_ranks = list({v['name']:v for v in poll_openrate_ranks}.values())
	poll_openrate_ranks = sorted(poll_openrate_ranks, key=lambda x: x['value'], reverse=True)
	print(poll_openrate_ranks)
	
			#print(poll_openrate_ranks)
	
	# else:
	# 	region1_poll = regionPoll(region2, 4)

	# 	# region1_openrate = sess.query(func.max(OpenProgress4.openPercent)).filter(OpenProgress4.datatime<=time, OpenProgress4.sido==region1, OpenProgress4.gusigun==region2).scalar()
	# 	# print(region1_openrate)

	# 	subq = sess.query(func.max(OpenProgress4.serial).label('maxserial'), func.max(OpenProgress4.datatime).label('maxtime')).group_by(OpenProgress4.sggCityCode).filter(OpenProgress4.datatime<=time, OpenProgress4.sido==region1, OpenProgress4.gusigun==region2, OpenProgress4.sggCityCode!=None).subquery()

	# 	sub_ranks = sess.query(OpenProgress4).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime))
	# 	print(pd.read_sql(sub_ranks.statement, sub_ranks.session.bind))

	# 	region1_openrate = sess.query(OpenProgress4.openPercent).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime)).scalar()

	# 	print(region1_openrate)

