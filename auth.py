from datetime import datetime, timedelta, UTC
from jose import jwt, JWTError
import os
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends, status

SECRET_KEY = os.getenv('secret_key', 'testkey')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_TIMEDELTA = timedelta(minutes=300)  # 30 minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def gen_token(user_id: str, username: str, expires_delta: timedelta) -> str:
    expires = datetime.now(UTC) + expires_delta
    encode = {'sub': username, 'id': str(user_id), 'exp': expires}
    return jwt.encode(encode, key=SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(user_id: str, username: str) -> str:
    return gen_token(user_id, username, ACCESS_TOKEN_EXPIRE_TIMEDELTA)


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if not username or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {'username': username, 'user_id': user_id}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


user_dependency = Annotated[dict, Depends(get_current_user)]
