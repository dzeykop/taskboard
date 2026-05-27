import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase, sessionmaker

class Base(DeclarativeBase):
    pass

class Aufgabe(Base):
    __tablename__ = 'aufgaben'

    id = Column(Integer, primary_key=True)
    beschreibung = Column(String, nullable=False)
    zugewiesen_an = Column(String, nullable=True)
    erledigt = Column(Boolean, default=False)
    erstellt_am = Column(DateTime, default=datetime.now)
    bild_pfad = Column(String, nullable=True)
    erledigt_am = Column(DateTime, nullable=True)
    erledigt_von = Column(String, nullable=True)

engine = create_engine('sqlite:////opt/taskboard/taskboard.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
