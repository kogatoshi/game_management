from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import sys
import pymysql
pymysql.install_as_MySQLdb()


DATABASE = 'mysql+pymysql://root:tenma129@localhost/gamesoft?charset=utf8'

metadata = MetaData()

engine = create_engine(DATABASE, encoding='utf-8')
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
session = db_session()
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import game.models
    Base.metadata.create_all(bind=engine)
