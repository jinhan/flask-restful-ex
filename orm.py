import dbinfo
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, mapper
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.sql import func
from sqlalchemy import MetaData, Table

# engine = create_engine('mysql+pymysql://{id}:{pw}@{host}/election2018?charset=utf8mb4'.format(id=dbinfo.id, pw=dbinfo.pw, host=dbinfo.host), echo=False)
engine = create_engine('mysql+pymysql://{id}:{pw}@{host}/election2018?charset=utf8mb4'.format(id=dbinfo.id, pw=dbinfo.pw, host=dbinfo.host), echo=False, pool_size=20, pool_recycle=500)

### using views
class OpenViewSido(object):
    def __init__(self, name):
       self.name = name

# class OpenViewGusigun(object):
#     def __init__(self, name):
#        self.name = name

metadata = MetaData()
metadata.reflect(engine, views=True)

openviewsido= Table('view_2018_open_sido_mayor', metadata, autoload=True, autoload_with=engine)
mapper(OpenViewSido, openviewsido, primary_key=[openviewsido.c.serial])

# openviewgusigun= Table('view_2018_open_sido_mayor', metadata, autoload=True, autoload_with=engine)
# mapper(OpenViewGusiguno, openviewgusigun, primary_key=[openviewgusigun.c.serial])

Base = automap_base(metadata=metadata)
Base.prepare(engine, reflect=True)

### basic usage
# Base = automap_base()
# Base.prepare(engine, reflect=True)

Vote13 = Base.classes.snu_2018_vote_13
District = Base.classes.sbs_2017_district
Candidate = Base.classes.sbs_2017_candidates
OpenSido = Base.classes.snu_2018_open_sido_mayor

# sess = Session(engine)
sess = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

if __name__== "__main__":
    # result = db.query(Vote13).limit(5)
    # for r in result:
    #     print(r.suncode, r.toorate)
    result = sess.query(func.max(Vote13.toorate)).filter(Vote13.tootime<=13, Vote13.sun_name1=='전국').first()
    print(result[0])
