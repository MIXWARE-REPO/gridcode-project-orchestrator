"""
Authentication routes for the GriPro Dashboard API.
Handles project code login and JWT token management.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.models.schemas import LoginRequest, TokenPayload, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "gripro-dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Demo projects for development (replace with Supabase in production)
DEMO_PROJECTS = {
    "GRIP-001": {
        "id": "proj-001-uuid",
        "name": "E-Commerce Platform",
        "client_name": "Acme Corp",
        "client_email": "client@acme.com",
    },
    "GRIP-002": {
        "id": "proj-002-uuid",
        "name": "Mobile Banking App",
        "client_name": "FinTech Inc",
        "client_email": "client@fintech.com",
    },
    "DEMO-123": {
        "id": "demo-project-uuid",
        "name": "Demo Project",
        "client_name": "Demo User",
        "client_email": "demo@gripro.dev",
    },
}


def create_token(project_id: str, client_email: Optional[str], client_name: Optional[str]) -> str:
    """Create a JWT token for project access."""
    now = datetime.utcnow()
    payload = {
        "project_id": project_id,
        "client_email": client_email,
        "client_name": client_name,
        "exp": now + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": now,
        "iss": "gripro-dashboard",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> TokenPayload:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return TokenPayload(
            project_id=payload["project_id"],
            client_email=payload.get("client_email"),
            client_name=payload.get("client_name"),
            exp=datetime.fromtimestamp(payload["exp"]),
            iat=datetime.fromtimestamp(payload["iat"]),
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )


async def get_current_project(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenPayload:
    """Dependency to get current project from JWT token."""
    return decode_token(credentials.credentials)


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login with project code to get access token.

    Project codes are provided to clients when their project is created.
    Format: XXXX-NNN (e.g., GRIP-001, DEMO-123)
    """
    project_code = request.project_code.upper().strip()

    # Look up project by code
    project = DEMO_PROJECTS.get(project_code)

    if not project:
        # In production, query Supabase here
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid project code. Please check and try again.",
        )

    # Create token
    token = create_token(
        project_id=project["id"],
        client_email=project.get("client_email"),
        client_name=project.get("client_name"),
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=JWT_EXPIRATION_HOURS * 3600,
        project_id=project["id"],
        project_name=project["name"],
    )


@router.post("/validate")
async def validate_token(token_payload: TokenPayload = Depends(get_current_project)):
    """Validate a JWT token and return its payload."""
    return {
        "valid": True,
        "project_id": token_payload.project_id,
        "client_name": token_payload.client_name,
        "expires_at": token_payload.exp.isoformat(),
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_payload: TokenPayload = Depends(get_current_project)):
    """Refresh an existing token to extend its expiration."""
    # Look up project to get current info
    project = None
    for code, proj in DEMO_PROJECTS.items():
        if proj["id"] == token_payload.project_id:
            project = proj
            break

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Create new token
    new_token = create_token(
        project_id=project["id"],
        client_email=project.get("client_email"),
        client_name=project.get("client_name"),
    )

    return TokenResponse(
        access_token=new_token,
        token_type="bearer",
        expires_in=JWT_EXPIRATION_HOURS * 3600,
        project_id=project["id"],
        project_name=project["name"],
    )
