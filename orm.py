import dbinfo
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.sql import func

Base = automap_base()
engine = create_engine('mysql+pymysql://{id}:{pw}@{host}/election2018?charset=utf8mb4'.format(id=dbinfo.id, pw=dbinfo.pw, host=dbinfo.host), echo=False)
# reflect the tables
Base.prepare(engine, reflect=True)

Vote13 = Base.classes.snu_2018_vote_13
District = Base.classes.sbs_2017_district
Candidate = Base.classes.sbs_2017_candidates
Open = Base.classes.snu_2018_open_sido_mayor

sess = Session(engine)

if __name__== "__main__":
    # result = db.query(Vote13).limit(5)
    # for r in result:
    #     print(r.suncode, r.toorate)
    result = sess.query(func.max(Vote13.toorate)).filter(Vote13.tootime<=13, Vote13.sun_name1=='전국').first()
    print(result[0])
