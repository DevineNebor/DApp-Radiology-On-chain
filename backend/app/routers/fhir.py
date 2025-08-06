from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime

from app.database import get_db, Procedure, Patient, User, FHIRResource
from app.schemas.auth import User as UserSchema
from app.utils.auth import get_current_practitioner
from app.utils.fhir_converter import (
    create_fhir_claim,
    create_fhir_patient,
    create_fhir_practitioner,
    create_fhir_coverage
)

router = APIRouter()

@router.get("/claim/{procedure_id}")
async def generate_fhir_claim(
    procedure_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_practitioner)
):
    """Génère un claim FHIR pour un acte spécifique"""
    # Récupérer l'acte
    procedure = db.query(Procedure).filter(Procedure.id == procedure_id).first()
    if not procedure:
        raise HTTPException(status_code=404, detail="Acte non trouvé")
    
    # Récupérer le patient
    patient = db.query(Patient).filter(Patient.patient_hash == procedure.patient_hash).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient non trouvé")
    
    # Récupérer le praticien
    practitioner = db.query(User).filter(User.id == procedure.practitioner_id).first()
    if not practitioner:
        raise HTTPException(status_code=404, detail="Praticien non trouvé")
    
    # Générer le claim FHIR
    claim = create_fhir_claim(procedure, patient, practitioner)
    
    # Sauvegarder en base
    fhir_resource = FHIRResource(
        resource_type="Claim",
        resource_id=f"claim-{procedure_id}",
        fhir_data=json.dumps(claim, indent=2)
    )
    
    db.add(fhir_resource)
    db.commit()
    
    return claim

@router.get("/patient/{patient_hash}")
async def generate_fhir_patient(
    patient_hash: str,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_practitioner)
):
    """Génère une ressource Patient FHIR"""
    patient = db.query(Patient).filter(Patient.patient_hash == patient_hash).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient non trouvé")
    
    fhir_patient = create_fhir_patient(patient)
    
    # Sauvegarder en base
    fhir_resource = FHIRResource(
        resource_type="Patient",
        resource_id=f"patient-{patient_hash}",
        fhir_data=json.dumps(fhir_patient, indent=2)
    )
    
    db.add(fhir_resource)
    db.commit()
    
    return fhir_patient

@router.get("/practitioner/{practitioner_id}")
async def generate_fhir_practitioner(
    practitioner_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_practitioner)
):
    """Génère une ressource Practitioner FHIR"""
    practitioner = db.query(User).filter(User.id == practitioner_id).first()
    if not practitioner:
        raise HTTPException(status_code=404, detail="Praticien non trouvé")
    
    fhir_practitioner = create_fhir_practitioner(practitioner)
    
    # Sauvegarder en base
    fhir_resource = FHIRResource(
        resource_type="Practitioner",
        resource_id=f"practitioner-{practitioner_id}",
        fhir_data=json.dumps(fhir_practitioner, indent=2)
    )
    
    db.add(fhir_resource)
    db.commit()
    
    return fhir_practitioner

@router.get("/patient/{patient_hash}/bundle")
async def generate_patient_bundle(
    patient_hash: str,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_practitioner)
):
    """Génère un bundle FHIR complet pour un patient"""
    # Récupérer le patient
    patient = db.query(Patient).filter(Patient.patient_hash == patient_hash).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient non trouvé")
    
    # Récupérer tous les actes du patient
    procedures = db.query(Procedure).filter(Procedure.patient_hash == patient_hash).all()
    
    # Créer le bundle FHIR
    bundle = {
        "resourceType": "Bundle",
        "id": f"bundle-patient-{patient_hash}",
        "type": "collection",
        "timestamp": datetime.utcnow().isoformat(),
        "entry": []
    }
    
    # Ajouter la ressource Patient
    fhir_patient = create_fhir_patient(patient)
    bundle["entry"].append({
        "resource": fhir_patient,
        "fullUrl": f"Patient/{patient_hash}"
    })
    
    # Ajouter les ressources Claim pour chaque acte
    for procedure in procedures:
        practitioner = db.query(User).filter(User.id == procedure.practitioner_id).first()
        if practitioner:
            claim = create_fhir_claim(procedure, patient, practitioner)
            bundle["entry"].append({
                "resource": claim,
                "fullUrl": f"Claim/{claim['id']}"
            })
    
    return bundle

@router.get("/resources")
async def get_fhir_resources(
    resource_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_practitioner)
):
    """Récupère les ressources FHIR stockées"""
    query = db.query(FHIRResource)
    
    if resource_type:
        query = query.filter(FHIRResource.resource_type == resource_type)
    
    resources = query.offset(skip).limit(limit).all()
    
    result = []
    for resource in resources:
        result.append({
            "id": resource.id,
            "resource_type": resource.resource_type,
            "resource_id": resource.resource_id,
            "fhir_data": json.loads(resource.fhir_data),
            "created_at": resource.created_at.isoformat(),
            "updated_at": resource.updated_at.isoformat()
        })
    
    return result

@router.get("/resources/{resource_id}")
async def get_fhir_resource(
    resource_id: str,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_practitioner)
):
    """Récupère une ressource FHIR spécifique"""
    resource = db.query(FHIRResource).filter(FHIRResource.resource_id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Ressource FHIR non trouvée")
    
    return {
        "id": resource.id,
        "resource_type": resource.resource_type,
        "resource_id": resource.resource_id,
        "fhir_data": json.loads(resource.fhir_data),
        "created_at": resource.created_at.isoformat(),
        "updated_at": resource.updated_at.isoformat()
    }

@router.post("/validate")
async def validate_fhir_resource(
    fhir_data: dict,
    current_user: UserSchema = Depends(get_current_practitioner)
):
    """Valide une ressource FHIR (validation basique)"""
    required_fields = {
        "Claim": ["resourceType", "id", "status", "type", "patient", "provider"],
        "Patient": ["resourceType", "id"],
        "Practitioner": ["resourceType", "id"]
    }
    
    resource_type = fhir_data.get("resourceType")
    if not resource_type:
        raise HTTPException(status_code=400, detail="resourceType manquant")
    
    if resource_type not in required_fields:
        raise HTTPException(status_code=400, detail=f"Type de ressource non supporté: {resource_type}")
    
    # Vérifier les champs requis
    missing_fields = []
    for field in required_fields[resource_type]:
        if field not in fhir_data:
            missing_fields.append(field)
    
    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Champs manquants pour {resource_type}: {missing_fields}"
        )
    
    return {
        "valid": True,
        "resource_type": resource_type,
        "message": "Ressource FHIR valide"
    }

@router.get("/stats")
async def get_fhir_stats(
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_practitioner)
):
    """Récupère des statistiques sur les ressources FHIR"""
    total_resources = db.query(FHIRResource).count()
    
    # Compter par type de ressource
    resource_types = db.query(FHIRResource.resource_type).all()
    type_counts = {}
    for res_type in resource_types:
        type_counts[res_type[0]] = type_counts.get(res_type[0], 0) + 1
    
    return {
        "total_resources": total_resources,
        "resource_types": type_counts,
        "last_created": db.query(FHIRResource).order_by(FHIRResource.created_at.desc()).first().created_at.isoformat() if total_resources > 0 else None
    }