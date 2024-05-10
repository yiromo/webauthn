from fastapi import HTTPException, Request
from typing import Dict
from models.model import User, Credential
from connection import collection as coll
from webauthn import (
    options_to_json,
    generate_authentication_options,
    verify_authentication_response,
)
from webauthn.helpers.structs import (
    UserVerificationRequirement,
    AuthenticationCredential,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier

RP_ID_GL = "localhost"
RP_NAME_GL = "TestWebauthn"
current_registration_challenge = None
current_authentication_challenge = None

async def handler_generate_authentication_options(username: str):
    global current_authentication_challenge
    user = coll.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    options = generate_authentication_options(
        rp_id=RP_ID_GL,
        allow_credentials=[
            {"type": "public-key", "id": cred.id, "transports": cred.transports}
            for cred in user.credentials
        ],
        user_verification=UserVerificationRequirement.REQUIRED,
    )

    current_authentication_challenge = options.challenge

    return options_to_json(options)


async def verify_authentication_response(request: Request):
    try:
        body = await request.json()
        credential = AuthenticationCredential.parse_raw(body)

        username = body.get("username")

        user = coll.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

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
        user_credential["sign_count"] = verification.new_sign_count
        return {"verified": True}
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


async def post_authentication(request: Request):
    pass

