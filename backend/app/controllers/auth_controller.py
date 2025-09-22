"""Authentication controller for user management"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.auth.security import get_password_hash, verify_password, create_access_token
from datetime import timedelta
from app.config.settings import settings

class AuthController:
    @staticmethod
    def create_user(db: Session, email: str, username: str, password: str, full_name: str = None) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(password)
        db_user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=True,
            is_verified=False
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User:
        """Authenticate user with username/email and password"""
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        return user
    
    @staticmethod
    def create_access_token_for_user(user: User) -> dict:
        """Create access token for authenticated user"""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name
            }
        }
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """Get user by ID"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    @staticmethod
    def update_user(db: Session, user_id: int, **kwargs) -> User:
        """Update user information"""
        user = AuthController.get_user_by_id(db, user_id)
        
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                if key == "password":
                    user.hashed_password = get_password_hash(value)
                else:
                    setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        return user
