from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    role = Column(String)
    password = Column(String)
    equipe = Column(String, nullable=True)          # Ex: Équipe A, Équipe B
    statut_presence = Column(String, default="Présent") # Présent ou Absent

class Controle(Base):
    __tablename__ = "controles"
    id = Column(Integer, primary_key=True, index=True)
    line_name = Column(String)
    status = Column(String)
    technician_id = Column(Integer, nullable=True)
    date_debut = Column(String, nullable=True)
    date_fin = Column(String, nullable=True)
    photo_path = Column(String, nullable=True)
    manquants = Column(String, nullable=True)
