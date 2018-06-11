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

	toorate_region1_sub = sess.query(func.max(VoteProgress.tooRate), VoteProgress.gusigun).filter(VoteProgress.timeslot<=t, VoteProgress.sido=='경기도', VoteProgress.gusigun!='합계').group_by(VoteProgress.gusigun).order_by(func.max(VoteProgress.tooRate).desc(), func.max(VoteProgress.tooTotal).desc()).all()
	print(toorate_region1_sub)