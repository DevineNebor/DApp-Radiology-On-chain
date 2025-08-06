# 🏥 DApp Radiologie Interventionnelle - MVP

Une application décentralisée (DApp) inspirée d'Avaneer Health pour la gestion des actes de radiologie interventionnelle avec traçabilité blockchain et standardisation FHIR.

## 🎯 Objectif

Cette DApp permet à un hôpital de :
- ✅ Enregistrer un acte interventionnel de manière vérifiable sur la blockchain
- ✅ Lier l'acte à un identifiant patient et un professionnel de santé
- ✅ Générer automatiquement un "claim" structuré FHIR pour assurance ou audit
- ✅ Tracer les consentements patients via hash blockchain
- ✅ Standardiser les données selon le modèle FHIR

## 🏗️ Architecture

```
├── contracts/           # Smart Contracts Solidity
├── backend/            # API FastAPI + Web3
├── frontend/           # Interface React + Wagmi
├── shared/             # Utilitaires partagés
└── docker/             # Configuration Docker
```

### Stack Technique

- **Smart Contract**: Solidity + Hardhat + Ethers.js
- **Backend**: FastAPI + SQLite + Web3.py
- **Frontend**: React.js + Tailwind CSS + Wagmi/Viem
- **Standards**: FHIR R4, HIPAA-compliant hashing

## 🚀 Installation et Lancement

### Prérequis

```bash
# Node.js 18+ et Python 3.9+
npm install -g hardhat
pip install fastapi uvicorn web3 sqlalchemy
```

### 1. Smart Contract (Hardhat)

```bash
cd contracts
npm install
npx hardhat compile
npx hardhat node  # Démarre le réseau local
npx hardhat run scripts/deploy.js --network localhost
```

### 2. Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend (React)

```bash
cd frontend
npm install
npm start
```

## 📋 Fonctionnalités

### 🔐 Authentification
- **Rôles**: Praticien, Admin
- **Méthode**: JWT avec clés privées/publiques
- **Sécurité**: Pas de stockage de données nominatives

### 📝 Enregistrement d'Acte
- ID patient pseudonymisé
- Type d'intervention (embolisation, ponction, stent...)
- Durée et praticien
- Upload consentement signé (hash SHA256)

### 📊 Visualisation
- Historique des actes par patient
- Génération automatique de claims FHIR
- Traçabilité blockchain en temps réel

## 🏥 Standards FHIR

### Claim Resource Example

```json
{
  "resourceType": "Claim",
  "id": "claim-12345",
  "status": "active",
  "type": {
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/claim-type",
      "code": "institutional"
    }]
  },
  "patient": {
    "reference": "Patient/patient-12345"
  },
  "created": "2024-01-15T10:30:00Z",
  "provider": {
    "reference": "Practitioner/practitioner-67890"
  },
  "procedure": [{
    "sequence": 1,
    "procedureCodeableConcept": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "433144002",
        "display": "Embolization procedure"
      }]
    }
  }],
  "insurance": [{
    "sequence": 1,
    "focal": true,
    "coverage": {
      "reference": "Coverage/coverage-12345"
    }
  }]
}
```

## 🔒 Sécurité et Conformité

### Protection des Données
- ✅ Aucune donnée nominative sur la blockchain
- ✅ Patient ID pseudonymisé (hash SHA256)
- ✅ Consentements stockés en hash uniquement
- ✅ Accès contrôlé par rôles

### Audit Trail
- ✅ Horodatage blockchain immuable
- ✅ Traçabilité complète des modifications
- ✅ Signature numérique des praticiens

## 🚧 Limitations Actuelles (MVP)

- ⚠️ Réseau blockchain local uniquement
- ⚠️ Pas de chiffrement end-to-end
- ⚠️ Interface basique (pas de notifications)
- ⚠️ Pas d'intégration PACS
- ⚠️ Validation FHIR limitée

## 🔮 Roadmap

- [ ] Déploiement sur réseau de test (Sepolia)
- [ ] Intégration PACS/DICOM
- [ ] Notifications temps réel
- [ ] Interface mobile responsive
- [ ] Audit automatisé
- [ ] Intégration systèmes hospitaliers

## 📞 Support

Pour toute question ou contribution :
- Issues GitHub
- Documentation technique détaillée dans `/docs`

---

**⚠️ Avertissement**: Cette application est un MVP à des fins de démonstration. Pour un usage en production, des audits de sécurité et de conformité sont requis.