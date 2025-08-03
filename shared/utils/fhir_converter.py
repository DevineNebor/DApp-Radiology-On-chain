"""
Convertisseur FHIR R4 pour la DApp de radiologie interventionnelle
Conforme aux standards HL7 FHIR R4 pour les claims et ressources médicales
"""

from datetime import datetime
from typing import Dict, Any, Optional
import hashlib

# Codes SNOMED CT pour les procédures de radiologie interventionnelle
SNOMED_PROCEDURE_CODES = {
    "embolisation": {
        "code": "433144002",
        "display": "Embolization procedure",
        "system": "http://snomed.info/sct"
    },
    "ponction": {
        "code": "261190007",
        "display": "Percutaneous puncture",
        "system": "http://snomed.info/sct"
    },
    "stent": {
        "code": "384692006",
        "display": "Insertion of stent",
        "system": "http://snomed.info/sct"
    },
    "angioplastie": {
        "code": "372024009",
        "display": "Angioplasty",
        "system": "http://snomed.info/sct"
    },
    "biopsie": {
        "code": "387713003",
        "display": "Surgical biopsy",
        "system": "http://snomed.info/sct"
    },
    "drainage": {
        "code": "174250002",
        "display": "Drainage procedure",
        "system": "http://snomed.info/sct"
    },
    "ablation": {
        "code": "713295009",
        "display": "Ablation",
        "system": "http://snomed.info/sct"
    },
    "radiofréquence": {
        "code": "173666000",
        "display": "Radiofrequency ablation",
        "system": "http://snomed.info/sct"
    },
    "cryothérapie": {
        "code": "173665001",
        "display": "Cryotherapy",
        "system": "http://snomed.info/sct"
    },
    "chimioembolisation": {
        "code": "430193006",
        "display": "Chemoembolization",
        "system": "http://snomed.info/sct"
    }
}

def create_fhir_claim(procedure, patient, practitioner) -> Dict[str, Any]:
    """
    Crée une ressource Claim FHIR R4 pour un acte de radiologie interventionnelle
    
    Args:
        procedure: Objet Procedure de la base de données
        patient: Objet Patient de la base de données
        practitioner: Objet User (praticien) de la base de données
    
    Returns:
        Dict contenant la ressource Claim FHIR
    """
    
    # Obtenir le code SNOMED pour le type de procédure
    snomed_code = SNOMED_PROCEDURE_CODES.get(
        procedure.procedure_type.lower(),
        {
            "code": "261190007",
            "display": "Percutaneous puncture",
            "system": "http://snomed.info/sct"
        }
    )
    
    # Créer la ressource Claim
    claim = {
        "resourceType": "Claim",
        "id": f"claim-{procedure.id}",
        "status": "active",
        "type": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/claim-type",
                "code": "institutional",
                "display": "Institutional"
            }]
        },
        "use": "claim",
        "patient": {
            "reference": f"Patient/{patient.patient_hash}",
            "display": f"Patient {patient.patient_hash[:8]}..."
        },
        "created": procedure.created_at.isoformat(),
        "provider": {
            "reference": f"Practitioner/{practitioner.id}",
            "display": practitioner.username
        },
        "priority": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/processpriority",
                "code": "normal",
                "display": "Normal"
            }]
        },
        "procedure": [{
            "sequence": 1,
            "procedureCodeableConcept": {
                "coding": [{
                    "system": snomed_code["system"],
                    "code": snomed_code["code"],
                    "display": snomed_code["display"]
                }],
                "text": procedure.procedure_type
            },
            "date": procedure.created_at.isoformat()
        }],
        "insurance": [{
            "sequence": 1,
            "focal": True,
            "coverage": {
                "reference": f"Coverage/coverage-{patient.patient_hash[:8]}"
            }
        }],
        "item": [{
            "sequence": 1,
            "careTeamSequence": [1],
            "productOrService": {
                "coding": [{
                    "system": snomed_code["system"],
                    "code": snomed_code["code"],
                    "display": snomed_code["display"]
                }]
            },
            "servicedDate": procedure.created_at.isoformat(),
            "quantity": {
                "value": 1,
                "unit": "procedure"
            }
        }],
        "total": {
            "currency": "EUR",
            "value": 0  # À calculer selon la tarification
        },
        "meta": {
            "versionId": "1",
            "lastUpdated": procedure.updated_at.isoformat(),
            "source": "#radiology-dapp"
        }
    }
    
    # Ajouter les métadonnées blockchain si disponibles
    if procedure.blockchain_tx_hash:
        claim["meta"]["extension"] = [{
            "url": "http://radiology-dapp.com/blockchain-transaction",
            "valueString": procedure.blockchain_tx_hash
        }]
    
    # Ajouter le hash du consentement
    if procedure.consent_hash:
        claim["supportingInfo"] = [{
            "sequence": 1,
            "category": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/claim-informationcategory",
                    "code": "consent",
                    "display": "Consent"
                }]
            },
            "valueString": procedure.consent_hash
        }]
    
    return claim

def create_fhir_patient(patient) -> Dict[str, Any]:
    """
    Crée une ressource Patient FHIR R4 (pseudonymisée)
    
    Args:
        patient: Objet Patient de la base de données
    
    Returns:
        Dict contenant la ressource Patient FHIR
    """
    
    patient_resource = {
        "resourceType": "Patient",
        "id": patient.patient_hash,
        "identifier": [{
            "system": "http://radiology-dapp.com/patient",
            "value": patient.patient_hash
        }],
        "active": True,
        "meta": {
            "versionId": "1",
            "lastUpdated": patient.created_at.isoformat(),
            "source": "#radiology-dapp",
            "security": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v3-Confidentiality",
                    "code": "R",
                    "display": "Restricted"
                }]
            }]
        }
    }
    
    # Ajouter les informations pseudonymisées si disponibles
    if patient.first_name_hash:
        patient_resource["name"] = [{
            "use": "official",
            "text": f"Patient {patient.patient_hash[:8]}..."
        }]
    
    return patient_resource

def create_fhir_practitioner(practitioner) -> Dict[str, Any]:
    """
    Crée une ressource Practitioner FHIR R4
    
    Args:
        practitioner: Objet User (praticien) de la base de données
    
    Returns:
        Dict contenant la ressource Practitioner FHIR
    """
    
    practitioner_resource = {
        "resourceType": "Practitioner",
        "id": str(practitioner.id),
        "identifier": [{
            "system": "http://radiology-dapp.com/practitioner",
            "value": str(practitioner.id)
        }],
        "active": practitioner.is_active,
        "name": [{
            "use": "official",
            "text": practitioner.username
        }],
        "telecom": [{
            "system": "email",
            "value": practitioner.email,
            "use": "work"
        }],
        "qualification": [{
            "identifier": [{
                "system": "http://radiology-dapp.com/qualification",
                "value": practitioner.role
            }],
            "code": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/practitioner-role",
                    "code": "doctor",
                    "display": "Doctor"
                }]
            },
            "period": {
                "start": practitioner.created_at.isoformat()
            }
        }],
        "meta": {
            "versionId": "1",
            "lastUpdated": practitioner.updated_at.isoformat(),
            "source": "#radiology-dapp"
        }
    }
    
    # Ajouter l'adresse wallet si disponible
    if practitioner.wallet_address:
        practitioner_resource["extension"] = [{
            "url": "http://radiology-dapp.com/wallet-address",
            "valueString": practitioner.wallet_address
        }]
    
    return practitioner_resource

def create_fhir_coverage(patient_hash: str, insurance_info: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Crée une ressource Coverage FHIR R4
    
    Args:
        patient_hash: Hash du patient
        insurance_info: Informations d'assurance optionnelles
    
    Returns:
        Dict contenant la ressource Coverage FHIR
    """
    
    coverage = {
        "resourceType": "Coverage",
        "id": f"coverage-{patient_hash[:8]}",
        "status": "active",
        "type": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "EHCPOL",
                "display": "extended healthcare"
            }]
        },
        "subscriber": {
            "reference": f"Patient/{patient_hash}"
        },
        "beneficiary": {
            "reference": f"Patient/{patient_hash}"
        },
        "period": {
            "start": datetime.utcnow().isoformat()
        },
        "meta": {
            "versionId": "1",
            "lastUpdated": datetime.utcnow().isoformat(),
            "source": "#radiology-dapp"
        }
    }
    
    if insurance_info:
        coverage.update(insurance_info)
    
    return coverage

def create_fhir_bundle(resources: list, bundle_type: str = "collection") -> Dict[str, Any]:
    """
    Crée un Bundle FHIR R4
    
    Args:
        resources: Liste des ressources FHIR
        bundle_type: Type de bundle (collection, searchset, etc.)
    
    Returns:
        Dict contenant le Bundle FHIR
    """
    
    bundle = {
        "resourceType": "Bundle",
        "id": f"bundle-{hashlib.md5(str(resources).encode()).hexdigest()[:8]}",
        "type": bundle_type,
        "timestamp": datetime.utcnow().isoformat(),
        "total": len(resources),
        "entry": []
    }
    
    for i, resource in enumerate(resources):
        entry = {
            "fullUrl": f"{resource['resourceType']}/{resource['id']}",
            "resource": resource,
            "search": {
                "mode": "match"
            }
        }
        bundle["entry"].append(entry)
    
    return bundle

def validate_fhir_claim(claim: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valide une ressource Claim FHIR
    
    Args:
        claim: Ressource Claim à valider
    
    Returns:
        Dict avec les résultats de validation
    """
    
    errors = []
    warnings = []
    
    # Vérifier les champs requis
    required_fields = ["resourceType", "id", "status", "type", "patient", "provider"]
    for field in required_fields:
        if field not in claim:
            errors.append(f"Champ requis manquant: {field}")
    
    # Vérifier le resourceType
    if claim.get("resourceType") != "Claim":
        errors.append("resourceType doit être 'Claim'")
    
    # Vérifier le status
    valid_statuses = ["active", "cancelled", "draft", "entered-in-error"]
    if claim.get("status") not in valid_statuses:
        errors.append(f"Status invalide. Valeurs autorisées: {valid_statuses}")
    
    # Vérifier la structure des procédures
    if "procedure" in claim:
        for i, procedure in enumerate(claim["procedure"]):
            if "sequence" not in procedure:
                errors.append(f"Sequence manquante pour la procédure {i}")
            if "procedureCodeableConcept" not in procedure:
                errors.append(f"procedureCodeableConcept manquant pour la procédure {i}")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def get_snomed_code(procedure_type: str) -> Dict[str, str]:
    """
    Récupère le code SNOMED CT pour un type de procédure
    
    Args:
        procedure_type: Type de procédure
    
    Returns:
        Dict avec le code SNOMED
    """
    
    return SNOMED_PROCEDURE_CODES.get(
        procedure_type.lower(),
        {
            "code": "261190007",
            "display": "Percutaneous puncture",
            "system": "http://snomed.info/sct"
        }
    )