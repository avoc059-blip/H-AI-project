"""
H-Ai Hospital System — Flask + SQLite Backend
Run: python app.py
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3, os, hashlib, secrets, subprocess, sys
from datetime import datetime

# ── POO Module ─────────────────────────────────────────────
from models import (
    Media, DossierMedical, VideoConsultation, RapportAudio,
    MediaInvalideException, EmailInvalideException, AnneeInvalideException,
    valider_email, valider_titre, sauvegarder_media, charger_media
)

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

DB_PATH = os.path.join(os.path.dirname(__file__), 'hai_database.db')

# ──────────────────────────────────────────────────────────
#  DATABASE INIT
# ──────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)    
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS doctors (
            id            INTEGER PRIMARY KEY,
            firstname     TEXT NOT NULL,
            lastname      TEXT NOT NULL,
            specialty     TEXT NOT NULL,
            fee           INTEGER DEFAULT 200,
            consultations INTEGER DEFAULT 0,
            gender        TEXT DEFAULT 'M',
            icon          TEXT DEFAULT 'fa-user-doctor',
            color         TEXT DEFAULT '#3B82F6',
            email         TEXT UNIQUE
        );

        CREATE TABLE IF NOT EXISTS medicines (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            type        TEXT,
            stock       INTEGER DEFAULT 0,
            explanation TEXT,
            posologie   TEXT,
            mutuelle    TEXT DEFAULT 'CNSS 70%'
        );

        CREATE TABLE IF NOT EXISTS patients (
            id          TEXT PRIMARY KEY,
            firstname   TEXT NOT NULL,
            lastname    TEXT NOT NULL,
            email       TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            cin         TEXT,
            dob         TEXT,
            gender      TEXT,
            phone       TEXT,
            mutuelle    TEXT DEFAULT 'CNSS',
            blood       TEXT,
            antecedents TEXT,
            allergies   TEXT,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name  TEXT NOT NULL,
            patient_id    TEXT,
            doctor_id     INTEGER,
            appt_date     TEXT,
            appt_time     TEXT,
            priority      TEXT DEFAULT 'Standard',
            status        TEXT DEFAULT 'En attente',
            reimbursement TEXT,
            patient_share TEXT,
            created_at    TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(doctor_id) REFERENCES doctors(id),
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        );
    """)

    # Seed doctors
    doctors = [
        (1,'Ahmed','Benali','Cardiologue',350,142,'M','fa-heart-pulse','#2563EB','a.benali@hia.ma'),
        (2,'Salima','Aouache','Généraliste',180,310,'F','fa-stethoscope','#14B8A6','s.aouache@hia.ma'),
        (3,'Youssef','Chakir','Neurologue',400,98,'M','fa-brain','#8B5CF6','y.chakir@hia.ma'),
        (4,'Nadia','El Fassi','Pédiatre',220,275,'F','fa-baby','#14B8A6','n.elfassi@hia.ma'),
        (5,'Karim','Mansouri','Orthopédiste',300,187,'M','fa-bone','#64748B','k.mansouri@hia.ma'),
        (6,'Fatima','Benhaddou','Gynécologue',280,230,'F','fa-venus','#A21CAF','f.benhaddou@hia.ma'),
        (7,'Omar','Tazi','Dermatologue',250,160,'M','fa-hand-dots','#14B8A6','o.tazi@hia.ma'),
        (8,'Hajar','Alaoui','ophtalmologie',260,145,'F','fa-eye','#A21CAF','h.alaoui@hia.ma'),
        (9,'Amine','Berrada','Dentiste',200,320,'M','fa-tooth','#10B981','a.berrada@hia.ma'),
    ]
    c.executemany("INSERT OR IGNORE INTO doctors VALUES (?,?,?,?,?,?,?,?,?,?)", doctors)

    # Seed medicines
    medicines = [
        ('Doliprane 1000mg','Antalgique / Antipyrétique',240,
         "Le paracétamol agit contre la douleur et la fièvre. Prendre un comprimé avec un grand verre d'eau, de préférence au cours d'un repas.",
         '1 comprimé toutes les 6h, max 3g/jour.','CNSS 70%'),
        ('Amoxicilline 500mg','Antibiotique',88,
         "Antibiotique à large spectre actif contre les bactéries. Terminer la cure complète.",
         '1 gélule 3×/jour pendant 7 jours.','CNSS 70%'),
        ('Metformine 850mg','Antidiabétique',155,
         "Antidiabétique oral qui réduit la glycémie.",
         '1 comprimé 2×/jour avec les repas.','CNOPS 80%'),
        ('Atorvastatine 20mg','Hypolipémiant',102,
         "Réduit le mauvais cholestérol (LDL).",
         '1 comprimé le soir, à heure fixe.','CNSS 70%'),
        ('Oméprazole 20mg','Anti-acide',195,
         "Réduit l'acidité gastrique.",
         '1 gélule le matin à jeun.','CNSS 70%'),
        ('Ibuprofène 400mg','Anti-inflammatoire',175,
         "Anti-inflammatoire non stéroïdien.",
         '1 comprimé 3×/jour aux repas.','RAMED 100%'),
        ('Amlodipine 5mg','Antihypertenseur',130,
         "Traite l'hypertension artérielle.",
         '1 comprimé/jour à heure fixe.','CNOPS 80%'),
        ('Ventoline 100mcg','Bronchodilatateur',62,
         "Utilisé en cas de crise d'asthme.",
         '1-2 bouffées si nécessaire.','CNSS 70%'),
        ('Lorazépam 1mg','Anxiolytique',45,
         "Benzodiazépine pour l'anxiété. Ordonnance obligatoire.",
         '0.5 à 1mg 2-3×/jour.','CNSS 70%'),
        ('Fer + Acide Folique','Supplément en Fer',210,
         "Indiqué en cas d'anémie ferriprive.",
         '1 comprimé/jour pendant les repas.','RAMED 100%'),
        ('Insuline Glargine','Insuline',38,
         "Insuline basale à longue durée d'action.",
         'Injection sous-cutanée 1×/jour.','CNOPS 80%'),
        ('Ciprofloxacine 500mg','Antibiotique',72,
         "Antibiotique puissant pour infections urinaires.",
         '1 comprimé 2×/jour.','CNSS 70%'),
    ]
    c.executemany("INSERT OR IGNORE INTO medicines (name,type,stock,explanation,posologie,mutuelle) VALUES (?,?,?,?,?,?)", medicines)

    # Seed demo patients (passwords hashed)
    def hp(p): return hashlib.sha256(p.encode()).hexdigest()
    patients = [
        ('P001','Mohammed','Chraibi','m.chraibi@gmail.com', hp('Patient@2026'),
         'AB123456','1985-03-12','M','0661234567','CNSS','O+','Hypertension artérielle','Aspirine'),
        ('P002','Zineb','Ouali','z.ouali@gmail.com', hp('Patient@2026'),
         'CD789012','1992-07-24','F','0672345678','CNOPS','A+','Diabète type 2',''),
    ]
    c.executemany("INSERT OR IGNORE INTO patients VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))", patients)

    # Seed demo appointments
    appts = [
        (1,'Mohammed Chraibi','P001',1,'2026-05-20','09:00','Haute','Confirmé','245 DH','105 DH'),
        (2,'Zineb Ouali','P002',3,'2026-05-21','10:30','Standard','En attente','280 DH','120 DH'),
        (3,'Hassan Bakkali',None,6,'2026-05-22','14:00','Urgente','Confirmé','224 DH','56 DH'),
        (4,'Asmaa Rachidi',None,4,'2026-05-22','11:00','Standard','Confirmé','154 DH','66 DH'),
        (5,'Khalid Soussi',None,2,'2026-05-23','08:30','Basse','En attente','126 DH','54 DH'),
    ]
    c.executemany("INSERT OR IGNORE INTO appointments (id,patient_name,patient_id,doctor_id,appt_date,appt_time,priority,status,reimbursement,patient_share) VALUES (?,?,?,?,?,?,?,?,?,?)", appts)

    conn.commit()
    conn.close()
    print("✅ H-Ai SQLite database initialized.")

# ──────────────────────────────────────────────────────────
#  PAGES
# ──────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    return render_template('dashboard.html', user=session['user'])

@app.route('/doctors')
def doctors():
    if 'user' not in session:
        return redirect('/')
    return render_template('doctors.html', user=session['user'])

@app.route('/pharmacy')
def pharmacy():
    if 'user' not in session:
        return redirect('/')
    return render_template('pharmacy.html', user=session['user'])

@app.route('/appointments')
def appointments():
    if 'user' not in session:
        return redirect('/')
    return render_template('appointments.html', user=session['user'])

@app.route('/analysis')
def analysis():
    if 'user' not in session:
        return redirect('/')
    return render_template('analysis.html', user=session['user'])

@app.route('/patients')
def patients():
    if 'user' not in session:
        return redirect('/')
    if session['user'].get('role') == 'patient':
        return redirect('/dashboard')
    return render_template('patients.html', user=session['user'])

@app.route('/dossier/<patient_id>')
def dossier(patient_id):
    if 'user' not in session:
        return redirect('/')
    user = session['user']
    # Patient can only see their own dossier
    if user.get('role') == 'patient' and user.get('id') != patient_id:
        return redirect('/dashboard')
    return render_template('dossier.html', user=session['user'])

@app.route('/python')
def python_console():
    if 'user' not in session:
        return redirect('/')
    return render_template('python.html', user=session['user'])

@app.route('/parameters')
def parameters():
    if 'user' not in session:
        return redirect('/')
    return render_template('parameters.html', user=session['user'])

@app.route('/sos')
def sos():
    subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), 'sos_window.py')])
    return redirect(request.referrer or url_for('dashboard'))

# ──────────────────────────────────────────────────────────
#  AUTH API
# ──────────────────────────────────────────────────────────
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email','').strip().lower()
    password = data.get('password','')
    role = data.get('role','')

    # Admin hardcoded
    if role == 'admin' and email == 'admin@hia.ma' and password == 'ADMIN@HAI2026':
        session['user'] = {'id':'ADMIN','name':'Administrateur H-Ai','role':'admin','email':email,'initials':'AD'}
        return jsonify({'ok':True,'role':'admin','redirect':'/dashboard'})

    # Médecin: check doctors table
    if role == 'medecin':
        conn = get_db()
        doc = conn.execute("SELECT * FROM doctors WHERE email=?", [email]).fetchone()
        conn.close()
        if doc and password == 'MED@HAI2026':
            session['user'] = {
                'id': doc['id'], 'name': f"{doc['firstname']} {doc['lastname']}",
                'role':'medecin', 'email':email,
                'specialty': doc['specialty'],
                'initials': doc['firstname'][0]+doc['lastname'][0]
            }
            return jsonify({'ok':True,'role':'medecin','redirect':'/dashboard'})
        return jsonify({'ok':False,'error':'Email ou mot de passe incorrect.'})

    # Patient: check patients table
    if role == 'patient':
        hp = hashlib.sha256(password.encode()).hexdigest()
        conn = get_db()
        pat = conn.execute("SELECT * FROM patients WHERE email=? AND password=?", [email, hp]).fetchone()
        conn.close()
        if pat:
            session['user'] = {
                'id': pat['id'], 'name': f"{pat['firstname']} {pat['lastname']}",
                'role':'patient', 'email':email,
                'initials': pat['firstname'][0]+pat['lastname'][0],
                'mutuelle': pat['mutuelle'], 'blood': pat['blood']
            }
            return jsonify({'ok':True,'role':'patient','redirect':'/dashboard'})
        return jsonify({'ok':False,'error':'Email ou mot de passe incorrect.'})

    return jsonify({'ok':False,'error':'Rôle invalide.'})

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json
    email = data.get('email','').strip().lower()
    password = data.get('password','')
    try:
        conn = get_db()
        count = conn.execute("SELECT COUNT(*) as n FROM patients").fetchone()['n']
        new_id = f"P{str(count+1).zfill(3)}"
        hp = hashlib.sha256(password.encode()).hexdigest()
        conn.execute("""INSERT INTO patients
            (id,firstname,lastname,email,password,cin,dob,gender,phone,mutuelle,blood,antecedents,allergies)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            [new_id, data['firstname'], data['lastname'], email, hp,
             data.get('cin',''), data.get('dob',''), data.get('gender',''),
             data.get('phone',''), data.get('mutuelle','CNSS'),
             data.get('blood',''), data.get('antecedents',''), data.get('allergies','')])
        conn.commit()
        conn.close()
        return jsonify({'ok':True})
    except Exception as e:
        return jsonify({'ok':False,'error': str(e)})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'ok':True})

# ──────────────────────────────────────────────────────────
#  DOCTORS API
# ──────────────────────────────────────────────────────────
@app.route('/api/doctors', methods=['GET'])
def api_get_doctors():
    conn = get_db()
    rows = conn.execute("SELECT * FROM doctors ORDER BY lastname").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/doctors', methods=['POST'])
def api_add_doctor():
    data = request.json
    conn = get_db()
    conn.execute("""INSERT INTO doctors (firstname,lastname,specialty,fee,gender,icon,color,email)
                    VALUES (?,?,?,?,?,?,?,?)""",
        [data['firstname'], data['lastname'], data['specialty'],
         int(data.get('fee',200)), data.get('gender','M'),
         'fa-user-doctor', '#3B82F6', data.get('email','')])
    conn.commit()
    conn.close()
    return jsonify({'ok':True})

# ──────────────────────────────────────────────────────────
#  MEDICINES API
# ──────────────────────────────────────────────────────────
@app.route('/api/medicines', methods=['GET'])
def api_get_medicines():
    q = request.args.get('q','').lower()
    conn = get_db()
    if q:
        rows = conn.execute("SELECT * FROM medicines WHERE lower(name) LIKE ?", [f'%{q}%']).fetchall()
    else:
        rows = conn.execute("SELECT * FROM medicines").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ──────────────────────────────────────────────────────────
#  APPOINTMENTS API
# ──────────────────────────────────────────────────────────
@app.route('/api/appointments', methods=['GET'])
def api_get_appointments():
    conn = get_db()
    user = session.get('user', {})
    if user.get('role') == 'patient':
        rows = conn.execute("""
            SELECT a.*, d.firstname, d.lastname, d.gender FROM appointments a
            LEFT JOIN doctors d ON a.doctor_id=d.id
            WHERE a.patient_id=?
            ORDER BY a.id DESC""", [user['id']]).fetchall()
    elif user.get('role') == 'medecin':
        rows = conn.execute("""
            SELECT a.*, d.firstname, d.lastname FROM appointments a
            LEFT JOIN doctors d ON a.doctor_id=d.id
            WHERE a.doctor_id=?
            ORDER BY a.appt_date DESC""", [user['id']]).fetchall()
    else:
        rows = conn.execute("""
            SELECT a.*, d.firstname, d.lastname, d.gender FROM appointments a
            LEFT JOIN doctors d ON a.doctor_id=d.id
            ORDER BY a.id DESC LIMIT 50""").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/appointments', methods=['POST'])
def api_add_appointment():
    data = request.json
    user = session.get('user', {})
    doc_id = int(data.get('doctor_id',1))
    conn = get_db()
    doc = conn.execute("SELECT fee FROM doctors WHERE id=?", [doc_id]).fetchone()
    mut = data.get('mutuelle','CNSS')
    rate = {'CNOPS':0.8,'RAMED':1.0,'SANS':0.0}.get(mut, 0.7)
    fee = doc['fee'] if doc else 200
    reimb = int(fee * rate)
    share = fee - reimb
    patient_id = user.get('id') if user.get('role') == 'patient' else None
    conn.execute("""INSERT INTO appointments
        (patient_name,patient_id,doctor_id,appt_date,appt_time,priority,status,reimbursement,patient_share)
        VALUES (?,?,?,?,?,?,'Confirmé',?,?)""",
        [data['patient_name'], patient_id, doc_id,
         data['appt_date'], data['appt_time'], data.get('priority','Standard'),
         f'{reimb} DH', f'{share} DH'])
    conn.commit()
    conn.close()
    return jsonify({'ok':True,'reimbursement':f'{reimb} DH','patient_share':f'{share} DH'})

# ──────────────────────────────────────────────────────────
#  PATIENT API
# ──────────────────────────────────────────────────────────
@app.route('/api/patient/me', methods=['GET'])
def api_patient_me():
    user = session.get('user')
    if not user or user.get('role') != 'patient':
        return jsonify({'ok':False,'error':'Non autorisé'}), 403
    conn = get_db()
    pat = conn.execute("SELECT * FROM patients WHERE id=?", [user['id']]).fetchone()
    conn.close()
    if pat:
        p = dict(pat)
        p.pop('password', None)
        return jsonify(p)
    return jsonify({'ok':False}), 404

# ──────────────────────────────────────────────────────────
#  PATIENTS API
# ──────────────────────────────────────────────────────────
@app.route('/api/patients', methods=['GET'])
def api_get_patients():
    user = session.get('user', {})
    if user.get('role') == 'patient':
        return jsonify({'ok':False,'error':'Non autorisé'}), 403
    conn = get_db()
    rows = conn.execute("SELECT * FROM patients ORDER BY lastname").fetchall()
    conn.close()
    result = []
    for r in rows:
        p = dict(r)
        p.pop('password', None)
        result.append(p)
    return jsonify(result)

@app.route('/api/patients/<patient_id>', methods=['GET'])
def api_get_patient(patient_id):
    user = session.get('user', {})
    # Patient can only access their own record
    if user.get('role') == 'patient' and user.get('id') != patient_id:
        return jsonify({'ok':False,'error':'Non autorisé'}), 403
    conn = get_db()
    pat = conn.execute("SELECT * FROM patients WHERE id=?", [patient_id]).fetchone()
    conn.close()
    if not pat:
        return jsonify({'ok':False,'error':'Patient introuvable'}), 404
    p = dict(pat)
    p.pop('password', None)
    return jsonify(p)

# ──────────────────────────────────────────────────────────
#  TIKENTER — Analyse IA du Dossier Patient
# ──────────────────────────────────────────────────────────
@app.route('/api/tikenter', methods=['POST'])
def api_tikenter():
    user = session.get('user', {})
    if not user:
        return jsonify({'ok': False, 'error': 'Non autorisé'}), 403

    data = request.json
    patient_id = data.get('patient_id', '')

    conn = get_db()
    pat = conn.execute("SELECT * FROM patients WHERE id=?", [patient_id]).fetchone()
    appts = conn.execute("""
        SELECT a.*, d.firstname as doc_firstname, d.lastname as doc_lastname, d.specialty
        FROM appointments a
        LEFT JOIN doctors d ON a.doctor_id = d.id
        WHERE a.patient_id=?
        ORDER BY a.appt_date DESC LIMIT 10
    """, [patient_id]).fetchall()
    conn.close()

    if not pat:
        return jsonify({'ok': False, 'error': 'Patient introuvable'}), 404

    p = dict(pat)
    p.pop('password', None)
    appts_list = [dict(a) for a in appts]

    age = ''
    if p.get('dob'):
        from datetime import date
        try:
            dob = date.fromisoformat(p['dob'])
            age = str((date.today() - dob).days // 365) + ' ans'
        except:
            age = '—'

    appts_text = '\n'.join([
        f"  - {a.get('appt_date','')} | Dr. {a.get('doc_firstname','')} {a.get('doc_lastname','')} ({a.get('specialty','')}) | {a.get('status','')} | Priorité: {a.get('priority','')}"
        for a in appts_list
    ]) or '  Aucun rendez-vous enregistré.'

    prompt = f"""Tu es un assistant médical IA pour le système hospitalier H-Ai.
Analyse le dossier médical suivant et fournis un résumé clinique structuré en français.

--- DOSSIER PATIENT ---
Nom complet   : {p.get('firstname','')} {p.get('lastname','')}
ID            : {p.get('id','')}
Âge           : {age}
Genre         : {'Féminin' if p.get('gender') == 'F' else 'Masculin'}
Groupe sanguin: {p.get('blood') or 'Non renseigné'}
Mutuelle      : {p.get('mutuelle') or 'Non renseignée'}
Antécédents   : {p.get('antecedents') or 'Aucun'}
Allergies     : {p.get('allergies') or 'Aucune'}

--- HISTORIQUE RDV ---
{appts_text}
-----------------------

Fournis une analyse structurée avec :
1. 📋 Résumé du profil patient
2. ⚠️ Points d'attention médicaux (antécédents, allergies, risques)
3. 💊 Recommandations générales (suivi, précautions)
4. 📅 Observation sur le parcours de soins (fréquence RDV, spécialistes)

Reste concis, professionnel et bienveillant. Maximum 250 mots."""

    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        return jsonify({'ok': False, 'error': "Clé API Anthropic manquante. Ajoutez ANTHROPIC_API_KEY dans votre fichier .env"}), 500

    import urllib.request, json as jsonlib
    payload = jsonlib.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.anthropic.com/v1/messages',
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01'
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = jsonlib.loads(resp.read().decode('utf-8'))
            text = result['content'][0]['text']
            return jsonify({'ok': True, 'analyse': text})
    except Exception as e:
        return jsonify({'ok': False, 'error': f"Erreur API: {str(e)}"}), 500

# ──────────────────────────────────────────────────────────
#  STATS API
# ──────────────────────────────────────────────────────────
@app.route('/api/stats', methods=['GET'])
def api_stats():
    conn = get_db()
    doctors_count  = conn.execute("SELECT COUNT(*) as n FROM doctors").fetchone()['n']
    patients_count = conn.execute("SELECT COUNT(*) as n FROM patients").fetchone()['n']
    appts_count    = conn.execute("SELECT COUNT(*) as n FROM appointments").fetchone()['n']
    meds_count     = conn.execute("SELECT COUNT(*) as n FROM medicines").fetchone()['n']
    conn.close()
    return jsonify({
        'doctors': doctors_count,
        'patients': patients_count,
        'appointments': appts_count,
        'medicines': meds_count
    })

# ──────────────────────────────────────────────────────────
#  POO DEMO API
# ──────────────────────────────────────────────────────────
@app.route('/api/demo-poo', methods=['GET'])
def demo_poo():
    """Démonstration live de tous les concepts POO."""
    resultats = []

    # Polymorphisme + Héritage
    medias = [
        DossierMedical("Dossier Chraibi Mohammed", 2026, 15, "P001"),
        VideoConsultation("Consultation Cardiologie", 2026, 30.0, 1),
        RapportAudio("Rapport Analyse Sanguine", 2026, 2.5),
    ]
    resultats.append({
        "concept": "Polymorphisme + Héritage",
        "data": [m.afficher() for m in medias]
    })

    # JSON Persistence
    sauvegarder_media(medias)
    recuperes = charger_media()
    resultats.append({
        "concept": "JSON Persistence",
        "data": f"{len(recuperes)} médias sauvegardés et rechargés depuis data.json"
    })

    # Regex Validation
    tests_email = ["a.benali@hia.ma", "s.aouache@univ.ma", "email_invalide"]
    email_results = []
    for email in tests_email:
        try:
            valider_email(email)
            email_results.append(f"✅ {email} — valide")
        except EmailInvalideException as e:
            email_results.append(f"❌ {str(e)}")
    resultats.append({"concept": "Regex Validation", "data": email_results})

    # Exception personnalisée
    try:
        DossierMedical("AB", 2026, -5, "P999")
    except MediaInvalideException as e:
        resultats.append({"concept": "Exception Personnalisée", "data": str(e)})

    return jsonify({"ok": True, "poo_demo": resultats})


# ──────────────────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    print("🏥 H-Ai Hospital System — http://localhost:5000")
    app.run(debug=True, port=5000)
