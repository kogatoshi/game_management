from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from game.database import Base


games_hardware_table = Table(
                    'games_hardwares',
                    Base.metadata,
                    Column('game_id', Integer, ForeignKey('games.id')),
                    Column('hard_id', Integer, ForeignKey('hardware.id')),
                )


class Games(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    title = Column(String(128), unique=True)

    hardwares = relationship(
            'Hardware',
            order_by='Hardware.id',
            uselist=True,
            backref='games',
            secondary=games_hardware_table
    )

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


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(16), unique=True)
    password = Column(String(32))

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return '<User %r>' % (self.username)
