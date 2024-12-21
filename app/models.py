from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Term(Base):
    __tablename__ = 'terms'

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String, nullable=False)
    description = Column(String, nullable=False)

def create_tables(engine):
    Base.metadata.create_all(engine)