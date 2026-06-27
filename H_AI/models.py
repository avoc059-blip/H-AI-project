"""
models.py — H-Ai Hospital System
Module POO : Abstraction, Héritage, Encapsulation, Polymorphisme,
             Exceptions personnalisées, Regex, JSON Persistence
"""

from abc import ABC, abstractmethod
import re, json, os

# ══════════════════════════════════════════════════════════
#  EXCEPTIONS PERSONNALISÉES
# ══════════════════════════════════════════════════════════

class MediaInvalideException(Exception):
    """Levée quand un média est créé avec des données invalides."""
    pass

class EmailInvalideException(Exception):
    """Levée quand un email ne respecte pas le format attendu."""
    pass

class AnneeInvalideException(Exception):
    """Levée quand l'année est hors plage valide."""
    pass


# ══════════════════════════════════════════════════════════
#  VALIDATION PAR REGEX
# ══════════════════════════════════════════════════════════

def valider_email(email: str) -> bool:
    """
    Valide un email universitaire ou médical.
    Accepte : @univ.ma  @hia.ma  @gmail.com  @medecin.fr
    """
    pattern = r'^[\w.\-]+@[\w.\-]+\.(ma|com|fr|org)$'
    if not re.match(pattern, email, re.IGNORECASE):
        raise EmailInvalideException(
            f"Email invalide : '{email}'. Format attendu : utilisateur@domaine.ma"
        )
    return True


def valider_titre(titre: str) -> bool:
    """Titre : 3 à 100 caractères, lettres/chiffres/espaces/tirets."""
    pattern = r'^[\w\s\-\.]{3,100}$'
    if not re.match(pattern, titre, re.UNICODE):
        raise MediaInvalideException(
            f"Titre invalide : '{titre}'. Entre 3 et 100 caractères."
        )
    return True


def valider_annee(annee: int) -> bool:
    """Année entre 2000 et 2100."""
    if not re.match(r'^\d{4}$', str(annee)) or not (2000 <= int(annee) <= 2100):
        raise AnneeInvalideException(
            f"Année invalide : {annee}. Doit être entre 2000 et 2100."
        )
    return True


# ══════════════════════════════════════════════════════════
#  CLASSE ABSTRAITE — Media (ABC + Encapsulation)
# ══════════════════════════════════════════════════════════

class Media(ABC):
    """
    Classe abstraite représentant un média médical.
    Applique : Abstraction, Encapsulation (attributs privés), Polymorphisme.
    """

    def __init__(self, titre: str, annee: int):
        # Validation avant assignation
        valider_titre(titre)
        valider_annee(annee)

        self.__titre = titre    # attribut privé (Encapsulation)
        self.__annee = annee    # attribut privé (Encapsulation)

    # ── Getters / Setters (Encapsulation) ──────────────────
    def get_titre(self) -> str:
        return self.__titre

    def set_titre(self, titre: str):
        valider_titre(titre)
        self.__titre = titre

    def get_annee(self) -> int:
        return self.__annee

    def set_annee(self, annee: int):
        valider_annee(annee)
        self.__annee = annee

    # ── Méthode abstraite (Polymorphisme) ──────────────────
    @abstractmethod
    def afficher(self) -> str:
        """Chaque sous-classe implémente son propre affichage."""
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """Sérialisation pour JSON Persistence."""
        pass

    def __repr__(self):
        return self.afficher()


# ══════════════════════════════════════════════════════════
#  SOUS-CLASSES — Héritage + Polymorphisme
# ══════════════════════════════════════════════════════════

class DossierMedical(Media):
    """
    Dossier médical d'un patient.
    Héritage de Media.
    """

    def __init__(self, titre: str, annee: int, nb_pages: int, patient_id: str):
        super().__init__(titre, annee)
        if nb_pages <= 0:
            raise MediaInvalideException("Le nombre de pages doit être positif.")
        self.__nb_pages = nb_pages      # privé
        self.__patient_id = patient_id  # privé

    def get_nb_pages(self) -> int:
        return self.__nb_pages

    def get_patient_id(self) -> str:
        return self.__patient_id

    def afficher(self) -> str:
        return (f"📋 [DossierMedical] Titre: {self.get_titre()} | "
                f"Année: {self.get_annee()} | "
                f"Patient: {self.__patient_id} | "
                f"Pages: {self.__nb_pages}")

    def to_dict(self) -> dict:
        return {
            "type": "DossierMedical",
            "titre": self.get_titre(),
            "annee": self.get_annee(),
            "nb_pages": self.__nb_pages,
            "patient_id": self.__patient_id
        }


class VideoConsultation(Media):
    """
    Enregistrement vidéo d'une consultation.
    Héritage de Media.
    """

    def __init__(self, titre: str, annee: int, duree_min: float, doctor_id: int):
        super().__init__(titre, annee)
        if duree_min <= 0:
            raise MediaInvalideException("La durée doit être positive.")
        self.__duree_min = duree_min    # privé
        self.__doctor_id = doctor_id    # privé

    def get_duree(self) -> float:
        return self.__duree_min

    def get_doctor_id(self) -> int:
        return self.__doctor_id

    def afficher(self) -> str:
        return (f"🎥 [VideoConsultation] Titre: {self.get_titre()} | "
                f"Année: {self.get_annee()} | "
                f"Médecin ID: {self.__doctor_id} | "
                f"Durée: {self.__duree_min} min")

    def to_dict(self) -> dict:
        return {
            "type": "VideoConsultation",
            "titre": self.get_titre(),
            "annee": self.get_annee(),
            "duree_min": self.__duree_min,
            "doctor_id": self.__doctor_id
        }


class RapportAudio(Media):
    """
    Rapport audio (dictée médicale, résumé vocal).
    Héritage de Media.
    """

    def __init__(self, titre: str, annee: int, taille_mb: float):
        super().__init__(titre, annee)
        if taille_mb <= 0:
            raise MediaInvalideException("La taille du fichier doit être positive.")
        self.__taille_mb = taille_mb    # privé

    def get_taille(self) -> float:
        return self.__taille_mb

    def afficher(self) -> str:
        return (f"🎙️ [RapportAudio] Titre: {self.get_titre()} | "
                f"Année: {self.get_annee()} | "
                f"Taille: {self.__taille_mb} MB")

    def to_dict(self) -> dict:
        return {
            "type": "RapportAudio",
            "titre": self.get_titre(),
            "annee": self.get_annee(),
            "taille_mb": self.__taille_mb
        }


# ══════════════════════════════════════════════════════════
#  JSON PERSISTENCE
# ══════════════════════════════════════════════════════════

MEDIA_JSON = os.path.join(os.path.dirname(__file__), 'data.json')


def sauvegarder_media(media_list: list) -> None:
    """Sauvegarde la liste de médias dans data.json (mise à jour automatique)."""
    data = [m.to_dict() for m in media_list]
    with open(MEDIA_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def charger_media() -> list:
    """Charge et reconstruit les objets Media depuis data.json."""
    if not os.path.exists(MEDIA_JSON):
        return []
    with open(MEDIA_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    classes = {
        "DossierMedical": DossierMedical,
        "VideoConsultation": VideoConsultation,
        "RapportAudio": RapportAudio
    }
    result = []
    for item in data:
        cls_name = item.pop("type", None)
        if cls_name in classes:
            try:
                obj = classes[cls_name](**item)
                result.append(obj)
            except (MediaInvalideException, AnneeInvalideException) as e:
                print(f"⚠️ Erreur chargement: {e}")
    return result


# ══════════════════════════════════════════════════════════
#  DÉMONSTRATION (si lancé directement)
# ══════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 60)
    print("  H-Ai — Démonstration POO")
    print("=" * 60)

    # Création des objets
    medias = [
        DossierMedical("Dossier Chraibi Mohammed", 2026, 15, "P001"),
        VideoConsultation("Consultation Cardiologie", 2026, 30.0, 1),
        RapportAudio("Rapport Analyse Sanguine", 2026, 2.5),
    ]

    # Polymorphisme — même appel, résultats différents
    print("\n── Polymorphisme (afficher) ──")
    for m in medias:
        print(m.afficher())

    # JSON Persistence
    print("\n── JSON Persistence ──")
    sauvegarder_media(medias)
    print(f"✅ {len(medias)} médias sauvegardés dans data.json")

    recuperes = charger_media()
    print(f"✅ {len(recuperes)} médias rechargés depuis data.json")

    # Regex Validation
    print("\n── Regex Validation ──")
    try:
        valider_email("a.benali@hia.ma")
        print("✅ Email valide : a.benali@hia.ma")
    except EmailInvalideException as e:
        print(f"❌ {e}")

    try:
        valider_email("email_invalide")
        print("✅ Email valide")
    except EmailInvalideException as e:
        print(f"❌ {e}")

    # Exception personnalisée
    print("\n── Exception Personnalisée ──")
    try:
        bad = DossierMedical("AB", 2026, -5, "P999")
    except MediaInvalideException as e:
        print(f"✅ Exception capturée : {e}")

    print("\n" + "=" * 60)
