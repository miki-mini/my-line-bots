import secrets
import os
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    """Basic Auth for Owl Web App"""
    # Get credentials from env
    correct_username = os.getenv("OWL_USER")
    correct_password = os.getenv("OWL_PASS")

    if not correct_username or not correct_password:
        print("❌ Error: OWL_USER or OWL_PASS not set in environment variables.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="System configuration error: Authentication not configured."
        )

    # Secure comparison
    is_correct_username = secrets.compare_digest(credentials.username, correct_username)
    is_correct_password = secrets.compare_digest(credentials.password, correct_password)

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
