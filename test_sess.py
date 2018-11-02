from orm import *
import datetime
from sqlalchemy.sql import func, and_, label
import pandas as pd
from templates import text_templates, background_variations
from queries import NoTextError, josaPick, regionPoll, regionCodeCheck, query_card_data
from collections import Counter
from random import choice

with session_scope() as sess:
	t = '20180613220000'
	time = datetime.datetime.strptime(t, '%Y%m%d%H%M%S')
# 	# time = datetime.datetime.now()
	index = 2
	regions = [3101]
# 	order = 0
	# candidates = [100131357]
	polls = [3]
	parties = [1,2,3]

	# region1 = '제주특별자치도'
	# region1 = '세종특별자치시'
	region1 = '서울특별시'
	# sub_r = sess.query(func.max(OpenProgress.openPercent).label('rate'), OpenProgress.sido, OpenProgress.gusigun).filter(OpenProgress.electionCode==3, OpenProgress.datatime<=time, OpenProgress.gusigun!='합계', OpenProgress.sido==region1).group_by(OpenProgress.sido, OpenProgress.gusigun)

	sub_r = sess.query(((func.sum(OpenProgress.tooTotal)+func.sum(OpenProgress.invalid)) / func.sum(OpenProgress.yooTotal) * 100).label('rate'), PrecinctCode4.sido, PrecinctCode4.gusigun).outerjoin(PrecinctCode4, and_(OpenProgress.sido==PrecinctCode4.sido, OpenProgress.gusigun==PrecinctCode4.sgg)).filter(OpenProgress.datatime<=time, PrecinctCode4.gusigun!='합계', OpenProgress.sido==region1).group_by(OpenProgress.sido, PrecinctCode4.gusigun)
	print(sub_r.all())

	t = 18
	toorate_region1_sub = sess.query((func.sum(VoteProgress.tooTotal) / func.sum(VoteProgress.yooTotal) * 100), PrecinctCode4.gusigun).outerjoin(PrecinctCode4, and_(VoteProgress.sido==PrecinctCode4.sido, VoteProgress.gusigun==PrecinctCode4.sgg)).filter(VoteProgress.timeslot==t, VoteProgress.sido==region1, VoteProgress.gusigun!='합계').group_by(VoteProgress.sido, PrecinctCode4.gusigun)
	
	# toorate_region1_sub = sess.query((func.sum(VoteProgress.tooTotal) / func.sum(VoteProgress.yooTotal) * 100), VoteProgress.gusigun).filter(VoteProgress.timeslot==t, VoteProgress.sido==region1, VoteProgress.gusigun!='합계').group_by(VoteProgress.sido, VoteProgress.gusigun)

	print(toorate_region1_sub.all())