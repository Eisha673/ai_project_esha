from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from ..config import settings

ALGORITHM = "HS256"


def create_access_token(subject: str, expires_minutes: int = 60) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    return jwt.encode({"sub": subject, "exp": expires_at}, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
