from orm import *
import datetime
from sqlalchemy.sql import func, and_, label
import pandas as pd
from templates import text_templates, background_variations
from queries import NoTextError, josaPick, regionPoll, regionCodeCheck, query_card_data
from collections import Counter
from random import choice

with session_scope() as sess:
# 	t = '20180614070000'
# 	time = datetime.datetime.strptime(t, '%Y%m%d%H%M%S')
# 	# time = datetime.datetime.now()
	index = 0
# 	# regions = [1100]
# 	order = 0
	candidates = [100131357]

# 	if time > datetime.datetime(2018, 6, 13, 23, 59, 59):
# 		t = 23
# 	else:
# 		t = time.hour

# 	region1 = "경상남도"
# 	polls = [4]


# 	region1='경기도'
# 	region2='수원시'



# 	# query_card_data
# 	polls = [2]
# 	regions = [4103]
# 	parties = [1]
# 	candidates = [100131357]
# 	card_seq = 22
# 	seqs_type = 1
# 	template = 1
# 	m = query_card_data(sess, order, index, polls, regions, parties, candidates, time, card_seq, seqs_type, template)
# 	print(m)
# 	# print(polls[index])
# 	# if polls[index] == 2:
# 	# 	sub = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sgg).filter(OpenProgress.datatime<=time,OpenProgress.electionCode==2, OpenProgress.sggCityCode!=None)

# 	# elif polls[index] == 3:
# 	# 	sub = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sido).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==3, OpenProgress.gusigun=='합계')
	
# 	# elif polls[index] == 4:
# 	# 	sub = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sggCityCode).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==4, OpenProgress.sggCityCode!=None)
	
# 	# elif polls[index] == 11:
# 	# 	sub = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sido).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==11, OpenProgress.gusigun=='합계')

# 	# if polls[index] in [2,3,4]:
# 	# 	if sub == None:
# 	# 		raise NoTextError

# 	# 	ranksDf = pd.read_sql(sub.statement, sub.session.bind)
# 	# 	print(ranksDf)
	
# 	subq = sess.query(func.max(OpenProgress.serial).label('maxserial'), func.max(OpenProgress.datatime).label('maxtime')).group_by(OpenProgress.sido).filter(OpenProgress.datatime<=time, OpenProgress.electionCode==11, OpenProgress.gusigun=='합계').subquery()
# 	sub_ranks = sess.query(OpenProgress).join(subq, and_(OpenProgress.serial==subq.c.maxserial, OpenProgress.datatime==subq.c.maxtime))
# 	ranksDf = pd.read_sql(sub_ranks.statement, sub_ranks.session.bind)
# 	ranksDf = ranksDf.sort_values(by=['openPercent', 'n_total'], ascending=False)
# 	ranksDf = ranksDf.reset_index(drop=True)
# 	print(ranksDf)
# 	openrate_rank1_region = ranksDf.loc[0,'sido']
# 	print(openrate_rank1_region)
# 	ranks_vote = ranksDf.filter(regex="n*_percent")
# 	ranks_ttl = []
# 	for i, ranks in ranks_vote.iterrows():
# 		ranks_ttl.append([v.split('_')[0] for v in ranks.sort_values(ascending=False).index.values])
# 	ranking = []
# 	for idx, ranks in enumerate(ranks_ttl):
# 		for i, r in enumerate(ranks):
# 			if ranksDf.loc[idx, r+'_name'] != None:
# 				ranking.append({
# 					'idx': idx,
# 					'rank': i,
# 					'jdName':ranksDf.loc[idx, r+'_jdName'],
# 					'name': ranksDf.loc[idx, r+'_name'],
# 					'percent': ranksDf.loc[idx, r+'_percent'],
# 					})
# 	print(ranking)
# 	openrate_rank1_region_candidate = [r['name'] for r in ranking if (r['idx']==0) and (r['rank']==0)][0]
# 	print(openrate_rank1_region_candidate)
# 	openrate_rank2_region_candidate = [r['name'] for r in ranking if (r['idx']==0) and (r['rank']==1)][0]
# 	print(openrate_rank2_region_candidate)

# 	print(sess.query(OpenProgress.serial, OpenProgress.sido, OpenProgress.gusigun(OpenProgress.tooTotal-OpenProgress.n_total+OpenProgress.invalid)).filter(OpenProgress.electionCode==2).group_by(OpenProgress.serial).all())


import requests
import urllib
import ast

url = 'http://127.0.0.1:5000/api?'
# url = 'http://13.209.65.180:5000/api?'
error_params = []
with open("../remake_log_180627_0507.txt", 'r') as f:
	previous_line = ''
	for line in f:
		if line == "CARD MODULE ERROR RESPONSE ;\n":
			error_params.append(previous_line)
			previous_line = line
		else:
			previous_line = line
print(error_params)



# with open("../remake_log_180627_0507.txt", 'r') as f:
# 	for line in f:
ee = []
for line in error_params:	# print(line)
	try:
		p = ast.literal_eval(line)
		# print(p)
		if 'ERROR' in p:
			pass
		else:
			params = urllib.parse.urlencode(p, doseq=True)
			response = requests.post(url+params)
			if response.status_code != 200:
				ee.append(params)
				# print(params)
	except SyntaxError:
		pass
print(ee)