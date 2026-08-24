from jose import JWTError, jwt
from datetime import datetime, timedelta
from flask import request, g, abort, jsonify
from functools import wraps
from . import schemas

SECRET_KEY = '1034f60f88f93c07fef0cd60d091ef0bea346a6830113e65c5a34193c41d9d21'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data : dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp' : expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)

    return encoded_jwt

def verify_access_token(token : str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        idp : str = payload.get('user_id')

        if idp is None:
            abort(401, description="Couldn't validate credentials")
        
        token_data = schemas.TokenData(id = str(idp))

    except Exception as e:
        print("JWT Decode Error details", e)
        abort(401, description="Couldn't validate credentials")

    return token_data

def require_user(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            abort(401, description="Couldn't validate credentials")
        
        token = auth_header.split(' ')[1]
        token_data = verify_access_token(token)
        g.user_id = int(token_data.id)
        
        return f(*args, **kwargs)
    return decorated