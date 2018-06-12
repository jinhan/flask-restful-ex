from orm import *
import datetime
from sqlalchemy.sql import func, and_, label
import pandas as pd
from templates import text_templates, background_variations
from queries import NoTextError, josaPick, regionPoll, regionCodeCheck
from collections import Counter
from random import choice

with session_scope() as sess:
	t = '20180613180000'
	time = datetime.datetime.strptime(t, '%Y%m%d%H%M%S')
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
	region_nums = [4110000, 4270000]
	d = sess.query(PrecinctCode.sido, PrecinctCode.gusigun).filter(PrecinctCode.sggCityCode.in_(region_nums)).all()
	print(d)