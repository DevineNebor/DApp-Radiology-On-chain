from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.schemas.auth import User, UserCreate, Token, UserLogin
from app.utils.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_current_admin,
    create_user,
    get_user_by_username,
    get_user_by_email,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()

@router.post("/register", response_model=User)
async def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """Enregistre un nouvel utilisateur"""
    # Vérifier si l'utilisateur existe déjà
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Nom d'utilisateur déjà utilisé"
        )
    
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email déjà utilisé"
        )
    
    # Créer l'utilisateur
    return create_user(
        db=db,
        username=user.username,
        email=user.email,
        password=user.password,
        role=user.role,
        wallet_address=user.wallet_address
    )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authentifie un utilisateur et retourne un token JWT"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/login-json", response_model=Token)
async def login_json(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Authentifie un utilisateur avec JSON et retourne un token JWT"""
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Récupère les informations de l'utilisateur connecté"""
    return current_user

@router.get("/users", response_model=list[User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Récupère la liste des utilisateurs (admin seulement)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Récupère un utilisateur par son ID (admin seulement)"""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

@router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Met à jour un utilisateur (admin seulement)"""
    from app.utils.auth import update_user as update_user_func
    
    user = update_user_func(db, user_id, **user_update)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Supprime un utilisateur (admin seulement)"""
    from app.utils.auth import delete_user as delete_user_func
    
    success = delete_user_func(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return {"message": "Utilisateur supprimé avec succès"}