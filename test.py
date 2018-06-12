from orm import *
import datetime
from sqlalchemy.sql import func, and_, label
import pandas as pd
from templates import text_templates, background_variations
from queries import NoTextError, josaPick, regionPoll, regionCodeCheck
from collections import Counter
from random import choice

with session_scope() as sess:
	t = '20180613230000'
	time = datetime.datetime.strptime(t, '%Y%m%d%H%M%S')
	index = 0
	# regions = [1100]
	order = 0
	candidates = [100128761]

	if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
		t = 23
	else:
		t = time.hour

	toorate_region1_sub = sess.query(func.max(VoteProgress.tooRate), VoteProgress.gusigun).filter(VoteProgress.timeslot<=t, VoteProgress.sido=='경기도', VoteProgress.gusigun!='합계').group_by(VoteProgress.gusigun).order_by(func.max(VoteProgress.tooRate).desc(), func.max(VoteProgress.tooTotal).desc()).all()
	# print(toorate_region1_sub)

	candidate_region_sub = sess.query(func.max(VoteProgress.tooRate), VoteProgress.gusigun,VoteProgress.townCode).filter(VoteProgress.timeslot<=t, VoteProgress.sido=='경기도', VoteProgress.gusigun!='합계').group_by(VoteProgress.gusigun).all()
	# print(candidate_region_sub)



	each_toorate = sess.query(VoteProgress.townCode, PrecinctCode4.gusigun.label('gusigun'), func.max(VoteProgress.yooToday).label('yooToday'), func.max(VoteProgress.yooEarly).label('yooEarly'), func.max(VoteProgress.tooToday).label('tooToday'), func.max(VoteProgress.tooEarly).label('tooEarly'))
	.outerjoin(PrecinctCode4, VoteProgress.gusigun==PrecinctCode4.sgg)
	.filter(VoteProgress.timeslot<=t, VoteProgress.sido=='경기도', VoteProgress.gusigun!='합계')
	.group_by(VoteProgress.townCode)
	
	
	print(each_toorate.all())
	
	# print(sess.query(each_toorate.subquery()).group_by(each_toorate.subquery().c.gusigun).all())
	
	dd = sess.query(func.sum(each_toorate.subquery().c.yooToday), func.sum(each_toorate.subquery().c.yooEarly), func.sum(each_toorate.subquery().c.tooToday), func.sum(each_toorate.subquery().c.tooEarly)).group_by(each_toorate.gusigun)
	print(dd.all())


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
	
