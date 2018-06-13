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

	# toorate_region1_sub = sess.query(func.max(VoteProgress.tooRate), VoteProgress.gusigun).filter(VoteProgress.timeslot<=t, VoteProgress.sido=='경기도', VoteProgress.gusigun!='합계').group_by(VoteProgress.gusigun).order_by(func.max(VoteProgress.tooRate).desc(), func.max(VoteProgress.tooTotal).desc()).all()
	# print(toorate_region1_sub)

	# candidate_region_sub = sess.query(func.max(VoteProgress.tooRate), VoteProgress.gusigun,VoteProgress.townCode).filter(VoteProgress.timeslot<=t, VoteProgress.sido=='경기도', VoteProgress.gusigun!='합계').group_by(VoteProgress.gusigun).all()
	# print(candidate_region_sub)

	# d = sess.query(VoteProgressLatest.townCode, PrecinctCode4.gusigun,  func.sum(VoteProgressLatest.yooToday).label('yooToday'), func.sum(VoteProgressLatest.yooEarly).label('yooEarly'), func.sum(VoteProgressLatest.tooToday).label('tooToday'), func.sum(VoteProgressLatest.tooEarly).label('tooEarly')).outerjoin(PrecinctCode4, and_(VoteProgressLatest.sido==PrecinctCode4.sido, VoteProgressLatest.gusigun==PrecinctCode4.sgg)).filter(VoteProgressLatest.timeslot<=t, PrecinctCode4.gusigun=='천안시', VoteProgressLatest.sido=='충청남도').group_by(VoteProgressLatest.sido, PrecinctCode4.gusigun)

	# print(d.all())

	# subq = sess.query(func.max(OpenProgress3.serial).label('maxserial'), func.max(OpenProgress3.datatime).label('maxtime')).group_by(OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.gusigun=='합계').subquery()
	# subq = sess.query(func.max(OpenProgress4.serial).label('maxserial'), func.max(OpenProgress4.datatime).label('maxtime')).group_by(OpenProgress4.sggCityCode).filter(OpenProgress4.datatime<=time, OpenProgress4.gusigun=='예산군', OpenProgress4.sggCityCode!=None).subquery()

	# sub_ranks = sess.query(OpenProgress4).join(subq, and_(OpenProgress4.serial==subq.c.maxserial, OpenProgress4.datatime==subq.c.maxtime))
	# # print(sub_ranks.all())
	# ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
	# print(ranksDf)

	# d = sess.query(OpenProgress11.openPercent, OpenProgress11.gusigun).filter(OpenProgress11.datatime<=time, OpenProgress11.sido=='서울특별시', OpenProgress11.gusigun!='합계').all()
	# print(d)
	# _, _, yooToday, yooEarly, tooToday, tooEarly = sess.query(VoteProgressLatest.townCode, PrecinctCode4.gusigun,  func.sum(VoteProgressLatest.yooToday).label('yooToday'), func.sum(VoteProgressLatest.yooEarly).label('yooEarly'), func.sum(VoteProgressLatest.tooToday).label('tooToday'), func.sum(VoteProgressLatest.tooEarly).label('tooEarly')).outerjoin(PrecinctCode4, and_(VoteProgressLatest.sido==PrecinctCode4.sido, VoteProgressLatest.gusigun==PrecinctCode4.sgg)).filter(VoteProgressLatest.timeslot<=t, PrecinctCode4.gusigun=='수원시', VoteProgressLatest.sido=='경기도').group_by(VoteProgressLatest.sido, PrecinctCode4.gusigun).first()
	# print(yooToday, yooEarly, tooToday, tooEarly)
	# each_toorate = sess.query(VoteProgress.townCode, PrecinctCode4.gusigun.label('gusigun'), func.max(VoteProgress.yooToday).label('yooToday'), func.max(VoteProgress.yooEarly).label('yooEarly'), func.max(VoteProgress.tooToday).label('tooToday'), func.max(VoteProgress.tooEarly).label('tooEarly')).outerjoin(PrecinctCode4, and_(VoteProgress.gusigun==PrecinctCode4.sgg, VoteProgress.sido==PrecinctCode4.sido)).filter(VoteProgress.timeslot<=t, VoteProgress.sido=='경기도', Vote
	# Progress.gusigun!='합계').group_by(PrecinctCode4.sido. PrecinctCode4.gusigun).subquery()
	
	# print(each_toorate.all())
	
	# print(sess.query(each_toorate.subquery()).group_by(each_toorate.subquery().c.gusigun).all())
	
	# dd = sess.query(func.sum(each_toorate.c.yooToday), func.sum(each_toorate.c.yooEarly), func.sum(each_toorate.c.tooToday), func.sum(each_toorate.c.tooEarly))

	# print(dd.all())

	# dd = sess.query(func.sum(each_toorate.subquery().c.yooToday), func.sum(each_toorate.subquery().c.yooEarly), func.sum(each_toorate.subquery().c.tooToday), func.sum(each_toorate.subquery().c.tooEarly)).group_by(each_toorate.gusigun)
	# print(dd.all())

	# s = "select a.timeslot, b.sido, b.gusigun, a.cityCode, a.townCode, sum(a.yooToday) as yooToday, sum(a.yooEarly) as yooEarly, sum(a.tooToday) as tooToday, sum(a.tooEarly) as tooEarly, sum(a.tooTotal) as tooTotal, tooTotal / yooTotal * 100 as tooRate, min(isCompleted) as isCompleted from VoteProgressLatest a left outer join PrecinctCode4 b on a.sido = b.sido and a.gusigun = b.sgg where b.gusigun not like '합계' group by a.sido, b.gusigun"
	# print(sess.execute(s).fetchall())


	# subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.townCode).filter(OpenProgress.datatime<=time, OpenProgress.gusigun!='합계', OpenProgress.electionCode==4, OpenProgress.sido=='경기도').subquery()

	# sub_r = sess.query(OpenProgress.gusigun, OpenProgress.tooTotal, OpenProgress.n_total, OpenProgress.invalid).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxtime))
	# print(sub_r.all())

	
	# print(ranks)
	# map_data = []
	# for v, r in ranks:
	# 	if r == '합계':
	# 		pass
	# 	else:
	# 		map_data.append({'name':r, 'value':float(v)*0.01})
	# 
	# region1='서울특별시'
	# region2='서초구'
	# _, _, yooTotal, tooTotal = sess.query(VoteProgressLatest.townCode, PrecinctCode4.gusigun,  func.sum(VoteProgressLatest.yooTotal).label('yooTotal'), func.sum(VoteProgressLatest.tooTotal).label('tooTotal')).outerjoin(PrecinctCode4, and_(VoteProgressLatest.sido==PrecinctCode4.sido, VoteProgressLatest.gusigun==PrecinctCode4.sgg)).filter(VoteProgressLatest.timeslot<=t, PrecinctCode4.gusigun==region2, VoteProgressLatest.sido==region1).group_by(VoteProgressLatest.sido, PrecinctCode4.gusigun).first()
	# print((tooTotal) / (yooTotal) * 100)

	# each_toorate = sess.query(func.max(VoteProgressLatest.yooTotal).label('yooTotal'), func.max(VoteProgressLatest.tooTotal).label('tooTotal')).filter(VoteProgressLatest.timeslot<=t, VoteProgressLatest.gusigun=='합계').group_by(VoteProgressLatest.sido).subquery()

	# yooTotal_a, tooTotal_a = sess.query(func.sum(each_toorate.c.yooTotal), func.sum(each_toorate.c.tooTotal)).first()
	# toorate_avg_nat = (tooTotal_a) / (yooTotal_a) * 100
	# print(toorate_avg_nat)

	# each_toorate_p = sess.query(func.max(PastVoteProgress.yooTotal).label('yooTotal'), func.max(PastVoteProgress.tooTotal).label('tooTotal')).filter(PastVoteProgress.timeslot<=t, PastVoteProgress.gusigun=='합계').group_by(PastVoteProgress.sido).subquery()
	# yooTotal_p, tooTotal_p = sess.query(func.sum(each_toorate_p.c.yooTotal), func.sum(each_toorate_p.c.tooTotal)).first()
	
	# try:
	# 	past_toorate = (tooTotal_p) / (yooTotal_p) * 100
	# except TypeError:
	# 	raise NoTextError
	# print(past_toorate)

	# each_toorate_p = sess.query(func.max(PastVoteProgress.yooTotal).label('yooTotal'), func.max(PastVoteProgress.tooTotal).label('tooTotal')).filter(PastVoteProgress.timeslot<=t, PastVoteProgress.gusigun=='합계').group_by(PastVoteProgress.sido)
	# print(each_toorate_p.all())

	# each_toorate = sess.query((VoteProgressLatest.yooTotal).label('yooTotal'), (VoteProgressLatest.tooTotal).label('tooTotal')).filter( VoteProgressLatest.gusigun!='합계').subquery()

	# yooTotal, tooTotal = sess.query(func.sum(each_toorate.c.yooTotal), func.sum(each_toorate.c.tooTotal)).first()

	# print(tooTotal/yooTotal*100)
	# region1 = '경기도'
	# yoo, too = sess.query(func.sum(VoteProgressLatest.yooTotal).label('yooTotal'), func.sum(VoteProgressLatest.tooTotal).label('tooTotal')).filter(VoteProgressLatest.sido==region1, VoteProgressLatest.gusigun!='합계').first()
	# too_too/yoo*100)

	# sido_rank1 = sess.query(VoteProgressLatest.sido).filter(VoteProgressLatest.timeslot==t, VoteProgressLatest.gusigun!='합계').order_by(func.max(VoteProgressLatest.tooRate).desc()).first()[0]
	# print(sido_rank1)

	# sido_rank1 = sess.query(VoteProgress.sido).filter(VoteProgress.timeslot==t, VoteProgress.gusigun=='합계').group_by(VoteProgress.sido).order_by(func.max(VoteProgress.tooRate).desc()).first()[0]
	# print(sido_rank1)
	# each_toorate = sess.query(func.max(VoteProgress.yooTotal).label('yooTotal'), func.max(VoteProgress.tooTotal).label('tooTotal')).filter(VoteProgress.timeslot<=t, VoteProgress.gusigun=='합계').group_by(VoteProgress.sido).subquery()
	# yooTotal, tooTotal = sess.query(func.sum(each_toorate.c.yooTotal), func.sum(each_toorate.c.tooTotal)).first()
		
	# toorate_avg_nat = (tooTotal) / (yooTotal) * 100
	# print(toorate_avg_nat)

	# each_toorate = sess.query((VoteProgressLatest.yooTotal).label('yooTotal'), (VoteProgressLatest.tooTotal).label('tooTotal')).filter(VoteProgressLatest.timeslot==t, VoteProgressLatest.gusigun!='합계').subquery()

	# yooTotal, tooTotal = sess.query(func.sum(each_toorate.c.yooTotal), func.sum(each_toorate.c.tooTotal)).first()
	
	# try:	
	# 	toorate_avg_nat = (tooTotal) / (yooTotal) * 100
	# except TypeError:
	# 	raise NoTextError
	# print(toorate_avg_nat)


	# ranks = sess.query(func.max(VoteProgressLatest.tooRate).label('max'), VoteProgressLatest.sido).filter(VoteProgressLatest.timeslot==t).group_by(VoteProgressLatest.sido, VoteProgressLatest.gusigun!='합계').order_by(func.max(VoteProgressLatest.tooRate).desc(), func.max(VoteProgressLatest.tooTotal).desc()).all()

	# print(ranks)
	# print(', '.join(rank[1] for rank in ranks[1:3]))

	# ranks = sess.query(func.max(VoteProgressLatest.tooRate).label('max'), VoteProgressLatest.sido).filter(VoteProgressLatest.timeslot<=t).group_by(VoteProgressLatest.sido, VoteProgressLatest.gusigun!='합계').order_by(func.max(VoteProgressLatest.tooRate).desc(), func.max(VoteProgressLatest.tooTotal).desc()).all()

	# print(ranks)
	# sido_rank1 = sess.query(VoteProgress.sido).filter(VoteProgress.timeslot<=t, VoteProgress.gusigun=='합계').group_by(VoteProgress.sido).order_by(func.max(VoteProgress.tooRate).desc()).first()[0]
	# print(sido_rank1)

	# # sido_rank1 = sess.query(VoteProgressLatest.sido).filter(VoteProgressLatest.timeslot==t, VoteProgressLatest.gusigun!='합계').group_by(VoteProgress.sido).order_by(func.max(VoteProgress.tooRate).desc()).first()[0]
	# # print(sido_rank1)
	# print(len(sess.query(VoteProgressLatest.timeslot).group_by(VoteProgressLatest.timeslot).all()))

	# region1 = "세종특별자치시"
	# # region1 = "경기도"
	# toorate_region1_sub = sess.query(VoteProgressLatest.townCode, PrecinctCode4.gusigun,  func.sum(VoteProgressLatest.yooTotal).label('yooTotal'), func.sum(VoteProgressLatest.tooTotal).label('tooTotal')).outerjoin(PrecinctCode4, and_(VoteProgressLatest.sido==PrecinctCode4.sido, VoteProgressLatest.gusigun==PrecinctCode4.sgg)).filter(VoteProgressLatest.gusigun!='합계', VoteProgressLatest.sido==region1).group_by(VoteProgressLatest.sido, PrecinctCode4.gusigun)
	# # print(toorate_region1_sub.all())
	# map_data = []
	# for tc, r, yooTotal, tooTotal in toorate_region1_sub:
	# 	print(tc)
	# 	if tc == 4901:
	# 		r = '제주특별자치도'
	# 	elif tc == 5101:
	# 		r = '세종특별자치시'
	# 	try:
	# 		v = (tooTotal) / (yooTotal)
	# 	except TypeError:
	# 		v = 0
	# 	map_data.append({'name':r, 'value':float(v)})
	# print(map_data)


	d = sess.query(OpenProgress3.openPercent.label('max'), OpenProgress3.sido).filter(OpenProgress3.datatime<=time, OpenProgress3.gusigun=='합계').group_by(OpenProgress3.cityCode).order_by(func.max(OpenProgress3.openPercent).desc(), func.max(OpenProgress3.n_total).desc()).all()
	print(d)
	candidate_region = '군위군'
	openrate = sess.query(func.max(OpenProgress4.openPercent)).filter(OpenProgress4.gusigun==candidate_region,OpenProgress4.datatime<=time, OpenProgress4.sggCityCode!=None).scalar() 
	print(openrate)
	
	candidate, candidate_region, candidate_poll_code = sess.query(CandidateInfo.name, CandidateInfo.sggName, CandidateInfo.sgTypecode).filter(CandidateInfo.huboid==100130241).first()
	print(candidate_poll_code)

	if candidate_poll_code == 2: # 국회의원
		openrate = sess.query(func.max(OpenProgress2.openPercent)).filter(OpenProgress2.sgg==candidate_region,OpenProgress2.datatime<=time, OpenProgress2.sggCityCode!=None).scalar() # , 
	elif candidate_poll_code == 3:
		openrate = sess.query(func.max(OpenProgress3.openPercent)).filter(OpenProgress3.sido==candidate_region, OpenProgress3.gusigun=='합계',OpenProgress3.datatime<=time).scalar() # ,  
	elif candidate_poll_code == 4:
		openrate = sess.query(func.max(OpenProgress4.openPercent)).filter(OpenProgress4.gusigun==candidate_region,OpenProgress4.datatime<=time, OpenProgress4.sggCityCode!=None).scalar() # , 
	elif candidate_poll_code == 11:
		openrate = sess.query(func.max(OpenProgress11.openPercent)).filter(OpenProgress11.sido==candidate_region, OpenProgress11.gusigun=='합계',OpenProgress11.datatime<=time).scalar() #
	print(openrate)
	region1 = '충청북도'
	openrate = sess.query(func.max(OpenProgress3.openPercent)).filter(OpenProgress3.datatime<=time, OpenProgress3.sido==region1, OpenProgress3.gusigun=='합계').scalar()
	print(openrate)
