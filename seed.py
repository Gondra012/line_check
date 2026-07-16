from models import Base, User, Controle
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///./line_check.db")
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

if db.query(User).count() == 0:
    db.add(User(id=2, name="Dominique", role="Technicien", password="123", equipe="Equipe A", statut_presence="Présent"))
    db.add(User(id=3, name="BADINI", role="Technicien", password="123", equipe="Equipe B", statut_presence="Présent"))
    db.add(User(id=4, name="MATHIEU", role="Technicien", password="123", equipe="Equipe A", statut_presence="Présent"))

if db.query(Controle).count() == 0:
    db.add(Controle(id=1, line_name="Portion HTB - Pylone 01", status="En attente"))
    db.add(Controle(id=2, line_name="Portion HTB - Pylone 02", status="En attente"))

db.commit()
db.close()
print("Base de données initialisée avec les effectifs !")
