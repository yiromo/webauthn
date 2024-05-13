from fastapi import HTTPException, Request
from typing import Dict
from connection import collection as coll
import json
from webauthn import (
    generate_authentication_options,
    verify_authentication_response,
)
from webauthn.helpers import options_to_json
from webauthn.helpers.structs import (
    UserVerificationRequirement,
)
from webauthn.helpers.parse_authentication_credential_json import parse_authentication_credential_json
from webauthn.helpers.cose import COSEAlgorithmIdentifier

RP_ID_GL = "localhost"
RP_NAME_GL = "TestWebauthn"
current_registration_challenge = None
current_authentication_challenge = None

async def check_user_in_db(username: str):
    user = coll.find_one({"username": username})
    if user:
        user['_id'] = str(user.get('_id'))
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")


async def handler_generate_authentication_options(username: str):
    global current_authentication_challenge
    user = coll.find_one({"username": username})
    user_passkeys = coll.find({"user.username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    options = generate_authentication_options(
        rp_id=RP_ID_GL,
        allow_credentials=[
            {"type": "public-key", "id": cred.id, "transports": cred.transports}
            for cred in user_passkeys
        ],
        user_verification=UserVerificationRequirement.REQUIRED,
    )

    current_authentication_challenge = options.challenge
    options_json_str = options_to_json(options)
    options_json=json.loads(options_json_str)
    return options_json



async def hander_verify_authentication_response(request: Request, *args, **kwargs):
    global current_authentication_challenge
    try:
        print("Received arguments:", args)
        print("Received keyword arguments:", kwargs)
        body = await request.json()
        print("Request Body:", body)
        credential = parse_authentication_credential_json(body)

        username = body.get("username")
        print("Username:", username)

        user = coll.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_credential = user.get("credentials", [])[0]
        if not user_credential:
            raise Exception("Could not find corresponding public key in DB")
        credential_public_key = user_credential.get("public_key")
        
        verification = verify_authentication_response(
            credential=credential,
            expected_challenge=current_authentication_challenge,
            expected_rp_id=RP_ID_GL,
            expected_origin="http://localhost:9000",
            credential_public_key=credential_public_key,
            credential_current_sign_count=user_credential.get("sign_count", 0),
            require_user_verification=True,
        )
        user_credential["sign_count"] = verification.new_sign_count
        return True
    except Exception as err:
        raise HTTPException(status_code=404, detail=str(err))


async def post_authentication(request: Request):
    pass

