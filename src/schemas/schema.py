from connection import collection as coll
from fastapi import HTTPException, Request
from typing import Dict
import json
from models.model import User, Credential
import urllib.parse
from webauthn import (
    generate_registration_options,
    options_to_json,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,   
)
from webauthn.helpers.structs import (
    AttestationConveyancePreference,
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    RegistrationCredential,
    AuthenticationCredential,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier

RP_ID_GL = "localhost"
RP_NAME_GL = "TestWebauthn"
current_registration_challenge = None
current_authentication_challenge = None

# user_id = "random"
# in_memory_db: Dict[str, User] = {}

# in_memory_db[user_id] = User(
#     id=user_id,
#     username=username,
#     credentials=[],
# )
# logged_in_user_id = user_id

async def register_user(username: str):
    global current_registration_challenge
    user_exist = coll.find_one({"username": username})
    if user_exist:
        raise HTTPException(status_code=400, detail="ALready Exists")
    
    #'rp_id', 'rp_name', and 'user_name'
    registration_options = generate_registration_options(
        user_id=username.encode(),
        rp_id = RP_ID_GL,
        rp_name = RP_NAME_GL,
        user_name = username,
        attestation=AttestationConveyancePreference.NONE,
        authenticator_selection = AuthenticatorSelectionCriteria(
            user_verification = UserVerificationRequirement.REQUIRED,
        ),
        supported_pub_key_algs=[
            COSEAlgorithmIdentifier.ECDSA_SHA_256,
            COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
        ],
    )
    
    registration_options_json = options_to_json(registration_options)  # Assigning a value here
    current_registration_challenge = registration_options.challenge
    
    coll.insert_one({"username": username, "registration_options": registration_options_json})  # Now you can use it
    
    return options_to_json(registration_options)


async def registration_check(request: Request, username: str):
    global current_registration_challenge
    body = await request.get_data()

    try:
        credential = RegistrationCredential.parse_raw(body)
        
        verified_credential = verify_registration_response(
                credential=credential,
                expected_challenge=current_registration_challenge,
                expected_rp_id=RP_ID_GL,
                expected_origin="http://localhost:9000",
        )
    except Exception as err:
        return {"verified": False, "msg": str(err), "status": 404}
    
    user = coll.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_credential = Credential(
        id=verified_credential.credential_id,
        public_key=verified_credential.credential_public_key,
        sign_count=verified_credential.sign_count,
        transports=credential.transports,
    )
    inserting_user = coll.update_one(
        {"username": username},
        {"$push": {"credentials": new_credential.dict()}}
    )

    return inserting_user

async def handler_generate_authentication_options(username: str):
    user = coll.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404)

    options = generate_authentication_options(
        rp_id=RP_ID_GL,
        allow_credentials=[
            {"type": "public-key", "id": cred.id, "transports": cred.transports}
            for cred in user.credentials
        ],
        user_verification=UserVerificationRequirement.REQUIRED,
    )
    return options_to_json(options)


async def hander_verify_authentication_response(request: Request, username: str):
    body = await request.body()
    try:
        credential = AuthenticationCredential.parse_raw(body)

        user = coll.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=404)
        user_credential = next(
            (
                cred
                for cred in user["credentials"]
                if cred["id"] == credential.raw_id
            ),
            None,
        )
        if not user_credential:
            raise Exception("Could not find corresponding public key in DB")
        
        verification = verify_authentication_response(
            credential=credential,
            expected_challenge=current_authentication_challenge,
            expected_rp_id=RP_ID_GL,
            expected_origin="http://localhost:9000", 
            credential_public_key=user_credential["public_key"],
            credential_current_sign_count=user_credential["sign_count"],
            require_user_verification=True,
        )
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))
    user_credential["sign_count"] = verification.new_sign_count
    return {"verified": True}