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

	regions = [4101]
	region_num = regionCodeCheck(regions[index])
	try:
		# region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.townCode==region_num).first()
		region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.sggCityCode==region_num).first()
	except TypeError:
		raise NoTextError
	print(region1, region2)

	if (region2 == '합계') or (region2 == None): # 시도만
		only_sido = True
	else: # 시 + 구시군
		only_sido = False
	print(only_sido)
	# if only_sido:
	region1_poll = regionPoll(region1, 3)

	region1_openrate = sess.query(func.max(OpenProgress3.openPercent)).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==region1, OpenProgress3.gusigun=='합계').scalar()
	print(region1_openrate)

	subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==region1, OpenProgress3.gusigun=='합계').subquery()

	sub_ranks = sess.query(OpenProgress3).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))

	# region_name = region1
	print(pd.read_sql(sub_ranks.statement, sub_ranks.session.bind))
	
	# else:
	# 	region1_poll = regionPoll(region2, 4)

	# 	# region1_openrate = sess.query(func.max(OpenProgress4.openPercent)).filter(OpenProgress4.datatime<=time, OpenProgress4.sido==region1, OpenProgress4.gusigun==region2).scalar()
	# 	# print(region1_openrate)

	# 	subq = sess.query(func.max(OpenProgress4.serial).label('maxserial'), func.max(OpenProgress4.datatime).label('maxtime')).group_by(OpenProgress4.sggCityCode).filter(OpenProgress4.datatime<=time, OpenProgress4.sido==region1, OpenProgress4.gusigun==region2, OpenProgress4.sggCityCode!=None).subquery()

	# 	sub_ranks = sess.query(OpenProgress4).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime))
	# 	print(pd.read_sql(sub_ranks.statement, sub_ranks.session.bind))

	# 	region1_openrate = sess.query(OpenProgress4.openPercent).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime)).scalar()

	# 	print(region1_openrate)

