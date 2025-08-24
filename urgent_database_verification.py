#!/usr/bin/env python3
"""
URGENT DATABASE VERIFICATION AFTER URL CHANGE
Vérification urgente de l'état des données après changement d'URL

CONTEXTE CRITIQUE:
- Changement REACT_APP_BACKEND_URL de preview.emergentagent.com vers localhost:8001
- L'utilisateur signale qu'il n'a plus aucune donnée de test
- Besoin de vérifier l'état de la base de données locale MongoDB
"""

import requests
import json
from datetime import datetime, date
import sys
import os

# Get backend URL from frontend .env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"❌ Erreur lecture frontend .env: {e}")
        return None

BASE_URL = get_backend_url()
if not BASE_URL:
    print("❌ ERREUR: Impossible de récupérer REACT_APP_BACKEND_URL depuis frontend/.env")
    sys.exit(1)

API_URL = f"{BASE_URL}/api"
print(f"🔍 VÉRIFICATION URGENTE - Base de données SURM à: {API_URL}")
print(f"📍 URL Backend configurée: {BASE_URL}")

def test_mongodb_connection():
    """Test 1: Vérifier la connexion à MongoDB locale"""
    print("\n" + "="*60)
    print("🔌 TEST 1: CONNEXION BASE DE DONNÉES MONGODB LOCALE")
    print("="*60)
    
    try:
        # Test simple endpoint pour vérifier la connexion
        response = requests.get(f"{API_URL}/statistics", timeout=10)
        if response.status_code == 200:
            print("✅ Connexion MongoDB locale RÉUSSIE")
            print(f"   Status: {response.status_code}")
            return True
        else:
            print(f"❌ Problème connexion MongoDB: Status {response.status_code}")
            print(f"   Réponse: {response.text[:200]}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ ERREUR CRITIQUE: Impossible de se connecter au backend")
        print(f"   URL testée: {API_URL}")
        print("   Vérifiez que le backend est démarré sur localhost:8001")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def count_existing_partners():
    """Test 2: Compter les partenaires sourcing et dealflow existants"""
    print("\n" + "="*60)
    print("📊 TEST 2: COMPTAGE PARTENAIRES EXISTANTS")
    print("="*60)
    
    sourcing_count = 0
    dealflow_count = 0
    
    # Compter partenaires sourcing
    try:
        response = requests.get(f"{API_URL}/sourcing", timeout=10)
        if response.status_code == 200:
            sourcing_partners = response.json()
            sourcing_count = len(sourcing_partners)
            print(f"✅ Partenaires SOURCING trouvés: {sourcing_count}")
        else:
            print(f"❌ Erreur récupération sourcing: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur sourcing: {e}")
    
    # Compter partenaires dealflow
    try:
        response = requests.get(f"{API_URL}/dealflow", timeout=10)
        if response.status_code == 200:
            dealflow_partners = response.json()
            dealflow_count = len(dealflow_partners)
            print(f"✅ Partenaires DEALFLOW trouvés: {dealflow_count}")
        else:
            print(f"❌ Erreur récupération dealflow: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur dealflow: {e}")
    
    total_count = sourcing_count + dealflow_count
    print(f"\n📈 RÉSUMÉ COMPTAGE:")
    print(f"   🏢 Sourcing: {sourcing_count} partenaires")
    print(f"   💼 Dealflow: {dealflow_count} partenaires")
    print(f"   🎯 TOTAL: {total_count} partenaires")
    
    if total_count == 0:
        print("\n🚨 ALERTE: BASE DE DONNÉES LOCALE VIDE!")
        print("   La transition preview.emergentagent.com → localhost:8001")
        print("   a résulté en une base de données locale sans données.")
    
    return sourcing_count, dealflow_count, total_count

def list_sample_partners():
    """Test 3: Lister quelques partenaires pour voir s'il y a des données"""
    print("\n" + "="*60)
    print("📋 TEST 3: ÉCHANTILLON DE DONNÉES EXISTANTES")
    print("="*60)
    
    # Échantillon sourcing
    try:
        response = requests.get(f"{API_URL}/sourcing", timeout=10)
        if response.status_code == 200:
            sourcing_partners = response.json()
            if sourcing_partners:
                print(f"📊 ÉCHANTILLON SOURCING (premiers 5):")
                for i, partner in enumerate(sourcing_partners[:5]):
                    print(f"   {i+1}. {partner.get('nom_entreprise', 'N/A')} - {partner.get('statut', 'N/A')}")
                    print(f"      Domaine: {partner.get('domaine_activite', 'N/A')}")
                    print(f"      Pilote: {partner.get('pilote', 'N/A')}")
                    print(f"      Date entrée: {partner.get('date_entree_sourcing', 'N/A')}")
                    print()
            else:
                print("📊 SOURCING: Aucune donnée trouvée")
    except Exception as e:
        print(f"❌ Erreur échantillon sourcing: {e}")
    
    # Échantillon dealflow
    try:
        response = requests.get(f"{API_URL}/dealflow", timeout=10)
        if response.status_code == 200:
            dealflow_partners = response.json()
            if dealflow_partners:
                print(f"📊 ÉCHANTILLON DEALFLOW (premiers 5):")
                for i, partner in enumerate(dealflow_partners[:5]):
                    print(f"   {i+1}. {partner.get('nom', 'N/A')} - {partner.get('statut', 'N/A')}")
                    print(f"      Domaine: {partner.get('domaine', 'N/A')}")
                    print(f"      Pilote: {partner.get('pilote', 'N/A')}")
                    print(f"      Date réception: {partner.get('date_reception_fichier', 'N/A')}")
                    print()
            else:
                print("📊 DEALFLOW: Aucune donnée trouvée")
    except Exception as e:
        print(f"❌ Erreur échantillon dealflow: {e}")

def create_test_data_for_user():
    """Test 4: Créer des données de test si la base est vide"""
    print("\n" + "="*60)
    print("🏗️ TEST 4: CRÉATION DONNÉES DE TEST POUR L'UTILISATEUR")
    print("="*60)
    
    # Données de test réalistes pour l'innovation française
    test_sourcing_partners = [
        {
            "nom_entreprise": "GreenTech Innovations",
            "statut": "A traiter",
            "pays_origine": "France",
            "domaine_activite": "Développement Durable",
            "typologie": "Startup",
            "objet": "Solutions IoT pour optimisation énergétique",
            "cas_usage": "Réduction consommation énergétique bâtiments tertiaires",
            "technologie": "IoT, Intelligence Artificielle",
            "source": "VivaTech 2024",
            "date_entree_sourcing": "2024-03-15",
            "interet": True,
            "pilote": "Marie Dubois",
            "actions_commentaires": "Startup prometteuse avec technologie mature",
            "date_prochaine_action": "2024-04-15"
        },
        {
            "nom_entreprise": "FinTech Secure Pro",
            "statut": "Klaxoon",
            "pays_origine": "France",
            "domaine_activite": "Services Financiers",
            "typologie": "Scale-up",
            "objet": "Sécurisation transactions blockchain",
            "cas_usage": "Authentification biométrique pour paiements",
            "technologie": "Blockchain, Biométrie",
            "source": "Réseau partenaires",
            "date_entree_sourcing": "2024-02-20",
            "interet": True,
            "pilote": "Jean Martin",
            "actions_commentaires": "Session Klaxoon planifiée pour validation concept",
            "date_prochaine_action": "2024-04-10"
        },
        {
            "nom_entreprise": "HealthTech Analytics",
            "statut": "A traiter",
            "pays_origine": "Suisse",
            "domaine_activite": "Santé",
            "typologie": "Startup",
            "objet": "IA pour diagnostic médical précoce",
            "cas_usage": "Détection précoce cancers par analyse d'images",
            "technologie": "Deep Learning, Vision par ordinateur",
            "source": "Salon MedTech Geneva",
            "date_entree_sourcing": "2024-03-01",
            "interet": True,
            "pilote": "Sophie Laurent",
            "actions_commentaires": "Technologie très innovante, à évaluer rapidement",
            "date_prochaine_action": "2024-04-05"
        }
    ]
    
    test_dealflow_partners = [
        {
            "nom": "MobilityTech Solutions",
            "statut": "En cours avec les métiers",
            "domaine": "Transport",
            "typologie": "PME",
            "objet": "Optimisation flux de transport urbain",
            "source": "Appel à projets Smart City",
            "pilote": "Marie Dubois",
            "metiers_concernes": "DSI, Mobilité Urbaine",
            "date_reception_fichier": "2024-01-15",
            "date_pre_qualification": "2024-01-30",
            "date_presentation_meetup_referents": "2024-02-15",
            "actions_commentaires": "Pilote en cours avec équipes métiers",
            "date_prochaine_action": "2024-04-20"
        },
        {
            "nom": "CyberSec Advanced",
            "statut": "En cours avec l'équipe inno",
            "domaine": "Cybersécurité",
            "typologie": "Startup",
            "objet": "Détection avancée de menaces cyber",
            "source": "Forum Cybersécurité",
            "pilote": "Jean Martin",
            "metiers_concernes": "RSSI, DSI",
            "date_reception_fichier": "2024-02-01",
            "date_pre_qualification": "2024-02-10",
            "actions_commentaires": "Évaluation technique en cours",
            "date_prochaine_action": "2024-04-12"
        }
    ]
    
    created_sourcing = 0
    created_dealflow = 0
    
    # Créer partenaires sourcing
    print("🏢 Création partenaires SOURCING:")
    for partner_data in test_sourcing_partners:
        try:
            response = requests.post(f"{API_URL}/sourcing", json=partner_data, timeout=10)
            if response.status_code == 200:
                partner = response.json()
                created_sourcing += 1
                print(f"   ✅ {partner['nom_entreprise']} - {partner['domaine_activite']}")
            else:
                print(f"   ❌ Échec création {partner_data['nom_entreprise']}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur création {partner_data['nom_entreprise']}: {e}")
    
    # Créer partenaires dealflow
    print("\n💼 Création partenaires DEALFLOW:")
    for partner_data in test_dealflow_partners:
        try:
            response = requests.post(f"{API_URL}/dealflow", json=partner_data, timeout=10)
            if response.status_code == 200:
                partner = response.json()
                created_dealflow += 1
                print(f"   ✅ {partner['nom']} - {partner['domaine']}")
            else:
                print(f"   ❌ Échec création {partner_data['nom']}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur création {partner_data['nom']}: {e}")
    
    print(f"\n📈 RÉSUMÉ CRÉATION:")
    print(f"   🏢 Sourcing créés: {created_sourcing}/{len(test_sourcing_partners)}")
    print(f"   💼 Dealflow créés: {created_dealflow}/{len(test_dealflow_partners)}")
    print(f"   🎯 TOTAL créé: {created_sourcing + created_dealflow}")
    
    return created_sourcing, created_dealflow

def verify_final_state():
    """Test 5: Vérification finale de l'état de la base"""
    print("\n" + "="*60)
    print("🔍 TEST 5: VÉRIFICATION FINALE ÉTAT BASE DE DONNÉES")
    print("="*60)
    
    # Recompter après création
    try:
        sourcing_response = requests.get(f"{API_URL}/sourcing", timeout=10)
        dealflow_response = requests.get(f"{API_URL}/dealflow", timeout=10)
        
        if sourcing_response.status_code == 200 and dealflow_response.status_code == 200:
            sourcing_count = len(sourcing_response.json())
            dealflow_count = len(dealflow_response.json())
            total_count = sourcing_count + dealflow_count
            
            print(f"📊 ÉTAT FINAL BASE DE DONNÉES:")
            print(f"   🏢 Sourcing: {sourcing_count} partenaires")
            print(f"   💼 Dealflow: {dealflow_count} partenaires")
            print(f"   🎯 TOTAL: {total_count} partenaires")
            
            if total_count > 0:
                print(f"\n✅ BASE DE DONNÉES LOCALE OPÉRATIONNELLE")
                print(f"   L'utilisateur dispose maintenant de {total_count} partenaires de test")
            else:
                print(f"\n❌ BASE DE DONNÉES TOUJOURS VIDE")
                print(f"   Problème persistant après tentative de création")
            
            return total_count
        else:
            print("❌ Erreur vérification finale")
            return 0
    except Exception as e:
        print(f"❌ Erreur vérification finale: {e}")
        return 0

def main():
    """Fonction principale de vérification urgente"""
    print("🚨 VÉRIFICATION URGENTE DONNÉES SURM APRÈS CHANGEMENT URL")
    print("=" * 80)
    print(f"📅 Date/Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 URL Backend: {BASE_URL}")
    print(f"🔗 API Endpoint: {API_URL}")
    
    # Test 1: Connexion MongoDB
    connection_ok = test_mongodb_connection()
    if not connection_ok:
        print("\n🚨 ARRÊT: Impossible de continuer sans connexion backend")
        return False
    
    # Test 2: Comptage partenaires existants
    sourcing_count, dealflow_count, total_count = count_existing_partners()
    
    # Test 3: Échantillon de données
    list_sample_partners()
    
    # Test 4: Création données de test si nécessaire
    if total_count == 0:
        print("\n🏗️ BASE VIDE DÉTECTÉE - CRÉATION DONNÉES DE TEST")
        created_sourcing, created_dealflow = create_test_data_for_user()
    else:
        print(f"\n✅ BASE CONTIENT DÉJÀ {total_count} PARTENAIRES")
        print("   Pas besoin de créer des données de test")
    
    # Test 5: Vérification finale
    final_count = verify_final_state()
    
    # Résumé final
    print("\n" + "="*80)
    print("📋 RÉSUMÉ VÉRIFICATION URGENTE")
    print("="*80)
    print(f"🔌 Connexion MongoDB locale: {'✅ OK' if connection_ok else '❌ ÉCHEC'}")
    print(f"📊 Partenaires dans base locale: {final_count}")
    print(f"🎯 État base de données: {'✅ OPÉRATIONNELLE' if final_count > 0 else '❌ VIDE'}")
    
    if final_count > 0:
        print(f"\n✅ CONCLUSION: PROBLÈME RÉSOLU")
        print(f"   L'utilisateur dispose maintenant de données de test")
        print(f"   dans sa base MongoDB locale après transition URL")
    else:
        print(f"\n❌ CONCLUSION: PROBLÈME PERSISTANT")
        print(f"   La base locale reste vide malgré les tentatives")
        print(f"   Investigation supplémentaire nécessaire")
    
    return final_count > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)