"""
Script d'import Dealflow — à lancer une seule fois via Render Shell
Lit dealflow_import.json et insère les documents dans MongoDB.
"""

import os
import json
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME   = os.environ["DB_NAME"]

# Chemin du fichier JSON (à la racine du projet)
JSON_PATH = os.path.join(os.path.dirname(__file__), "dealflow_import.json")

def main():
    print("=" * 50)
    print("Import Dealflow → MongoDB")
    print("=" * 50)

    # Lecture du fichier JSON
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        docs = json.load(f)
    print(f"📄 {len(docs)} documents à importer")

    # Connexion MongoDB
    client = MongoClient(MONGO_URL)
    db     = client[DB_NAME]
    col    = db["dealflow_partners"]

    # Noms déjà en base (anti-doublons)
    existing = set(
        d["nom"].strip().lower()
        for d in col.find({}, {"nom": 1})
        if d.get("nom")
    )
    print(f"📦 {len(existing)} entrées déjà présentes\n")

    inserted = 0
    skipped  = 0

    for doc in docs:
        nom = doc.get("nom", "").strip()
        if not nom:
            skipped += 1
            continue
        if nom.lower() in existing:
            print(f"  ⏭️  '{nom}' déjà présent → ignoré")
            skipped += 1
            continue

        col.insert_one(doc)
        existing.add(nom.lower())
        inserted += 1
        print(f"  ✅ [{inserted:3d}] {nom}")

    print("\n" + "=" * 50)
    print(f"✅ Insérés  : {inserted}")
    print(f"⏭️  Ignorés  : {skipped}")
    print(f"📦 Total en base : {col.count_documents({})}")
    print("=" * 50)
    client.close()

if __name__ == "__main__":
    main()
