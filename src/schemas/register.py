from fastapi import HTTPException, Request
from typing import Dict, Any
import uuid
import json
from connection import collection as coll
from webauthn import (
    generate_registration_options,
    options_to_json,
    verify_registration_response,
)
from webauthn.helpers.parse_registration_credential_json import parse_registration_credential_json
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
)
import base64
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from utils.utils import to_buffer, to_base64url

RP_ID_GL = "localhost"
RP_NAME_GL = "TestWebauthn"
current_registration_challenge = None
current_authentication_challenge = None



async def register_user(username: str):
    global current_registration_challenge
    user = coll.find_one({"username": username})
    if user:
        raise HTTPException(status_code=400, detail="exists")

    user_passkeys = coll.find({"user.username": username})

    user_id_str = str(uuid.uuid4())
    user_id_bytes = user_id_str.encode('utf-8')
    encoded_user_id = base64.urlsafe_b64encode(user_id_bytes)

    registration_options = generate_registration_options(
        rp_id=RP_ID_GL,
        rp_name=RP_NAME_GL,
        user_id=encoded_user_id, 
        user_name=username,
        exclude_credentials=[
            {"id": cred.id, "transports": cred.transports, "type": "public-key"}
            for cred in user_passkeys
        ],
        authenticator_selection=AuthenticatorSelectionCriteria(
            user_verification=UserVerificationRequirement.REQUIRED
        ),
        supported_pub_key_algs=[
            COSEAlgorithmIdentifier.ECDSA_SHA_256,
            COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
        ],
    )

    print("Generated registration options:", registration_options)

    current_registration_challenge = registration_options.challenge
    print(current_registration_challenge)
    registration_options_str = options_to_json(registration_options)
    registration_options_json = json.loads(registration_options_str)
    inserted = coll.insert_one({"username": username, "registration_options": registration_options_json})
    print(inserted)
    
    return registration_options_json


async def registration_check(request: Request, *args, **kwargs):
    try:
        print("Received arguments:", args)
        print("Received keyword arguments:", kwargs)
        
        body = await request.json()
        
        credential = parse_registration_credential_json(body)

        username = body.get("username")

        if not username:
            raise HTTPException(status_code=400, detail="Username missing in the request body")

        user = coll.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        verified_credential = verify_registration_response(
            credential=credential,
            expected_challenge=current_registration_challenge,
            expected_rp_id=RP_ID_GL,
            expected_origin="http://localhost:9000",
        )

        new_credential_dict = {
            "id": verified_credential.credential_id,
            "public_key": verified_credential.credential_public_key,
            "sign_count": verified_credential.sign_count,
            "transports": body.get("transports", []),
        }

        inserting_user = coll.update_one(
            {"username": username},
            {"$push": {"credentials": new_credential_dict}},
        )

        if inserting_user.modified_count == 1:
            return True
        else:
            return False

    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


    
async def post_register():
    pass