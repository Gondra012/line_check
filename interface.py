def obtenir_status_style(status):
    status_upper = status.upper()
    if any(k in status_upper for k in ["ACCES", "PIQUETAGE", "TERRASSEMENT", "FOUILLE"]):
        return "background:#fee2e2; color:#dc2626; border:1px solid #fca5a5;"  # Rouge
    if any(k in status_upper for k in ["BETONNAGE", "LIVRAISONS", "ASSEMBLAGE", "REVISION"]):
        return "background:#ffedd5; color:#ea580c; border:1px solid #fdba74;"  # Orange
    if any(k in status_upper for k in ["TERRE", "POULIE", "DEROULAGE", "REGLAGE", "PINCE"]):
        return "background:#e0f2fe; color:#0284c7; border:1px solid #7dd3fc;"  # Bleu
    if "ESSAIS" in status_upper:
        return "background:#dcfce7; color:#16a34a; border:1px solid #86efac;"  # Vert
    return "background:#f1f5f9; color:#475569; border:1px solid #cbd5e1;"

def get_pct(status):
    status_upper = status.upper()
    if "OUVERTURES" in status_upper: return 10
    if "PIQUETAGE" in status_upper: return 20
    if "TERRASSEMENT" in status_upper: return 30
    if "FOUILLE" in status_upper: return 40
    if "BETONNAGE" in status_upper: return 50
    if "LIVRAISONS" in status_upper: return 60
    if "ASSEMBLAGE" in status_upper: return 70
    if "REVISION" in status_upper: return 75
    if "VERIFICATION" in status_upper: return 80
    if "POULIE" in status_upper: return 85
    if "DEROULAGE CABLE" in status_upper: return 90
    if "REGLAGE" in status_upper: return 93
    if "PINCE" in status_upper: return 96
    if "ESSAIS" in status_upper: return 100
    return 0
def generer_bureau_html(tc, tu, t_presents, t_absents, alertes_manquants, rows, u_list, opt_pylones, opt_techs):
    return f"""
    <html>
    <head>
        <title>LINE_CHECK Superviseur</title>
        <meta charset='utf-8'>
        <style>
            body {{ font-family:'Segoe UI',sans-serif; background:#f8fafc; margin:0; padding:30px; color:#1e293b; }}
            header {{ background:#0f172a; color:white; padding:25px; border-radius:12px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom:30px; position:relative; }}
            h1 {{ margin:0; font-size:24px; font-weight:700; letter-spacing:-0.5px; }}
            .grid {{ display:flex; gap:20px; margin-bottom:30px; }}
            .card {{ background:white; padding:20px; border-radius:12px; box-shadow:0 1px 3px rgba(0,0,0,0.05); flex:1; border:1px solid #e2e8f0; }}
            .card h3 {{ margin:0 0 10px 0; color:#64748b; font-size:12px; text-transform:uppercase; letter-spacing:0.5px; }}
            .card .num {{ font-size:32px; font-weight:700; color:#0f172a; margin:0; }}
            .card.alert {{ border-left:5px solid #ef4444; }} .card.alert .num {{ color:#ef4444; }}
            .card.present {{ border-left:5px solid #10b981; }} .card.present .num {{ color:#10b981; }}
            .card.absent {{ border-left:5px solid #f59e0b; }} .card.absent .num {{ color:#f59e0b; }}
            .main-content {{ display:flex; gap:25px; align-items: flex-start; }}
            .table-container {{ background:white; padding:24px; border-radius:12px; box-shadow:0 1px 3px rgba(0,0,0,0.05); border:1px solid #e2e8f0; flex:2.5; width:100%; overflow-x:auto; }}
            .sidebar-layout {{ display:flex; flex-direction:column; gap:20px; flex:1.2; }}
            .sidebar {{ background:white; padding:20px; border-radius:12px; box-shadow:0 1px 3px rgba(0,0,0,0.05); border:1px solid #e2e8f0; }}
            table {{ width:100%; border-collapse:collapse; text-align:left; }}
            th {{ background:#f8fafc; padding:14px; border-bottom:2px solid #e2e8f0; color:#64748b; font-size:12px; text-transform:uppercase; font-weight:600; }}
            tr:hover {{ background:#f8fafc; }}
            h2 {{ margin:0 0 15px 0; font-size:15px; font-weight:600; color:#0f172a; border-bottom:2px solid #f1f5f9; padding-bottom:8px; }}
            input, select, button {{ width:100%; padding:10px; margin-bottom:10px; border-radius:6px; border:1px solid #cbd5e1; box-sizing:border-box; font-size:13px; }}
            button {{ color:white; font-weight:bold; border:none; cursor:pointer; }}
            .btn-excel {{ position:absolute; right:25px; top:28px; background:#16a34a; padding:10px 20px; border-radius:8px; color:white; text-decoration:none; font-weight:bold; font-size:14px; box-shadow:0 2px 4px rgba(0,0,0,0.1); }}
        </style>
    </head>
    <body>
        <header>
            <h1>⚡ LINE_CHECK | Console de Supervision (Bureau)</h1>
            <div style='color:#94a3b8; font-size:13px; margin-top:5px;'>Suivi fin-en-fin, gestion des effectifs et rapports automatisés HTB</div>
            <a href='/telecharger-rapport-excel' class='btn-excel'>📊 Extraire Rapport Excel</a>
        </header>
        
        <div class='grid'>
            <div class='card'>
                <h3>Pylônes HTB</h3>
                <p class='num'>{tc}</p>
            </div>
            <div class='card present'>
                <h3>Actifs Chantier</h3>
                <p class='num'>{t_presents}</p>
            </div>
            <div class='card absent'>
                <h3>Absents</h3>
                <p class='num'>{t_absents}</p>
            </div>
            <div class='card alert'>
                <h3>Alertes Manquants</h3>
                <p class='num'>{alertes_manquants}</p>
            </div>
        </div>
        <div class='main-content'>
            <div class='table-container'>
                <h2>Journal d'Avancement Global Fin-en-Fin</h2>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Portion HTB</th>
                            <th>Étape Actuelle</th>
                            <th>Progression</th>
                            <th>Validé Par</th>
                            <th>Début</th>
                            <th>Fin</th>
                            <th>Observations / Manquants</th>
                            <th>Preuve Visuelle</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
            
            <div class='sidebar-layout'>
                <div class='sidebar'>
                    <h2>🏗️ Ajouter un Pylône</h2>
                    <form method='post' action='/creer-pylone'>
                        <input type='text' name='p_name' placeholder='Nom du Pylône (ex: Pylône 34)' required>
                        <button type='submit' style='background:#2563eb;'>Ajouter au Chantier</button>
                    </form>
                </div>
                <div class='sidebar'>
                    <h2>👥 Enregistrer un Équipier</h2>
                    <form method='post' action='/creer-user'>
                        <input type='text' name='u_name' placeholder="Nom d'utilisateur" required>
                        <input type='text' name='u_role' placeholder='Rôle (ex: Monteur)' required>
                        <input type='text' name='u_equipe' placeholder='Équipe (ex: Equipe A)' required>
                        <input type='password' name='u_pass' placeholder='Mot de passe terrain' required>
                        <button type='submit' style='background:#10b981;'>Ajouter au Registre</button>
                    </form>
                </div>
                <div class='sidebar'>
                    <h2>✏️ Modifier Équipier / Présence</h2>
                    <form method='post' action='/modifier-user-bureau'>
                        <select name='t_id' required>
                            <option value='' disabled selected>--- Choisir l'équipier ---</option>
                            {opt_techs}
                        </select>
                        <input type='text' name='u_role' placeholder='Changer Rôle (Optionnel)'>
                        <input type='text' name='u_equipe' placeholder='Changer Équipe (Optionnel)'>
                        <select name='u_presence'>
                            <option value='Présent'>Présent (Actif Chantier)</option>
                            <option value='Absent'>Absent</option>
                        </select>
                        <button type='submit' style='background:#ea580c;'>Modifier la Fiche Équipe</button>
                    </form>
                </div>
                <div class='sidebar'>
                    <h2>✏️ Assignation Rapide Bureau</h2>
                    <form method='post' action='/maj-statut-bureau'>
                        <select name='c_id' required>
                            <option value='' disabled selected>--- Choisir le Pylône ---</option>
                            {opt_pylones}
                        </select>
                        <select name='t_id' required>
                            <option value='' disabled selected>--- Assigner un Tech ---</option>
                            {opt_techs}
                        </select>
                        <select name='n_statut' required>
                            <option value='' disabled selected>--- Choisir l'étape ---</option>
                            <option>1-OUVERTURES DES ACCES</option>
                            <option>2-PIQUETAGE</option>
                            <option>3- TERRASSEMENT</option>
                            <option>4- FOUILLE</option>
                            <option>5- BETONNAGE FONDATIONS</option>
                            <option>6- LIVRAISONS PYLONES</option>
                            <option>7- ASSEMBLAGE ET LEVAGE</option>
                            <option>8- REVISION</option>
                            <option>9-VERIFICATION MISE A LA TERRE</option>
                            <option>9-MIS EN POULIE ET DEROULAGE CABLETTE</option>
                            <option>10-DEROULAGE CABLE</option>
                            <option>11- REGLAGE ET ANCRAGE</option>
                            <option>12- MISE EN PINCE</option>
                            <option>12- ESSAIS ET MISE EN SERVICE</option>
                        </select>
                        <button type='submit' style='background:#eab308; color:#0f172a;'>Enregistrer les modifications</button>
                    </form>
                </div>
                <div class='sidebar'>
                    <h2>Registre Personnel & Présences</h2>
                    <ul style='list-style:none; padding:0; margin:0;'>
                        {u_list}
                    </ul>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
def generer_login_html(erreur=""):
    msg_err = f"<p style='color:#ef4444; font-weight:bold; text-align:center;'>⚠️ {erreur}</p>" if erreur else ""
    return f"""
    <html>
    <head>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>Connexion Terrain</title>
        <style>
            body{{font-family:'Segoe UI',sans-serif; background:#f1f5f9; margin:0; padding:40px 15px; display:flex; flex-direction:column; justify-content:center; align-items:center;}}
            .login-card{{background:white; padding:30px; border-radius:12px; box-shadow:0 4px 6px rgba(0,0,0,0.05); width:100%; max-width:400px; border:1px solid #e2e8f0;}}
            h1{{color:#2563eb; font-size:22px; text-align:center; margin:0 0 5px 0;}}
            label{{display:block; margin:15px 0 5px 0; font-weight:bold; color:#334155; font-size:14px}}
            input, button{{width:100%; padding:12px; box-sizing:border-box; border-radius:8px; border:1px solid #cbd5e1; font-size:16px; margin-bottom:10px}}
            button{{background:#2563eb; color:white; border:none; font-weight:bold; margin-top:15px; cursor:pointer}}
        </style>
    </head>
    <body>
        <div class='login-card'>
            <h1>🔒 LINE_CHECK Tech</h1>
            <p style='text-align:center; color:#64748b; font-size:13px; margin:0 0 20px 0;'>Authentification Opérateur HTB</p>
            {msg_err}
            <form method='post' action='/login-mobile'>
                <label>Nom d'utilisateur :</label>
                <input type='text' name='username' placeholder='Ex: Dominique' required>
                <label>Mot de passe :</label>
                <input type='password' name='password' placeholder='••••' required>
                <button type='submit'>Se connecter au chantier</button>
            </form>
        </div>
    </body>
    </html>
    """

def generer_mobile_html(user_name, user_id, opt_pylones):
    return f"""
    <html>
    <head>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>LINE_CHECK Terrain</title>
        <style>
            body{{font-family:'Segoe UI',sans-serif; background:#f1f5f9; margin:0; padding:15px}}
            header{{background:#2563eb; color:white; padding:15px 20px; border-radius:12px; margin-bottom:15px; position:relative;}}
            .form-card{{background:white; padding:20px; border-radius:12px; box-shadow:0 4px 6px rgba(0,0,0,0.05); border:1px solid #e2e8f0;}}
            label{{display:block; margin:15px 0 5px 0; font-weight:bold; color:#334155; font-size:14px}}
            select,input,button{{width:100%; padding:12px; box-sizing:border-box; border-radius:8px; border:1px solid #cbd5e1; font-size:16px; margin-bottom:10px}}
            button{{background:#10b981; color:white; border:none; font-weight:bold; margin-top:15px; cursor:pointer}}
            .status-banner{{display:none; padding:10px; border-radius:8px; text-align:center; font-weight:bold; margin-bottom:10px; font-size:14px;}}
            .offline{{display:block; background:#fee2e2; color:#dc2626; border:1px solid #fca5a5;}}
            .online{{display:block; background:#dcfce7; color:#16a34a; border:1px solid #86efac;}}
        </style>
    </head>
    <body>
        <header>
            <h1 style='margin:0; font-size:18px;'>🛠️ Session : {user_name}</h1>
            <p style='margin:2px 0 0 0; font-size:11px; opacity:0.8;'>Opérateur ID #{user_id} - Rapport HTB</p>
            <a href='/deconnexion-mobile' style='position:absolute; right:15px; top:18px; color:white; text-decoration:none; font-size:12px; font-weight:bold; background:#1d4ed8; padding:6px 10px; border-radius:6px;'>Quitter</a>
        </header>
        <div id='reseau-statut' class='status-banner'></div>
        <div class='form-card'>
            <form id='htbForm' method='post' action='/maj-statut-mobile' enctype='multipart/form-data'>
                <input type='hidden' name='t_id' value='{user_id}'>
                <label>1. Quel Pylône validez-vous ?</label>
                <select name='c_id' required>{opt_pylones}</select>
                <label>2. Quelle étape venez-vous de finir ?</label>
                <select name='n_statut' required>
                    <option value='' disabled selected>--- Choisir l'étape accomplie ---</option>
                    <option>1-OUVERTURES DES ACCES</option>
                    <option>2-PIQUETAGE</option>
                    <option>3- TERRASSEMENT</option>
                    <option>4- FOUILLE</option>
                    <option>5- BETONNAGE FONDATIONS</option>
                    <option>6- LIVRAISONS PYLONES</option>
                    <option>7- ASSEMBLAGE ET LEVAGE</option>
                    <option>8- REVISION</option>
                    <option>9-VERIFICATION MISE A LA TERRE</option>
                    <option>9-MIS EN POULIE ET DEROULAGE CABLETTE</option>
                    <option>10-DEROULAGE CABLE</option>
                    <option>11- REGLAGE ET ANCRAGE</option>
                    <option>12- MISE EN PINCE</option>
                    <option>12- ESSAIS ET MISE EN SERVICE</option>
                </select>
                <label>Date de Début :</label>
                <input type='date' name='d_debut'>
                <label>Date de Fin :</label>
                <input type='date' name='d_fin'>
                <label style='color:#dc2626;'>🚨 Liste des Matériels Manquants / Observations :</label>
                <input type='text' name='manquants' placeholder='Ex: 4 isolateurs manquants, roche dure...'>
                <label>📸 Preuve Visuelle (Photo Terrain) :</label>
                <input type='file' name='photo' accept='image/*'>
                <button type='submit' id='submitBtn'>🚀 TRANSMETTRE AU BUREAU</button>
            </form>
        </div>
        <script>
            const banner = document.getElementById('reseau-statut');
            const form = document.getElementById('htbForm');
            function verifierReseau() {{
                if (navigator.onLine) {{
                    banner.className = 'status-banner online';
                    banner.innerText = '🌐 Connexion rétablie. Envoi en direct.';
                }} else {{
                    banner.className = 'status-banner offline';
                    banner.innerText = '📴 Mode Hors-Ligne actif. Rapports stockés localement.';
                }}
            }}
            window.addEventListener('online', verifierReseau);
            window.addEventListener('offline', verifierReseau);
            verifierReseau();
            form.addEventListener('submit', function(e) {{
                if (!navigator.onLine) {{
                    e.preventDefault();
                    const formData = new FormData(form);
                    const rapport = {{
                        t_id: formData.get('t_id'),
                        c_id: formData.get('c_id'),
                        n_statut: formData.get('n_statut'),
                        d_debut: formData.get('d_debut'),
                        d_fin: formData.get('d_fin'),
                        manquants: formData.get('manquants'),
                        date_sauvegarde: new Date().toLocaleString()
                    }};
                    let stock = JSON.parse(localStorage.getItem('suivi_htb_attente')) || [];
                    stock.push(rapport);
                    localStorage.setItem('suivi_htb_attente', JSON.stringify(stock));
                    alert('Rapport sauvegardé en mémoire locale (Hors-Ligne) ! Il sera synchronisé au retour du réseau.');
                    form.reset();
                }}
            }});
        </script>
    </body>
    </html>
    """
