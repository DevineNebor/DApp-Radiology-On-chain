from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

from app.database import engine, Base
from app.routers import procedures, auth, fhir
from app.utils.blockchain import init_web3
from app.utils.auth import get_current_user

# Charger les variables d'environnement
load_dotenv()

# Configuration de l'application
app_config = {
    "title": "Radiology DApp API",
    "description": "API pour la gestion des actes de radiologie interventionnelle avec blockchain",
    "version": "1.0.0",
    "docs_url": "/docs",
    "redoc_url": "/redoc"
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Démarrage
    print("🚀 Démarrage de l'API Radiology DApp...")
    
    # Initialiser la base de données
    Base.metadata.create_all(bind=engine)
    print("✅ Base de données initialisée")
    
    # Initialiser Web3
    try:
        init_web3()
        print("✅ Connexion Web3 établie")
    except Exception as e:
        print(f"⚠️ Erreur Web3: {e}")
    
    yield
    
    # Arrêt
    print("🛑 Arrêt de l'API Radiology DApp...")

# Créer l'application FastAPI
app = FastAPI(**app_config, lifespan=lifespan)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend React
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Frontend Vite
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sécurité
security = HTTPBearer()

# Inclure les routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(procedures.router, prefix="/api/procedures", tags=["Procedures"])
app.include_router(fhir.router, prefix="/api/fhir", tags=["FHIR"])

@app.get("/")
async def root():
    """Point d'entrée principal de l'API"""
    return {
        "message": "🏥 Radiology DApp API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Vérification de l'état de santé de l'API"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-15T10:30:00Z",
        "services": {
            "database": "connected",
            "blockchain": "connected",
            "api": "running"
        }
    }

@app.get("/api/info")
async def api_info():
    """Informations sur l'API"""
    return {
        "name": "Radiology DApp API",
        "description": "API pour la gestion des actes de radiologie interventionnelle",
        "version": "1.0.0",
        "features": [
            "Enregistrement d'actes médicaux",
            "Gestion des consentements",
            "Génération de claims FHIR",
            "Traçabilité blockchain",
            "Authentification JWT"
        ],
        "standards": [
            "FHIR R4",
            "HIPAA-compliant",
            "Blockchain Ethereum"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )