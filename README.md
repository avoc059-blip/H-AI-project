# 🏥 H-Ai Hospital System — v2.4

Plateforme hospitalière intelligente (Flask + SQLite + Claude AI)

---

## 📁 Structure du Projet

```
h-ai/
├── app.py                    ← Serveur Flask + API SQLite
├── hai_database.db           ← Base SQLite (créée automatiquement)
├── requirements.txt
└── templates/
    ├── base.html             ← Layout de base (head, toast, scripts)
    ├── layout.html           ← Layout avec sidebar + header
    ├── login.html            ← Page de connexion (3 rôles)
    ├── signup.html           ← Inscription patient (3 étapes)
    ├── dashboard.html        ← Tableau de bord (admin/médecin/patient)
    ├── doctors.html          ← Gestion des médecins
    ├── pharmacy.html         ← Pharmacie & médicaments
    ├── appointments.html     ← Prise de rendez-vous + AMO
    ├── analysis.html         ← Scanner clinique IA (upload image)
    ├── mediapipe.html        ← Gestes main MediaPipe + IA
    ├── python.html           ← Console Python + templates médicaux
    └── parameters.html       ← Paramètres + DB stats
```

---

## 🚀 Lancement

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer le serveur
python app.py

# 3. Ouvrir dans le navigateur
http://localhost:5000
```

---

## 🔐 Identifiants de démonstration

| Rôle          | Email                   | Mot de passe     |
|---------------|-------------------------|------------------|
| Administrateur | admin@hia.ma           | ADMIN@HAI2026    |
| Médecin        | a.benali@hia.ma        | MED@HAI2026      |
| Patient        | m.chraibi@gmail.com    | Patient@2026     |

---

## 🗃️ Base de données SQLite

Tables créées automatiquement au premier lancement :
- **doctors** — 9 médecins pré-chargés
- **patients** — 2 patients de démo
- **appointments** — 5 RDV de démo
- **medicines** — 12 médicaments avec posologies

---

## 🤖 Intelligence Artificielle

- **Diagnostic rapide** → Claude Sonnet (symptômes → recommandation)
- **Analyse clinique** → Vision IA sur images de bilans biologiques
- **Gestes MediaPipe** → Interprétation JSON structurée
- **Console Python** → Exécution simulée + explication de code

---

## 📱 Fonctionnalités

- Login/Signup multi-rôle (Admin, Médecin, Patient)
- Dashboard personnalisé selon le rôle
- Gestion médecins avec filtres spécialités
- Pharmacie avec explication médicale & stock
- Prise de RDV avec calcul AMO automatique (CNSS/CNOPS/RAMED)
- Scanner d'analyse médicale par IA (upload image)
- Détection de gestes MediaPipe + réponse IA pour patients sourds/muets
- Console Python avec 5 templates médicaux + AI explainer
- Paramètres système + inspection SQLite
