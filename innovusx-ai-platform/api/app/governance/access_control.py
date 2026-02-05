"""Access control and authorization system."""

import hashlib
import secrets
import time
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Optional

import structlog
from fastapi import HTTPException, Request, status

from app.config import settings

logger = structlog.get_logger()


class Permission(str, Enum):
    """Available permissions."""
    # Strategy operations
    STRATEGY_READ = "strategy:read"
    STRATEGY_GENERATE = "strategy:generate"

    # Telemetry operations
    TELEMETRY_READ = "telemetry:read"

    # Audit operations
    AUDIT_READ = "audit:read"
    AUDIT_EXPORT = "audit:export"

    # Admin operations
    CONFIG_READ = "config:read"
    CONFIG_WRITE = "config:write"
    MODEL_DEPLOY = "model:deploy"


class Role(str, Enum):
    """User roles with associated permissions."""
    ANONYMOUS = "anonymous"
    USER = "user"
    DEVELOPER = "developer"
    ADMIN = "admin"


# Role to permissions mapping
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ANONYMOUS: {
        Permission.STRATEGY_READ,
        Permission.STRATEGY_GENERATE,
    },
    Role.USER: {
        Permission.STRATEGY_READ,
        Permission.STRATEGY_GENERATE,
        Permission.TELEMETRY_READ,
    },
    Role.DEVELOPER: {
        Permission.STRATEGY_READ,
        Permission.STRATEGY_GENERATE,
        Permission.TELEMETRY_READ,
        Permission.AUDIT_READ,
        Permission.CONFIG_READ,
    },
    Role.ADMIN: {
        Permission.STRATEGY_READ,
        Permission.STRATEGY_GENERATE,
        Permission.TELEMETRY_READ,
        Permission.AUDIT_READ,
        Permission.AUDIT_EXPORT,
        Permission.CONFIG_READ,
        Permission.CONFIG_WRITE,
        Permission.MODEL_DEPLOY,
    },
}


@dataclass
class APIKey:
    """API key with associated metadata."""
    id: str
    name: str
    key_hash: str
    role: Role
    rate_limit: int  # requests per minute
    allowed_origins: list[str]
    created_at: float
    expires_at: Optional[float] = None
    is_active: bool = True


@dataclass
class AccessContext:
    """Context for access control decisions."""
    user_id: Optional[str]
    role: Role
    api_key_id: Optional[str]
    permissions: set[Permission]
    rate_limit: int
    origin: Optional[str]


class AccessController:
    """
    Access control and authorization system.

    Features:
    - Role-based access control (RBAC)
    - API key management
    - Origin validation
    - Permission checking
    """

    def __init__(self):
        # In production, store in database
        self._api_keys: dict[str, APIKey] = {}
        self._init_demo_keys()

        logger.info("Access controller initialized")

    def _init_demo_keys(self):
        """Initialize demo API keys."""
        demo_keys = [
            {
                "id": "key_demo_001",
                "name": "Demo Widget",
                "key": "demo_key_for_testing_only",
                "role": Role.ANONYMOUS,
                "rate_limit": 100,
                "allowed_origins": ["http://localhost:*", "https://innovus-x.com"]
            },
            {
                "id": "key_user_001",
                "name": "User API Key",
                "key": "user_key_for_testing",
                "role": Role.USER,
                "rate_limit": 500,
                "allowed_origins": ["*"]
            },
            {
                "id": "key_admin_001",
                "name": "Admin API Key",
                "key": "admin_key_for_testing",
                "role": Role.ADMIN,
                "rate_limit": 1000,
                "allowed_origins": ["*"]
            },
        ]

        for key_data in demo_keys:
            self._api_keys[key_data["id"]] = APIKey(
                id=key_data["id"],
                name=key_data["name"],
                key_hash=self._hash_key(key_data["key"]),
                role=key_data["role"],
                rate_limit=key_data["rate_limit"],
                allowed_origins=key_data["allowed_origins"],
                created_at=time.time()
            )

    def _hash_key(self, key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(key.encode()).hexdigest()

    async def authenticate(self, request: Request) -> AccessContext:
        """
        Authenticate a request and return access context.

        Args:
            request: FastAPI request

        Returns:
            AccessContext with permissions and metadata
        """
        # Check for API key in header
        api_key = request.headers.get("X-API-Key")
        origin = request.headers.get("Origin")

        if api_key:
            return await self._authenticate_api_key(api_key, origin)

        # Fall back to anonymous access
        return AccessContext(
            user_id=None,
            role=Role.ANONYMOUS,
            api_key_id=None,
            permissions=ROLE_PERMISSIONS[Role.ANONYMOUS],
            rate_limit=settings.rate_limit_requests_per_minute,
            origin=origin
        )

    async def _authenticate_api_key(
        self,
        api_key: str,
        origin: Optional[str]
    ) -> AccessContext:
        """Authenticate using API key."""
        key_hash = self._hash_key(api_key)

        # Find matching key
        matching_key = None
        for key_id, stored_key in self._api_keys.items():
            if stored_key.key_hash == key_hash:
                matching_key = stored_key
                break

        if not matching_key:
            logger.warning(
                "Invalid API key",
                key_prefix=api_key[:8] if len(api_key) >= 8 else "short"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )

        # Check if key is active
        if not matching_key.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key is disabled"
            )

        # Check expiration
        if matching_key.expires_at and time.time() > matching_key.expires_at:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has expired"
            )

        # Check origin
        if origin and not self._check_origin(origin, matching_key.allowed_origins):
            logger.warning(
                "Origin not allowed",
                origin=origin,
                api_key_id=matching_key.id
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Origin not allowed for this API key"
            )

        return AccessContext(
            user_id=None,
            role=matching_key.role,
            api_key_id=matching_key.id,
            permissions=ROLE_PERMISSIONS[matching_key.role],
            rate_limit=matching_key.rate_limit,
            origin=origin
        )

    def _check_origin(self, origin: str, allowed_origins: list[str]) -> bool:
        """Check if origin is allowed."""
        for allowed in allowed_origins:
            if allowed == "*":
                return True
            if allowed.endswith("*"):
                # Wildcard matching
                prefix = allowed[:-1]
                if origin.startswith(prefix):
                    return True
            elif origin == allowed:
                return True
        return False

    def check_permission(
        self,
        context: AccessContext,
        permission: Permission
    ) -> bool:
        """Check if context has a specific permission."""
        return permission in context.permissions

    def require_permission(
        self,
        context: AccessContext,
        permission: Permission
    ) -> None:
        """Require a permission, raise exception if not present."""
        if not self.check_permission(context, permission):
            logger.warning(
                "Permission denied",
                role=context.role.value,
                permission=permission.value,
                api_key_id=context.api_key_id
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value}"
            )

    async def create_api_key(
        self,
        name: str,
        role: Role,
        rate_limit: int = 100,
        allowed_origins: Optional[list[str]] = None,
        expires_in_days: Optional[int] = None
    ) -> tuple[str, APIKey]:
        """
        Create a new API key.

        Returns:
            Tuple of (raw_key, APIKey metadata)
        """
        # Generate secure random key
        raw_key = secrets.token_urlsafe(32)
        key_id = f"key_{secrets.token_hex(8)}"

        expires_at = None
        if expires_in_days:
            expires_at = time.time() + (expires_in_days * 86400)

        api_key = APIKey(
            id=key_id,
            name=name,
            key_hash=self._hash_key(raw_key),
            role=role,
            rate_limit=rate_limit,
            allowed_origins=allowed_origins or ["*"],
            created_at=time.time(),
            expires_at=expires_at
        )

        self._api_keys[key_id] = api_key

        logger.info(
            "API key created",
            key_id=key_id,
            name=name,
            role=role.value
        )

        return raw_key, api_key

    async def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key."""
        if key_id in self._api_keys:
            self._api_keys[key_id].is_active = False
            logger.info("API key revoked", key_id=key_id)
            return True
        return False

    async def list_api_keys(self) -> list[APIKey]:
        """List all API keys (without hashes)."""
        return list(self._api_keys.values())


@lru_cache
def get_access_controller() -> AccessController:
    """Get access controller instance."""
    return AccessController()
