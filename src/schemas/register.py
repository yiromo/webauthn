from fastapi import HTTPException, Request
from typing import Dict
from models.model import User, Credential
from connection import collection as coll
from webauthn import (
    generate_registration_options,
    options_to_json,
    verify_registration_response,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    RegistrationCredential,
)
import base64
from webauthn.helpers.cose import COSEAlgorithmIdentifier

RP_ID_GL = "localhost"
RP_NAME_GL = "TestWebauthn"
current_registration_challenge = None
current_authentication_challenge = None

import base64

async def register_user(username: str):
    global current_registration_challenge
    user = coll.find_one({"username": username})
    if user:
        raise HTTPException(status_code=400, detail="exists")

    user_passkeys = coll.find({"user.username": username})

    encoded_username = base64.urlsafe_b64encode(username.encode())

    registration_options = generate_registration_options(
        rp_id=RP_ID_GL,
        rp_name=RP_NAME_GL,
        user_id=encoded_username, 
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
    registration_options_json = options_to_json(registration_options)

    coll.insert_one(
        {"username": username, "registration_options": registration_options_json}
    )

    return registration_options_json


async def registration_check(request: Request):
    try:
        body = await request.json()
        credential = RegistrationCredential.parse_raw(body)

        username = body.get("username")

        verified_credential = verify_registration_response(
            credential=credential,
            expected_challenge=current_registration_challenge,
            expected_rp_id=RP_ID_GL,
            expected_origin="http://localhost:9000",
        )

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
            {"$push": {"credentials": new_credential.dict()}},
        )

        return inserting_user
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))