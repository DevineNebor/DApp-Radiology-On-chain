from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PatientBase(BaseModel):
    patient_hash: str
    first_name_hash: Optional[str] = None
    last_name_hash: Optional[str] = None
    birth_date_hash: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProcedureBase(BaseModel):
    patient_hash: str
    procedure_type: str = Field(..., description="Type d'intervention (embolisation, ponction, stent, etc.)")
    duration: int = Field(..., gt=0, description="Durée en minutes")
    consent_hash: str
    metadata: Optional[str] = None  # JSON FHIR

class ProcedureCreate(ProcedureBase):
    pass

class ProcedureUpdate(BaseModel):
    procedure_type: Optional[str] = None
    duration: Optional[int] = None
    consent_hash: Optional[str] = None
    metadata: Optional[str] = None

class Procedure(ProcedureBase):
    id: int
    blockchain_id: Optional[int] = None
    practitioner_id: int
    blockchain_tx_hash: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProcedureResponse(BaseModel):
    id: int
    blockchain_id: Optional[int]
    patient_hash: str
    practitioner_id: int
    procedure_type: str
    duration: int
    consent_hash: str
    metadata: Optional[str]
    blockchain_tx_hash: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ConsentBase(BaseModel):
    procedure_id: int
    consent_hash: str
    file_path: Optional[str] = None
    signed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class ConsentCreate(ConsentBase):
    pass

class Consent(ConsentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Types d'interventions supportés
PROCEDURE_TYPES = [
    "embolisation",
    "ponction",
    "stent",
    "angioplastie",
    "biopsie",
    "drainage",
    "ablation",
    "radiofréquence",
    "cryothérapie",
    "chimioembolisation"
]