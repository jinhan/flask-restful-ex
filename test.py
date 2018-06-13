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

	region1='경기도'
	sub = sess.query(func.max(OpenProgress3.tooTotal).label('tooTotal'), func.max(OpenProgress3.n_total).label('n_total'), func.max(OpenProgress3.invalid).label('invalid')).filter(OpenProgress3.sido==region1, OpenProgress3.datatime<=time).group_by(OpenProgress3.townCode)
	print(sub.all())