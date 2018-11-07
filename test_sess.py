from orm import *
import datetime
from sqlalchemy.sql import func, and_, label
import pandas as pd
from templates import text_templates, background_variations
from queries import NoTextError, josaPick, regionPoll, regionCodeCheck, query_card_data
from collections import Counter
from random import choice

with session_scope() as sess:
	t = '20180614000000'
	time = datetime.datetime.strptime(t, '%Y%m%d%H%M%S')
# 	# time = datetime.datetime.now()
	index = 0
	regions = [4901]
	# regions = [2602]
# 	order = 0
	# candidates = [100131357]
	polls = [3]
	parties = [1,2,3]

	# region1 = '제주특별자치도'
	# region1 = '세종특별자치시'
	# region1 = '서울특별시'
	# region2 = '성동구'

	region_num, special_case = regionCodeCheck(regions[index])

	try:
		region1, region2 = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.sggCityCode==region_num).first()
	except TypeError:
		raise NoTextError

	if (region2 == '합계') or (region2 == None): # 시도만
		only_sido = True
	else: # 시 + 구시군
		only_sido = False
	print(only_sido, special_case)
	print(region1, region2)
	
	region2Poll = regionPoll(region2, 4) # 구시군장
	print(region2Poll)
					
	region2_serial = sess.query(OpenProgress.serial).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==4, OpenProgress.sido==region1, OpenProgress.gusigun==region2, OpenProgress.sggCityCode!=None).order_by(OpenProgress.openPercent.desc()).first()[0]
	print(region2_serial)


	
	if only_sido:
		subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxdate')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.sido==region1, OpenProgress.gusigun=='합계').group_by(OpenProgress.sido).subquery()

		openrate_region1 = sess.query(OpenProgress.openPercent).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxdate)).scalar()

		region_name = region1
		print(region_name, openrate_region1)
	else: # 시+도 : 도의 결과
		# TODO 시 + 도의 개표율
		if special_case:
			if region1 in ['제주특별자치도', '세종특별자치시']:
				subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxdate')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.sido==region1, OpenProgress.gusigun=='합계').group_by(OpenProgress.gusigun).subquery()

				openrate_region1 = sess.query(OpenProgress.openPercent).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxdate)).scalar()

			else:
				subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxdate'), PrecinctCode4.sido, PrecinctCode4.gusigun).outerjoin(PrecinctCode4, and_(OpenProgress.sido==PrecinctCode4.sido, OpenProgress.gusigun==PrecinctCode4.sgg)).filter(OpenProgress.datatime<=time, PrecinctCode4.gusigun==region2, OpenProgress.sido==region1, OpenProgress.electionCode==3).group_by(OpenProgress.gusigun)
				# print(subq.all())
				subq = subq.subquery()
			
				openrate_region1 = sess.query((func.sum(OpenProgress.n_total) + func.sum(OpenProgress.invalid))/func.sum(OpenProgress.tooTotal) * 100).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxdate)).scalar()
				print(openrate_region1)

		else: 
			subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxdate')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.sido==region1, OpenProgress.gusigun==region2).group_by(OpenProgress.gusigun).subquery()

			openrate_region1 = sess.query(OpenProgress.openPercent).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxdate)).scalar()

			# openrate_region1 = sess.query(func.max(OpenProgress.openPercent).label('max'), OpenProgress.sido).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.sido==region1, OpenProgress.gusigun==region2).scalar()

		region_name = region1 + ' ' + region2
		print(region_name, openrate_region1)
		

	if openrate_region1 == 0:
		card_num = '10-1'
	elif openrate_region1 >= 100:
		card_num = '10-2'
	else:
		# openrate_avg_nat = sess.query((func.sum(OpenProgress.n_total)+func.sum(OpenProgress.invalid))/ func.sum(OpenProgress.tooTotal)*100).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계').group_by(OpenProgress.electionCode).scalar()
		s = sess.query(func.max(OpenProgress.n_total).label('n_total'), func.max(OpenProgress.invalid).label('invalid'), func.max(OpenProgress.tooTotal).label('tooTotal')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계').group_by(OpenProgress.sido).subquery()

		openrate_avg_nat = sess.query((func.sum(s.c.n_total) + func.sum(s.c.invalid)) / func.sum(s.c.tooTotal) * 100).scalar()

		openrate_region1_openrate_avg_nat = openrate_region1 - openrate_avg_nat
		compare_region1 = '높은' if openrate_region1_openrate_avg_nat > 0 else '낮은'

		# 시 + 도 개표율의 각 

		# TODO: 
		# sub_r = sess.query(((func.sum(OpenProgress.tooTotal)+func.sum(OpenProgress.invalid)) / func.sum(OpenProgress.yooTotal) * 100).label('rate'), PrecinctCode4.sido, PrecinctCode4.gusigun).outerjoin(PrecinctCode4, and_(OpenProgress.sido==PrecinctCode4.sido, OpenProgress.gusigun==PrecinctCode4.sgg)).filter(OpenProgress.datatime<=time, PrecinctCode4.gusigun!='합계', OpenProgress.sido==region1).group_by(OpenProgress.sido, PrecinctCode4.gusigun)

		# sub_r = sess.query(func.max(OpenProgress.openPercent).label('rate'), PrecinctCode4.sido, PrecinctCode4.gusigun).outerjoin(PrecinctCode4, and_(OpenProgress.sido==PrecinctCode4.sido, OpenProgress.gusigun==PrecinctCode4.sgg)).filter(OpenProgress.electionCode==3, OpenProgress.datatime<=time, PrecinctCode4.gusigun!='합계', OpenProgress.sido==region1).group_by(OpenProgress.sido, PrecinctCode4.gusigun)
		# subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxdate')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.sido==region1, OpenProgress.sggCityCode!=None).group_by(OpenProgress.gusigun).subquery()

		# sub_r = sess.query(OpenProgress.openPercent, OpenProgress.sido, OpenProgress.gusigun).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxdate))
		sub_r = None
		if only_sido:
			subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxdate')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.sido==region1, OpenProgress.gusigun!='합계').group_by(OpenProgress.gusigun).subquery()

			sub_r = sess.query(OpenProgress.openPercent, OpenProgress.sido, OpenProgress.gusigun).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxdate))
		
		else:
			if special_case:
				if region1 in ['제주특별자치도', '세종특별자치시']:
					sub_r = sess.query(func.max(OpenProgress.openPercent).label('rate'), OpenProgress.sido, OpenProgress.gusigun).filter(OpenProgress.electionCode==3, OpenProgress.datatime<=time, OpenProgress.gusigun!='합계', OpenProgress.sido==region1).group_by(OpenProgress.sido, OpenProgress.gusigun)
				else:
					subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxdate'), PrecinctCode4.sido, PrecinctCode4.gusigun.label('gusigun')).outerjoin(PrecinctCode4, and_(OpenProgress.sido==PrecinctCode4.sido, OpenProgress.gusigun==PrecinctCode4.sgg)).filter(OpenProgress.datatime<=time, OpenProgress.gusigun!='합계', OpenProgress.sido==region1, OpenProgress.electionCode==3).group_by(OpenProgress.gusigun)
					# print(subq.all())
					# print(len(subq.all()))
					subq = subq.subquery()
				
					sub_r = sess.query((func.sum(OpenProgress.n_total) + func.sum(OpenProgress.invalid))/func.sum(OpenProgress.tooTotal) * 100, OpenProgress.sido, subq.c.gusigun).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxdate)).group_by(subq.c.gusigun)
					# print(sub_r.all())
					# print(len(sub_r.all()))
			else:
				subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxdate')).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.sido==region1, OpenProgress.gusigun!='합계').group_by(OpenProgress.gusigun).subquery()

				sub_r = sess.query(OpenProgress.openPercent, OpenProgress.sido, OpenProgress.gusigun).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxdate))
			
		print(sub_r.all())