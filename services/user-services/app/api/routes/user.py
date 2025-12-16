from fastapi import APIRouter, Depends
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse, UserLogin, UserUpdate, Token
from db.database import get_db
from services.user_service import UserService
from utils.jwt_handler import create_token_pair
from utils.auth_dependencies import get_current_user, TokenData

router = APIRouter()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

@router.post("/register", response_model=UserResponse)
async def register_user(
    user: UserCreate, 
    service: UserService = Depends(get_user_service)
):
    return service.create_user(user)

@router.post("/login", response_model=Token)
async def login_user(
    user: UserLogin, 
    service: UserService = Depends(get_user_service)
):
    db_user = service.authenticate_user(user)
    return create_token_pair(
        user_id=db_user.id,
        email=db_user.email,
        role=db_user.role.value
    )

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    service: UserService = Depends(get_user_service)
):
    return service.get_users()

@router.get("/users/{user_id}", response_model=UserResponse) 
async def get_user_by_id(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    return service.get_user_by_id(user_id)

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user: UserUpdate,
    current_user: TokenData = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    return service.update_user(user_id, user)

@router.delete("/users/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: int,
    current_user: TokenData = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    return service.delete_user(user_id)

@router.get("/creators", response_model=List[UserResponse])
async def get_creators(
    niche: Optional[str] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    service: UserService = Depends(get_user_service)
):
    return service.get_creators(niche, min_price, max_price)