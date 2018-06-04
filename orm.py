import dbinfo
from sqlalchemy.ext.automap import automap_base
# from sqlalchemy.orm import Session, mapper
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
# from sqlalchemy.sql import func
# from sqlalchemy import MetaData, Table
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column, Integer, String

engine = create_engine('mysql+pymysql://{id}:{pw}@{host}/election180613?charset=utf8mb4'.format(id=dbinfo.id, pw=dbinfo.pw, host=dbinfo.host), 
        echo=False, pool_size=20, pool_recycle=500)

Base = automap_base()
Base.prepare(engine, reflect=True)

CandidateInfo = Base.classes.CandidateInfo
PrecinctCode = Base.classes.PrecinctCode
SgTypecode = Base.classes.SgTypecode
PastVoteProgress = Base.classes.VoteProgressPast
VoteProgress = Base.classes.VoteProgress
VoteProgressLatest = Base.classes.VoteProgressLatest
OpenProgress = Base.classes.OpenProgress
OpenProgress2 = Base.classes.OpenProgressLatest2
OpenProgress3 = Base.classes.OpenProgressLatest3
OpenProgress4 = Base.classes.OpenProgressLatest4
OpenProgress11 = Base.classes.OpenProgressLatest11
PartyCode = Base.classes.PartyCode

sess = scoped_session(sessionmaker(autocommit=True, autoflush=True, bind=engine, expire_on_commit=True))

