from connection import collection as coll
from fastapi import HTTPException
from webauthn.webauthn import generate_challenge
from webauthn import PublicKeyCredentialRpEntity, PublicKeyCredentialUserEntity

async def register_user(username: str):
    user_exist = coll.find_one({username})
    if user_exist:
        raise HTTPException(status_code=400, detail="ALready Exists")
    
    chal = generate_challenge(32)

    
