from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..core.database import get_db_session
from ..core.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    create_credentials_exception
)
from ..models.auth import User
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter()
security = HTTPBearer()


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "annotator"  # Default role


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    payroll_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# Dependency to get current user from token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """Get current user from JWT token."""
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise create_credentials_exception()

    username: str = payload.get("sub")
    if username is None:
        raise create_credentials_exception()

    # Get user from database
    query = select(User).where(User.username == username, User.is_active == True)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise create_credentials_exception()

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Require admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db_session)
):
    """Register a new user."""
    # Check if username already exists
    query = select(User).where(User.username == user_data.username)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    query = select(User).where(User.email == user_data.email)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        role=user_data.role
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db_session)
):
    """Login user and return access token."""
    # Get user by username
    query = select(User).where(User.username == user_credentials.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_credentials.password, user.password_hash):
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

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    await db.commit()

    # Create access token
    access_token = create_access_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    _current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """List all users (admin only)."""
    query = select(User).order_by(User.created_at.desc())
    result = await db.execute(query)
    users = result.scalars().all()
    return users


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role: str,
    _current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update user role (admin only)."""
    if role not in ["admin", "annotator", "faculty"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 'admin', 'annotator', or 'faculty'"
        )

    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.role = role
    await db.commit()

    return {"message": f"User role updated to {role}"}


async def sync_users_from_payroll(db: AsyncSession) -> dict:
    """Internal function to sync users from AcademicResearchGroups payroll data."""
    from ..models.annotation_datasets import AcademicResearchGroups

    # Get unique payroll names from the dataset
    query = select(AcademicResearchGroups.payroll_name).distinct()
    result = await db.execute(query)
    payroll_names = [row[0] for row in result.fetchall() if row[0]]

    created_users = []
    for payroll_name in payroll_names:
        # Convert "Chevalier,Samuel" to username "chevalier_samuel"
        if ',' not in payroll_name:
            continue

        last_name, first_name = payroll_name.split(',', 1)

        # Clean up names: handle hyphens, periods, apostrophes, and spaces
        # For last names: replace hyphens with underscores to preserve compound names
        # For first names: take only the first part, remove special characters

        # Clean last name: replace hyphens/spaces with underscores, remove other special chars
        clean_last = last_name.strip().lower()
        clean_last = clean_last.replace('-', '_').replace(' ', '_')
        clean_last = ''.join(c for c in clean_last if c.isalpha() or c == '_')

        # Clean first name: take only first part, preserve hyphens in compound first names
        first_part = first_name.strip().split()[0]  # Take only first part before space
        clean_first = first_part.lower().replace('-', '_')
        clean_first = ''.join(c for c in clean_first if c.isalpha() or c == '_')

        username = f"{clean_last}_{clean_first}"
        email = f"{username}@uvm.edu"

        # Check if user already exists
        existing_query = select(User).where(User.username == username)
        existing_result = await db.execute(existing_query)
        existing_user = existing_result.scalar_one_or_none()

        if existing_user:
            # Update payroll_name if missing
            if not existing_user.payroll_name:
                existing_user.payroll_name = payroll_name
            continue

        # Create new user
        password_hash = get_password_hash("changeMe123!")  # Default password
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role="faculty",
            payroll_name=payroll_name,
            is_active=True
        )

        db.add(new_user)
        created_users.append({
            "username": username,
            "email": email,
            "payroll_name": payroll_name,
            "role": "faculty"
        })

    return {
        "message": f"Created {len(created_users)} faculty users",
        "users": created_users
    }


@router.post("/create-users-from-payroll")
async def create_users_from_payroll(
    _current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create users from AcademicResearchGroups payroll data (admin only)."""
    result = await sync_users_from_payroll(db)
    await db.commit()
    return result