from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, synonym
from game.database import Base
from werkzeug import check_password_hash, generate_password_hash

games_hardware_table = Table(
                    'games_hardwares',
                    Base.metadata,
                    Column('game_id', Integer, ForeignKey('games.id')),
                    Column('hard_id', Integer, ForeignKey('hardware.id')),
                )


user_game_table = Table(
                    'users_games',
                    Base.metadata,
                    Column('user_id', Integer, ForeignKey('users.id')),
                    Column('game_id', Integer, ForeignKey('games.id')),
                )


user_hard_table = Table(
                    'users_hardwares',
                    Base.metadata,
                    Column('user_id', Integer, ForeignKey('users.id')),
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

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return '<Title %r>' % (self.title)


class Hardware(Base):
    __tablename__ = 'hardware'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Name %r>' % (self.name)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(16), unique=True, nullable=False)
    address = Column(String(128), unique=True, nullable=False)
    _password = Column('password', String(256), nullable=False)

    games = relationship(
            'Games',
            order_by='Games.id',
            uselist=True,
            backref='users',
            secondary=user_game_table
    )

    hardwares = relationship(
            'Hardware',
            order_by='Hardware.id',
            uselist=True,
            backref='users',
            secondary=user_hard_table
    )

    def __init__(self, username, address, password):
        self.username = username
        self.address = address
        self.password = password

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        if password:
            password = password.strip()
        self._password = generate_password_hash(password)
    password_descriptor = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password_descriptor)

    def check_password(self, password):
        password = password.strip()
        if not password:
            return False
        return check_password_hash(self.password, password)

    @classmethod
    def authenticate(cls, query, address, password):
        user = query(cls).filter(cls.address == address).first()
        if user is None:
            return None, False
        return user, user.check_password(password)

    def __repr__(self):
        return '<User %r>' % (self.username)
