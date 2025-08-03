from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./radiology_dapp.db")

# Créer le moteur de base de données
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Créer la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Créer la base pour les modèles
Base = declarative_base()

# Modèles de données
class User(Base):
    """Modèle utilisateur pour l'authentification"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="practitioner")  # practitioner, admin
    wallet_address = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    procedures = relationship("Procedure", back_populates="practitioner")

class Patient(Base):
    """Modèle patient (pseudonymisé)"""
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_hash = Column(String, unique=True, index=True)  # Hash du patient
    first_name_hash = Column(String)  # Hash du prénom
    last_name_hash = Column(String)   # Hash du nom
    birth_date_hash = Column(String)  # Hash de la date de naissance
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    procedures = relationship("Procedure", back_populates="patient")

class Procedure(Base):
    """Modèle acte médical (métadonnées locales)"""
    __tablename__ = "procedures"

    id = Column(Integer, primary_key=True, index=True)
    blockchain_id = Column(Integer, unique=True, index=True)  # ID sur la blockchain
    patient_hash = Column(String, ForeignKey("patients.patient_hash"))
    practitioner_id = Column(Integer, ForeignKey("users.id"))
    procedure_type = Column(String, index=True)
    duration = Column(Integer)  # en minutes
    consent_hash = Column(String)
    metadata = Column(Text)  # JSON FHIR
    blockchain_tx_hash = Column(String)  # Hash de la transaction
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    patient = relationship("Patient", back_populates="procedures")
    practitioner = relationship("User", back_populates="procedures")

class Consent(Base):
    """Modèle consentement patient"""
    __tablename__ = "consents"

    id = Column(Integer, primary_key=True, index=True)
    procedure_id = Column(Integer, ForeignKey("procedures.id"))
    consent_hash = Column(String, unique=True, index=True)
    file_path = Column(String)  # Chemin vers le fichier signé
    signed_at = Column(DateTime)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class FHIRResource(Base):
    """Modèle ressource FHIR"""
    __tablename__ = "fhir_resources"

    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(String, index=True)  # Claim, Patient, Practitioner, etc.
    resource_id = Column(String, index=True)
    fhir_data = Column(Text)  # JSON FHIR complet
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Fonction pour obtenir la session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()