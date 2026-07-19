from fastapi import FastAPI, Depends, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Controle, User
import os
import pandas as pd
from datetime import datetime
import smtplib
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

engine = create_engine('sqlite:///./line_check.db', connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- BLOC DE DEMARRAGE ET D'INITIALISATION SECURISE (LIFESPAN) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    Base.metadata.create_all(bind=engine)
    if db.query(User).count() == 0:
        db.add(User(id=2, name="Dominique", role="Technicien", password="123", equipe="Equipe A", statut_presence="Présent"))
        db.add(User(id=3, name="BADINI", role="Technicien", password="123", equipe="Equipe B", statut_presence="Présent"))
        db.add(User(id=4, name="MATHIEU", role="Technicien", password="123", equipe="Equipe A", statut_presence="Présent"))
        db.commit()
    if db.query(Controle).count() == 0:
        db.add(Controle(id=1, line_name="Portion HTB - Pylone 01", status="En attente"))
        db.add(Controle(id=2, line_name="Portion HTB - Pylone 02", status="En attente"))
        db.commit()
    db.close()
    print("Verification et initialisation de la base Cloud accomplies !")
    yield

app = FastAPI(lifespan=lifespan)

if not os.path.exists('fichiers_chantier'): 
    os.makedirs('fichiers_chantier')
app.mount('/fichiers', StaticFiles(directory='fichiers_chantier'), name='fichiers')

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# --- ENGINE EXTRACTION EXCEL AUTOMATIQUE ---
EMAIL_EMETTEUR = "votre_email_bureau@gmail.com"
EMAIL_MOT_DE_PASSE = "votre_mot_de_passe_secret"
EMAIL_DESTINATAIRE = "directeur_projet@entreprise.com"
SMTP_SERVEUR = "://gmail.com"
SMTP_PORT = 587

def envoyer_rapport_samedi():
    db = SessionLocal()
    controles = db.query(Controle).all()
    data = []
    for c in controles:
        u = db.query(User).filter(User.id == c.technician_id).first()
        data.append({
            "ID Pylone": c.id,
            "Portion HTB": c.line_name,
            "Etape Actuelle": c.status,
            "Valide Par": u.name if u else "Non assigne",
            "Date Debut": c.date_debut if c.date_debut else "--",
            "Date Fin": c.date_fin if c.date_fin else "--",
            "Materiels Manquants": c.manquants if c.manquants else "Aucun"
        })
    db.close()
    nom_fichier = "Rapport_Hebdomadaire_HTB.xlsx"
    pd.DataFrame(data).to_excel(nom_fichier, index=False)
    msg = MIMEMultipart()
    msg['From'] = EMAIL_EMETTEUR
    msg['To'] = EMAIL_DESTINATAIRE
    msg['Subject'] = f"LINE_CHECK - Rapport Hebdomadaire HTB ({datetime.now().strftime('%d/%m/%Y')})"
    msg.attach(MIMEText("Bonjour,\n\nVeuillez trouver ci-joint le rapport hebdomadaire d'avancement.", 'plain'))
    try:
        with open(nom_fichier, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {nom_fichier}")
            msg.attach(part)
        server = smtplib.SMTP(SMTP_SERVEUR, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_EMETTEUR, EMAIL_MOT_DE_PASSE)
        server.sendmail(EMAIL_EMETTEUR, EMAIL_DESTINATAIRE, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Erreur e-mail : {e}")

# --- ROBOT AUTOMATIQUE ANTI-SOMMEIL CLOUD ---
def garder_serveur_actif():
    try:
        url_render = "https://onrender.com"
        req = urllib.request.Request(url_render, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            print(f"Ping d'activite envoye : {response.getcode()}")
    except Exception as e:
        print(f"Robot de garde en attente : {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(envoyer_rapport_samedi, 'cron', day_of_week='sat', hour=13, minute=0)
scheduler.add_job(garder_serveur_actif, 'interval', minutes=3)
scheduler.start()

from interface import obtenir_status_style, get_pct, generer_bureau_html, generer_login_html, generer_mobile_html

@app.get('/', response_class=HTMLResponse)
def home(db: Session = Depends(get_db)):
    tc = db.query(Controle).count()
    tu = db.query(User).count()
    t_presents = db.query(User).filter(User.statut_presence == "Présent").count()
    t_absents = db.query(User).filter(User.statut_presence == "Absent").count()
    controles = db.query(Controle).all()
    users = db.query(User).all()
    alertes_manquants = sum(1 for c in controles if c.manquants and c.manquants.strip().lower() != 'aucun')
    
    rows = ''
    for c in controles:
        u = db.query(User).filter(User.id == c.technician_id).first()
        t_name = u.name if u else "Non assigné"
        d_deb = c.date_debut if c.date_debut else "--"
        d_fin = c.date_fin if c.date_fin else "--"
        is_mq = c.manquants and c.manquants.strip().lower() != 'aucun'
        mq_style = "color:#dc2626; font-weight:bold; background:#fee2e2; padding:4px 8px; border-radius:6px;" if is_mq else "color:#64748b;"
        mq_text = c.manquants if c.manquants else "Aucun"
        pct = get_pct(c.status)
        badge_style = obtenir_status_style(c.status)
        img = f"<a href='/fichiers/{c.photo_path}' target='_blank' style='color:#2563eb; font-weight:600; text-decoration:none;'>👁️ Voir Photo</a>" if c.photo_path else "<span style='color:#94a3b8;'>Pas de photo</span>"
        btn_suppr = f"<a href='/supprimer-pylone/{c.id}' style='color:#ef4444; font-weight:bold; text-decoration:none; margin-left:10px;' onclick='return confirm(\"Supprimer ce pylône ?\");'>❌</a>"
        
        rows += f"<tr><td style='padding:14px; border-bottom:1px solid #e2e8f0;'>#{c.id} {btn_suppr}</td><td style='padding:14px; border-bottom:1px solid #e2e8f0; font-weight:600;'>{c.line_name}</td><td style='padding:14px; border-bottom:1px solid #e2e8f0;'><span style='padding:6px 12px; border-radius:20px; font-size:11px; font-weight:bold; text-transform:uppercase; {badge_style}'>{c.status}</span></td><td style='padding:14px; border-bottom:1px solid #e2e8f0;'><div style='background:#e2e8f0; border-radius:8px; width:100px; height:10px; display:inline-block; margin-right:8px; overflow:hidden;'><div style='background:#16a34a; height:100%; width:{pct}%;'></div></div> <b>{pct}%</b></td><td>{t_name}</td><td>{d_deb}</td><td>{d_fin}</td><td><span style='{mq_style}'>{mq_text}</span></td><td>{img}</td></tr>"
        
    u_list = ''.join([f"<li style='padding:6px 0; border-bottom:1px solid #f1f5f9; color:#334155;'><a href='/supprimer-user/{usr.id}' style='color:#ef4444; font-weight:bold; text-decoration:none; margin-right:8px;' onclick='return confirm(\"Supprimer définitivement cet équipier ?\");'>❌</a><b>{usr.name}</b> - {usr.role} [<span style='color:blue;'>{usr.equipe}</span>] - <b>{usr.statut_presence}</b></li>" for usr in users])
    opt_pylones = ''.join([f"<option value='{c.id}'>#{c.id} - {c.line_name}</option>" for c in controles])
    opt_techs = "".join([f"<option value='{u.id}'>{u.name} ({u.equipe})</option>" for u in users])
    return generer_bureau_html(tc, tu, t_presents, t_absents, alertes_manquants, rows, u_list, opt_pylones, opt_techs)

sessions_actives = {}

@app.get('/mobile', response_class=HTMLResponse)
def page_login_ou_terrain(request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host
    if client_ip in sessions_actives:
        user = sessions_actives[client_ip]
        controles = db.query(Controle).all()
        opt_pylones = ''.join([f"<option value='{c.id}'>{c.line_name}</option>" for c in controles])
        return generer_mobile_html(user.name, user.id, opt_pylones)
    return generer_login_html()

@app.post('/login-mobile')
def login_mobile(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.name == username, User.password == password).first()
    if not user:
        return generer_login_html(erreur="Identifiants ou mot de passe invalides")
    if user.statut_presence == "Absent":
        return generer_login_html(erreur="Accès refusé : vous êtes déclaré Absent au bureau")
    
    client_ip = request.client.host
    sessions_actives[client_ip] = user
    return RedirectResponse(url='/mobile', status_code=303)

@app.get('/deconnexion-mobile')
def deconnexion_mobile(request: Request):
    client_ip = request.client.host
    if client_ip in sessions_actives:
        del sessions_actives[client_ip]
    return RedirectResponse(url='/mobile', status_code=303)

@app.post('/creer-user')
def creer_user(u_name: str = Form(...), u_role: str = Form(...), u_equipe: str = Form(...), u_pass: str = Form(...), db: Session = Depends(get_db)):
    db.add(User(name=u_name, role=u_role, equipe=u_equipe, password=u_pass, statut_presence="Présent"))
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post('/creer-pylone')
def creer_pylone(p_name: str = Form(...), db: Session = Depends(get_db)):
    db.add(Controle(line_name=p_name, status="En attente"))
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get('/supprimer-pylone/{p_id}')
def supprimer_pylone(p_id: int, db: Session = Depends(get_db)):
    item = db.query(Controle).filter(Controle.id == p_id).first()
    if item:
        db.delete(item)
        db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get('/supprimer-user/{u_id}')
def supprimer_user(u_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == u_id).first()
    if user:
        db.delete(user)
        db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post('/modifier-user-bureau')
def modifier_user_bureau(t_id: int = Form(...), u_role: str = Form(None), u_equipe: str = Form(None), u_presence: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == t_id).first()
    if user:
        if u_role: user.role = u_role
        if u_equipe: user.equipe = u_equipe
        user.statut_presence = u_presence
        db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post('/maj-statut-bureau')
def maj_statut_bureau(c_id: int = Form(...), t_id: int = Form(...), n_statut: str = Form(...), db: Session = Depends(get_db)):
    item = db.query(Controle).filter(Controle.id == c_id).first()
    if item:
        item.status = n_statut
        item.technician_id = t_id
        db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post('/maj-statut-mobile')
def maj_statut_mobile(c_id: int = Form(...), t_id: int = Form(...), n_statut: str = Form(...), d_debut: str = Form(None), d_fin: str = Form(None), manquants: str = Form(None), photo: UploadFile = File(None), db: Session = Depends(get_db)):
    item = db.query(Controle).filter(Controle.id == c_id).first()
    if item:
        item.status = n_statut
        item.technician_id = t_id
        item.date_debut = d_debut
        item.date_fin = d_fin
        item.manquants = manquants
        if photo and photo.filename:
            dossier_pylone = f"fichiers_chantier/pylone_{c_id}"
            if not os.path.exists(dossier_pylone):
                os.makedirs(dossier_pylone)
            f_name = f"pylone_{c_id}/{photo.filename}"
            with open(f"fichiers_chantier/{f_name}", "wb") as f: 
                f.write(photo.file.read())
            item.photo_path = f_name
        db.commit()
    return RedirectResponse(url='/mobile', status_code=303)

@app.get('/telecharger-rapport-excel')
def telecharger_rapport_excel(db: Session = Depends(get_db)):
    controles = db.query(Controle).all()
    data = []
    for c in controles:
        u = db.query(User).filter(User.id == c.technician_id).first()
        data.append({
            "ID Pylone": c.id,
            "Portion HTB": c.line_name,
            "Etape Actuelle": c.status,
            "Progression (%)": get_pct(c.status),
            "Valide Par": u.name if u else "Non assigne",
            "Equipe": u.equipe if u else "--",
            "Date Debut": c.date_debut if c.date_debut else "--",
            "Date Fin": c.date_fin if c.date_fin else "--",
            "Materiels Manquants / Observations": c.manquants if c.manquants else "Aucun"
        })
    df = pd.DataFrame(data)
    nom_fichier = "Rapport_Hebdomadaire_HTB.xlsx"
    with pd.ExcelWriter(nom_fichier, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Avancement Chantier")
    return FileResponse(path=nom_fichier, filename=nom_fichier, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
# Synchronisation finale pour Render 
