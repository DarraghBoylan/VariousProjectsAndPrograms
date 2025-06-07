import sqlite3
import os
import requests
import uuid
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type #pour le retry

print("dark vador va au marché qu'est ce qu'il achète ?")

# Co à la db
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "brouillon_tres_potable.db")

# Reset 
drop_sql = """
DROP TABLE IF EXISTS parametres;
DROP TABLE IF EXISTS uge;
DROP TABLE IF EXISTS moa;
DROP TABLE IF EXISTS distributeur;
DROP TABLE IF EXISTS departement_reseau;
DROP TABLE IF EXISTS communes_reseau;
DROP TABLE IF EXISTS reseau_udi;
DROP TABLE IF EXISTS communes;
DROP TABLE IF EXISTS Departements;
"""

conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.executescript(drop_sql)

# tables sql
schema_sql = """
CREATE TABLE IF NOT EXISTS Departements (
    code_departement VARCHAR(10) PRIMARY KEY,
    nom_departement VARCHAR(50)
);
CREATE TABLE IF NOT EXISTS communes (
    code_commune VARCHAR(5) PRIMARY KEY,
    nom_commune VARCHAR(50),
    code_departement VARCHAR(10),
    FOREIGN KEY (code_departement) REFERENCES Departements(code_departement)
);
CREATE TABLE IF NOT EXISTS reseau_udi (
    code_reseau VARCHAR PRIMARY KEY,
    nom_reseau VARCHAR
);
CREATE TABLE IF NOT EXISTS communes_reseau (
    code_commune VARCHAR(5),
    code_reseau VARCHAR,
    PRIMARY KEY (code_commune, code_reseau),
    FOREIGN KEY (code_commune) REFERENCES communes(code_commune),
    FOREIGN KEY (code_reseau) REFERENCES reseau_udi(code_reseau)
);
CREATE TABLE IF NOT EXISTS departement_reseau (
    code_departement VARCHAR(5),
    code_reseau VARCHAR,
    PRIMARY KEY (code_departement, code_reseau),
    FOREIGN KEY (code_departement) REFERENCES Departements(code_departement),
    FOREIGN KEY (code_reseau) REFERENCES reseau_udi(code_reseau)
);
CREATE TABLE IF NOT EXISTS distributeur (
    code_distributeur VARCHAR PRIMARY KEY,
    nom_distributeur VARCHAR,
    code_UGE VARCHAR
);
CREATE TABLE IF NOT EXISTS moa (
    code_moa VARCHAR PRIMARY KEY,
    nom_moa VARCHAR,
    code_UGE VARCHAR
);
CREATE TABLE IF NOT EXISTS uge (
    code_UGE VARCHAR PRIMARY KEY,
    nom_UGE VARCHAR,
    code_reseau VARCHAR,
    code_distributeur VARCHAR,
    code_moa VARCHAR,
    FOREIGN KEY (code_reseau) REFERENCES reseau_udi(code_reseau),
    FOREIGN KEY (code_distributeur) REFERENCES distributeur(code_distributeur),
    FOREIGN KEY (code_moa) REFERENCES moa(code_moa)
);
CREATE TABLE IF NOT EXISTS parametres (
    code_parametre VARCHAR(50) PRIMARY KEY,
    code_parametre_se VARCHAR(50),
    code_parametre_cas VARCHAR(50),
    libelle_parametre TEXT,
    libelle_parametre_maj TEXT,
    libelle_parametre_web TEXT,
    code_type_parametre VARCHAR(50),
    code_unite VARCHAR(50),
    libelle_unite TEXT,
    limite_qualite_parametre DECIMAL(10, 2),
    reference_qualite_parametre DECIMAL(10, 2)
);
"""
cur.executescript(schema_sql)
conn.commit()
conn.close()
print("Toutes les tables ont été supprimées.")

# requete http
base_url = "https://hubeau.eaufrance.fr/api/v1/qualite_eau_potable/resultats_dis"
page = 1
page_size = 10000

print("Téléchargement des données...")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

def generate_code(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

moa_dict = {}
distributeur_dict = {}
uge_dict = {}


#gerer erreur 502 (serveur error) askip l'api peut planter brievement et un peu au pif de temps en temps et ce serait normal
# donc je fais un raise exeption pour lui dire d'attendre 10 secondes avant de réessayer  
@retry(
    wait=wait_fixed(10),
    stop=stop_after_attempt(5), #il réessaye 5 fois
    retry=retry_if_exception_type(requests.exceptions.HTTPError)
)
def fetch_data_with_retry(url, params=None):
    response = requests.get(url, params=params)
    if response.status_code == 502:
        raise requests.exceptions.HTTPError("502 Bad Gateway")
    return response


#remplir db 10000 lignes à la fois
while page <= 11514:
    print(f"page {page}")
    params = {"size": page_size, "page": page}
    response = fetch_data_with_retry(base_url, params=params)#retry si erreur 502
    response.raise_for_status()
    page_data = response.json().get('data', [])

    if not page_data:
        print("Fin des données atteinte.")
        break

    for row in page_data:
        row = {k: v.strip() if isinstance(v, str) else v for k, v in row.items()}

        cur.execute("""
            INSERT OR IGNORE INTO Departements (code_departement, nom_departement)
            VALUES (?, ?)
        """, (row['code_departement'], row['nom_departement']))

        cur.execute("""
            INSERT OR IGNORE INTO communes (code_commune, nom_commune, code_departement)
            VALUES (?, ?, ?)
        """, (row['code_commune'], row['nom_commune'], row['code_departement']))

        reseaux = row.get('reseaux', [])
        if not reseaux:
            print(f"Aucune donnée réseau pour commune {row['code_commune']}")
            continue

        for reseau in reseaux:
            code_r = reseau.get('code')
            nom_r = reseau.get('nom')
            if not code_r or not nom_r:
                continue

            cur.execute("""
                INSERT OR IGNORE INTO reseau_udi (code_reseau, nom_reseau)
                VALUES (?, ?)
            """, (code_r, nom_r))

            cur.execute("""
                INSERT OR IGNORE INTO communes_reseau (code_commune, code_reseau)
                VALUES (?, ?)
            """, (row['code_commune'], code_r))

            cur.execute("""
                INSERT OR IGNORE INTO departement_reseau (code_departement, code_reseau)
                VALUES (?, ?)
            """, (row['code_departement'], code_r))

        nom_moa = row.get('nom_moa', '')
        if nom_moa and nom_moa not in moa_dict:
            code_moa = generate_code("moa")
            moa_dict[nom_moa] = code_moa
            cur.execute("""
                INSERT OR IGNORE INTO moa (code_moa, nom_moa, code_UGE)
                VALUES (?, ?, NULL)
            """, (code_moa, nom_moa))
        code_moa = moa_dict.get(nom_moa)

        nom_distributeur = row.get('nom_distributeur', '')
        if nom_distributeur and nom_distributeur not in distributeur_dict:
            code_distributeur = generate_code("dist")
            distributeur_dict[nom_distributeur] = code_distributeur
            cur.execute("""
                INSERT OR IGNORE INTO distributeur (code_distributeur, nom_distributeur, code_UGE)
                VALUES (?, ?, NULL)
            """, (code_distributeur, nom_distributeur))
        code_distributeur = distributeur_dict.get(nom_distributeur)

        nom_uge = row.get('nom_uge', '')
        key = (nom_uge, row['code_commune'])
        if key not in uge_dict:
            code_uge = generate_code("uge")
            uge_dict[key] = code_uge
            first_code_reseau = reseaux[0].get('code') if reseaux else None
            cur.execute("""
                INSERT OR IGNORE INTO uge (code_UGE, nom_UGE, code_reseau, code_distributeur, code_moa)
                VALUES (?, ?, ?, ?, ?)
            """, (code_uge, nom_uge, first_code_reseau, code_distributeur, code_moa))
        code_uge = uge_dict[key]

        cur.execute("UPDATE distributeur SET code_UGE = ? WHERE code_distributeur = ?", (code_uge, code_distributeur))
        cur.execute("UPDATE moa SET code_UGE = ? WHERE code_moa = ?", (code_uge, code_moa))

        code_parametre = row.get('code_parametre')
        if code_parametre:
            cur.execute("""
                INSERT OR IGNORE INTO parametres (
                    code_parametre,
                    code_parametre_se,
                    code_parametre_cas,
                    libelle_parametre,
                    libelle_parametre_maj,
                    libelle_parametre_web,
                    code_type_parametre,
                    code_unite,
                    libelle_unite,
                    limite_qualite_parametre,
                    reference_qualite_parametre
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row.get('code_parametre'),
                row.get('code_parametre_se'),
                row.get('code_parametre_cas'),
                row.get('libelle_parametre'),
                row.get('libelle_parametre_maj'),
                row.get('libelle_parametre_web'),
                row.get('code_type_parametre'),
                row.get('code_unite'),
                row.get('libelle_unite'),
                str(row.get('limite_qualite_parametre')).split()[0].replace('<', '').replace('=', '').replace(',', '.') if row.get('limite_qualite_parametre') else None,
                str(row.get('reference_qualite_parametre')).replace(',', '.') if row.get('reference_qualite_parametre') else None
            ))

    page += 1
    conn.commit()  

conn.close()
print("Pain, pain, pain, tartatin, tartatin")
