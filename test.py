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

	region1 = "경상남도"
	subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==region1).subquery()

	sub_r = sess.query(OpenProgress3.sido, OpenProgress3.gusigun, OpenProgress3.tooTotal, OpenProgress3.n_total, OpenProgress3.invalid).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))
			# print(sub_r.all())

	tooTotal_r, n_total_r, invalid_r = sess.query(func.sum(OpenProgress3.tooTotal), func.sum(OpenProgress3.n_total), func.sum(OpenProgress3.invalid)).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime)).first()
	print((n_total_r) / tooTotal_r * 100)
	
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

