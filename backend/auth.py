"""
Authentication and authorization module for the AI Workflow Automation Platform.
"""
import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.config import settings

# Security scheme
security = HTTPBearer()

# In a production environment, these would come from a secure secrets manager or environment variables
# For now, we'll use environment variables with fallback to defaults for development
API_KEYS = {
    os.getenv("API_KEY_ADMIN", "admin-secret-key-change-in-production"): "admin",
    os.getenv("API_KEY_OPERATOR", "operator-secret-key-change-in-production"): "operator",
    os.getenv("API_KEY_VIEWER", "viewer-secret-key-change-in-production"): "viewer",
}

# Role permissions mapping
ROLE_PERMISSIONS = {
    "admin": ["read", "write", "delete", "approve", "configure"],
    "operator": ["read", "write", "approve"],
    "viewer": ["read"],
}

def get_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract and validate the API key from the Authorization header.
    """
    token = credentials.credentials
    if token in API_KEYS:
        return token
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(api_key: str = Depends(get_api_key)) -> dict:
    """
    Get the current user based on the API key.
    Returns a dictionary with user information including role.
    """
    return {
        "api_key": api_key,
        "role": API_KEYS[api_key],
        "permissions": ROLE_PERMISSIONS[API_KEYS[api_key]]
    }

def require_permission(permission: str):
    """
    Dependency factory to require a specific permission.
    """
    def permission_checker(user: dict = Depends(get_current_user)):
        if permission not in user["permissions"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission}",
            )
        return user
    return permission_checker

# Convenience dependencies for common permissions
require_read = require_permission("read")
require_write = require_permission("write")
require_delete = require_permission("delete")
require_approve = require_permission("approve")
require_configure = require_permission("configure")