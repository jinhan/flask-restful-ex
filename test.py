from orm import *
import datetime
from sqlalchemy.sql import func, and_
import pandas as pd
from templates import text_templates, background_variations
from queries import NoTextError, josaPick, regionPoll
from collections import Counter
from random import choice

with session_scope() as sess:
	t = '20180613150000'
	time = datetime.datetime.strptime(t, '%Y%m%d%H%M%S')
	index = 0
	# regions = [1100]
	order = 0
	candidates = [100128761]

	if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
		t = 23
	else:
		t = time.hour
	candidate, candidate_region, candidate_sdName = sess.query(CandidateInfo.name, CandidateInfo.sggName, CandidateInfo.sdName).filter(CandidateInfo.huboid==candidates[index]).first()
	print(candidate, candidate_region, candidate_sdName)

	candidate_region_toorate = sess.query(func.max(VoteProgress.tooRate)).filter(VoteProgress.timeslot<=t, VoteProgress.sido==candidate_sdName, VoteProgress.gusigun=='합계').scalar()
	print(candidate_region_toorate)
	# each_toorate = sess.query(func.max(VoteProgress.yooToday).label('yooToday'), func.max(VoteProgress.yooEarly).label('yooEarly'), func.max(VoteProgress.tooToday).label('tooToday'), func.max(VoteProgress.tooEarly).label('tooEarly')).filter(VoteProgress.timeslot<=t, VoteProgress.sido==candidate_region, VoteProgress.gusigun=='합계').group_by(VoteProgress.sido).subquery()
	# print(sess.query(func.max(VoteProgress.yooToday).label('yooToday'), func.max(VoteProgress.yooEarly).label('yooEarly'), func.max(VoteProgress.tooToday).label('tooToday'), func.max(VoteProgress.tooEarly).label('tooEarly')).filter(VoteProgress.timeslot<=t, VoteProgress.sido==candidate_region, VoteProgress.gusigun=='합계').group_by(VoteProgress.sido))
	# yooToday, yooEarly, tooToday, tooEarly = sess.query(func.sum(each_toorate.c.yooToday), func.sum(each_toorate.c.yooEarly), func.sum(each_toorate.c.tooToday), func.sum(each_toorate.c.tooEarly)).first()

	# if tooEarly == None:
	# 	tooEarly = 0
	# print((tooToday+tooEarly) / (yooToday+yooEarly) * 100)


	candidate_region_sub = sess.query(func.max(VoteProgress.tooRate), VoteProgress.gusigun).filter(VoteProgress.timeslot<=t, VoteProgress.sido==candidate_sdName, VoteProgress.gusigun!='합계').group_by(VoteProgress.gusigun).all()
	print(candidate_region_sub)