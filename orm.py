import dbinfo
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, mapper
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.sql import func
from sqlalchemy import MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

# engine = create_engine('mysql+pymysql://{id}:{pw}@{host}/election2018?charset=utf8mb4'.format(id=dbinfo.id, pw=dbinfo.pw, host=dbinfo.host), echo=False)
# engine = create_engine('mysql+pymysql://{id}:{pw}@{host}/election2018?charset=utf8mb4'.format(id=dbinfo.id, pw=dbinfo.pw, host=dbinfo.host), 
#         echo=False, pool_size=20, pool_recycle=500)

# ### using views
# class OpenViewSido(object):
#     def __init__(self, name):
#        self.name = name

# class OpenViewGusigun(object):
#     def __init__(self, name):
#        self.name = name

# metadata = MetaData()
# metadata.reflect(engine, views=True)

# openviewsido= Table('view_2018_open_sido_mayor', metadata, autoload=True, autoload_with=engine)
# mapper(OpenViewSido, openviewsido, primary_key=[openviewsido.c.serial])

# openviewgusigun= Table('view_2018_open_gusigun_mayor', metadata, autoload=True, autoload_with=engine)
# mapper(OpenViewGusigun, openviewgusigun, primary_key=[openviewgusigun.c.serial])

# Base = automap_base(metadata=metadata)
# Base.prepare(engine, reflect=True)

### basic usage
# Base = automap_base()
# Base.prepare(engine, reflect=True)

# Vote13 = Base.classes.snu_2018_vote_13
# District = Base.classes.sbs_2017_district
# Candidate = Base.classes.sbs_2017_candidates
# OpenSido = Base.classes.snu_2018_open_sido_mayor
# OpenGusigun = Base.classes.snu_2018_open_gusigun_mayor
# PastVote = Base.classes.sbs_2012_vote
# CurrentVote = Base.classes.snu_2018_vote
# PartyCode = Base.classes.PartyCode
# # SgCode = Base.classes.SgCode
# # SggCode = Base.classes.SggCode
# SunCode = Base.classes.SunCode_180613

# sess2 = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


engine2 = create_engine('mysql+pymysql://{id}:{pw}@{host}/election180613?charset=utf8mb4'.format(id=dbinfo.id, pw=dbinfo.pw, host=dbinfo.host), 
        echo=False, pool_size=20, pool_recycle=500)
# Base2 = declarative_base()
Base2 = automap_base()
Base2.prepare(engine2, reflect=True)

# class SgTypeCode(Base2):
#     __tablename__ = 'SgTypeCode'
#     SgTypeCode = Column(Integer, primary_key=True)
#     SgName = Column(String)
    
# class CandidateInfo(Base2):
#     __tablename__ = 'CandidateInfo'
#     SgTypeCode = Column(Integer)
#     huboid = Column(Integer, primary_key=True)
#     jdName = Column(String)
#     name = Column(String)
#     SggName = Column(String)
#     SdName = Column(String)
#     wiwName = Column(String)

# class PrecinctCode(Base2):
#     __tablename__ = 'PrecinctCode'
#     sggCityCode = Column(Integer, primary_key=True)
#     electionCode = Column(Integer)
#     sido = Column(String)
#     gusigun = Column(String)

CandidateInfo = Base2.classes.CandidateInfo
PrecinctCode = Base2.classes.PrecinctCode
SgTypecode = Base2.classes.SgTypecode
PastVoteProgress = Base2.classes.VoteProgressPast
VoteProgress = Base2.classes.VoteProgress
VoteProgressLatest = Base2.classes.VoteProgressLatest
OpenProgress = Base2.classes.OpenProgress
OpenProgress2 = Base2.classes.OpenProgressLatest2
OpenProgress3 = Base2.classes.OpenProgressLatest3
OpenProgress4 = Base2.classes.OpenProgressLatest4
OpenProgress11 = Base2.classes.OpenProgressLatest11
PartyCode = Base2.classes.PartyCode


sess = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine2))

# SgTypeCode = Base2.classes.SgTypeCode
# CandidateInfo = Base2.classes.CandidateInfo
# PrecinctCode = Base2.classes.PrecinctCode



# sess = Session(engine)

# if __name__== "__main__":
    # result = db.query(Vote13).limit(5)
    # for r in result:
    #     print(r.suncode, r.toorate)
    # result = sess.query(func.max(Vote13.toorate)).filter(Vote13.tootime<=13, Vote13.sun_name1=='전국').first()
    # print(result[0])
