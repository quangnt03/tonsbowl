import os
import jwt
from datetime import date, timedelta
from fastapi.exceptions import HTTPException

SECRET_KEY = os.environ['JWT_SECRET']
ALGORITHM = 'HS256'

def create_access_token(teleid = str) -> str:
    payload = teleid
    encoded_jwt = jwt.encode(
        payload,
        key=SECRET_KEY
    )
    
    return encoded_jwt

def jwt_decode(token: str) -> dict:
    try:
        data = jwt.decode(token, key=SECRET_KEY)
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid authentication credential")
    return data