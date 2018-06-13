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

	# region1='경상남도'
	regions = [4803]
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
	if only_sido:
		# subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==region1, OpenProgress3.gusigun=='합계').subquery()
		subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==region1).subquery()

		sub_r = sess.query(OpenProgress3.sido, OpenProgress3.gusigun, OpenProgress3.tooTotal, OpenProgress3.n_total, OpenProgress3.invalid).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime))
		# print(sub_r.all())

		tooTotal_r, n_total_r, invalid_r = sess.query(func.sum(OpenProgress3.tooTotal), func.sum(OpenProgress3.n_total), func.sum(OpenProgress3.invalid)).join(subq, and_(OpenProgress3.serial==subq.c.maxserial, OpenProgress3.datatime==subq.c.maxtime)).first()

		region_name = region1
		if invalid_r == None:
			invalid_r = 0
		try:
			openrate_region1 = (n_total_r) / tooTotal_r * 100
		except TypeError:
			openrate_region1 = 0


	else: # 시+도 : 도의 결과
		subq = sess.query(func.max(OpenProgress4.serial).label('maxserial'), func.max(OpenProgress4.datatime).label('maxtime')).group_by(OpenProgress4.sggCityCode).filter(OpenProgress4.datatime<=time, OpenProgress4.sido==region1, OpenProgress4.sggCityCode!=None).subquery()

		sub_r = sess.query(OpenProgress4.sido, OpenProgress4.gusigun, OpenProgress4.tooTotal, OpenProgress4.n_total, OpenProgress4.invalid).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime))
		
		# print(sub_r.all())

		tooTotal_r, n_total_r, invalid_r = sess.query(func.sum(OpenProgress4.tooTotal), func.sum(OpenProgress4.n_total), func.sum(OpenProgress4.invalid)).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime)).first()

		region_name = region1 + ' ' + region2
		if invalid_r == None:
			invalid_r = 0
		try:
			openrate_region1 = (n_total_r) / tooTotal_r * 100
		except TypeError:
			openrate_region1 = 0


	print(openrate_region1)
	
	# if only_sido:
	sub = sess.query(OpenProgress3.gusigun, func.max(OpenProgress3.tooTotal).label('tooTotal'), func.max(OpenProgress3.n_total).label('n_total'), func.max(OpenProgress3.invalid).label('invalid')).filter(OpenProgress3.sido==region1, OpenProgress3.gusigun!='합계',OpenProgress3.datatime<=time).group_by(OpenProgress3.townCode).subquery()
	# else:


	tooTotal, n_total, invalid = sess.query(func.sum(sub.c.tooTotal), func.sum(sub.c.n_total), func.sum(sub.c.invalid)).first()

	if invalid == None:
		invalid = 0
	try:		
		openrate_avg_nat = (n_total) / tooTotal * 100
	except TypeError:
		raise NoTextError

	openrate_region1_openrate_avg_nat = openrate_region1 - openrate_avg_nat
	compare_region1 = '높은' if openrate_region1_openrate_avg_nat > 0 else '낮은'
