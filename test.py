from orm import *
import datetime
from sqlalchemy.sql import func, and_
import pandas as pd

with session_scope() as sess:
	t = '20180613230000'
	time = datetime.datetime.strptime(t, '%Y%m%d%H%M%S')

	subq = sess.query(func.max(OpenProgress11.serial).label('maxserial'), func.max(OpenProgress11.datatime).label('maxtime')).group_by(OpenProgress11.sido).filter(OpenProgress11.datatime<=time, OpenProgress11.gusigun=='합계').subquery()

	sub = sess.query(OpenProgress11.sido, OpenProgress11.tooTotal, OpenProgress11.n_total, OpenProgress11.invalid).join(subq, and_(OpenProgress11.serial==subq.c.maxserial, OpenProgress11.datatime==subq.c.maxtime))

	tooTotal, n_total, invalid = sess.query(func.sum(OpenProgress11.tooTotal), func.sum(OpenProgress11.n_total), func.sum(OpenProgress11.invalid)).join(subq, and_(OpenProgress11.serial==subq.c.maxserial, OpenProgress11.datatime==subq.c.maxtime)).first()
	print(tooTotal, n_total, invalid )
	poll_openrate_nat_avg = (n_total + invalid) / tooTotal * 100
	print(poll_openrate_nat_avg)

	poll, poll_num_sunname = sess.query(SgTypecode.sgName, func.count(PrecinctCode.sggCityCode)).join(PrecinctCode, PrecinctCode.electionCode==SgTypecode.sgTypecode).filter(SgTypecode.sgTypecode==polls[index]).first()
	
	# if invalid == None:
	# 	invalid = 0

	# print(sess.query(SgTypecode.sgName).filter(SgTypecode.sgTypecode==2).scalar())
