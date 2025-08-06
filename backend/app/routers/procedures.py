from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import os

from app.database import get_db, Procedure, Patient, Consent
from app.schemas.procedure import (
    ProcedureCreate, ProcedureResponse, PatientCreate, ConsentCreate,
    PROCEDURE_TYPES
)
from app.schemas.auth import User
from app.utils.auth import get_current_practitioner
from app.utils.blockchain import (
    hash_patient_data, hash_consent_file, record_procedure_on_blockchain,
    get_procedure_from_blockchain, get_patient_procedures_from_blockchain
)

router = APIRouter()

@router.post("/patients", response_model=PatientCreate)
async def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_practitioner)
):
    """Crée un nouveau patient (pseudonymisé)"""
    # Vérifier si le patient existe déjà
    existing_patient = db.query(Patient).filter(
        Patient.patient_hash == patient.patient_hash
    ).first()
    
    if existing_patient:
        raise HTTPException(
            status_code=400,
            detail="Patient déjà enregistré"
        )
    
    db_patient = Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    
    return db_patient

@router.get("/patients", response_model=List[PatientCreate])
async def get_patients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_practitioner)
):
    """Récupère la liste des patients"""
    patients = db.query(Patient).offset(skip).limit(limit).all()
    return patients

@router.get("/patients/{patient_hash}", response_model=PatientCreate)
async def get_patient(
    patient_hash: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_practitioner)
):
    """Récupère un patient par son hash"""
    patient = db.query(Patient).filter(Patient.patient_hash == patient_hash).first()
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient non trouvé")
    return patient

@router.post("/", response_model=ProcedureResponse)
async def create_procedure(
    procedure: ProcedureCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_practitioner)
):
    """Crée un nouvel acte médical"""
    # Vérifier que le type d'intervention est valide
    if procedure.procedure_type not in PROCEDURE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Type d'intervention invalide. Types supportés: {PROCEDURE_TYPES}"
        )
    
    # Vérifier que le patient existe
    patient = db.query(Patient).filter(
        Patient.patient_hash == procedure.patient_hash
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient non trouvé"
        )
    
    # Créer l'acte en base locale
    db_procedure = Procedure(
        patient_hash=procedure.patient_hash,
        practitioner_id=current_user.id,
        procedure_type=procedure.procedure_type,
        duration=procedure.duration,
        consent_hash=procedure.consent_hash,
        metadata=procedure.metadata
    )
    
    db.add(db_procedure)
    db.commit()
    db.refresh(db_procedure)
    
    # Enregistrer sur la blockchain (si configuré)
    try:
        # Note: En production, la clé privée devrait être sécurisée
        private_key = os.getenv("PRACTITIONER_PRIVATE_KEY")
        if private_key:
            blockchain_result = record_procedure_on_blockchain(
                patient_hash=procedure.patient_hash,
                procedure_type=procedure.procedure_type,
                duration=procedure.duration,
                consent_hash=procedure.consent_hash,
                metadata=procedure.metadata or "",
                private_key=private_key
            )
            
            if blockchain_result["success"]:
                db_procedure.blockchain_id = db_procedure.id  # ID local comme ID blockchain
                db_procedure.blockchain_tx_hash = blockchain_result["tx_hash"]
                db.commit()
                db.refresh(db_procedure)
    except Exception as e:
        print(f"Erreur blockchain: {e}")
        # L'acte est quand même créé en local
    
    return db_procedure

@router.get("/", response_model=List[ProcedureResponse])
async def get_procedures(
    skip: int = 0,
    limit: int = 100,
    patient_hash: Optional[str] = None,
    practitioner_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_practitioner)
):
    """Récupère la liste des actes avec filtres optionnels"""
    query = db.query(Procedure)
    
    if patient_hash:
        query = query.filter(Procedure.patient_hash == patient_hash)
    
    if practitioner_id:
        query = query.filter(Procedure.practitioner_id == practitioner_id)
    
    procedures = query.offset(skip).limit(limit).all()
    return procedures

@router.get("/{procedure_id}", response_model=ProcedureResponse)
async def get_procedure(
    procedure_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_practitioner)
):
    """Récupère un acte par son ID"""
    procedure = db.query(Procedure).filter(Procedure.id == procedure_id).first()
    if procedure is None:
        raise HTTPException(status_code=404, detail="Acte non trouvé")
    return procedure

@router.get("/patient/{patient_hash}/history", response_model=List[ProcedureResponse])
async def get_patient_history(
    patient_hash: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_practitioner)
):
    """Récupère l'historique complet d'un patient"""
    procedures = db.query(Procedure).filter(
        Procedure.patient_hash == patient_hash
    ).order_by(Procedure.created_at.desc()).all()
    
    return procedures

@router.get("/blockchain/{procedure_id}")
async def get_procedure_from_blockchain_endpoint(
    procedure_id: int,
    current_user: User = Depends(get_current_practitioner)
):
    """Récupère un acte directement depuis la blockchain"""
    procedure = get_procedure_from_blockchain(procedure_id)
    if procedure is None:
        raise HTTPException(status_code=404, detail="Acte non trouvé sur la blockchain")
    return procedure

@router.get("/blockchain/patient/{patient_hash}")
async def get_patient_procedures_from_blockchain_endpoint(
    patient_hash: str,
    current_user: User = Depends(get_current_practitioner)
):
    """Récupère tous les actes d'un patient depuis la blockchain"""
    procedures = get_patient_procedures_from_blockchain(patient_hash)
    return {"procedures": procedures}

@router.post("/upload-consent")
async def upload_consent(
    procedure_id: int = Form(...),
    consent_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_practitioner)
):
    """Upload un fichier de consentement"""
    # Vérifier que l'acte existe
    procedure = db.query(Procedure).filter(Procedure.id == procedure_id).first()
    if not procedure:
        raise HTTPException(status_code=404, detail="Acte non trouvé")
    
    # Vérifier que l'utilisateur est le praticien de l'acte
    if procedure.practitioner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Vous n'êtes pas autorisé à modifier cet acte"
        )
    
    # Lire le contenu du fichier
    content = await consent_file.read()
    
    # Générer le hash du fichier
    consent_hash = hash_consent_file(content)
    
    # Sauvegarder le fichier
    upload_dir = "uploads/consents"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, f"consent_{procedure_id}_{consent_hash[:8]}.pdf")
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Créer l'enregistrement de consentement
    consent = Consent(
        procedure_id=procedure_id,
        consent_hash=consent_hash,
        file_path=file_path
    )
    
    db.add(consent)
    db.commit()
    db.refresh(consent)
    
    # Mettre à jour le hash de consentement de l'acte
    procedure.consent_hash = consent_hash
    db.commit()
    
    return {
        "message": "Consentement uploadé avec succès",
        "consent_hash": consent_hash,
        "file_path": file_path
    }

@router.get("/types")
async def get_procedure_types():
    """Récupère la liste des types d'interventions supportés"""
    return {
        "procedure_types": PROCEDURE_TYPES,
        "count": len(PROCEDURE_TYPES)
    }

@router.get("/stats/summary")
async def get_procedure_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_practitioner)
):
    """Récupère des statistiques sur les actes"""
    total_procedures = db.query(Procedure).count()
    user_procedures = db.query(Procedure).filter(
        Procedure.practitioner_id == current_user.id
    ).count()
    
    # Statistiques par type d'intervention
    procedure_types = db.query(Procedure.procedure_type).all()
    type_counts = {}
    for proc_type in procedure_types:
        type_counts[proc_type[0]] = type_counts.get(proc_type[0], 0) + 1
    
    return {
        "total_procedures": total_procedures,
        "user_procedures": user_procedures,
        "procedure_types": type_counts,
        "unique_patients": db.query(Procedure.patient_hash).distinct().count()
    }