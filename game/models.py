from sqlalchemy import Column, Integer, String, Text
from game.database import Base


class Games(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    title = Column(String(128), unique=True)
    hardware = Column(Text)

    def __init__(self, title=None, hardware=None):
        self.title = title
        self.hardware = hardware

    def __repr__(self):
        return '<Title %r>' % (self.title)


class Hardware(Base):
    __tablename__ = 'hardware'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return '<Name %r>' % (self.name)
