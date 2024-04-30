from connection import collection as coll
from fastapi import HTTPException
import json
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

RP_ID_GL = "localhost"
RP_NAME_GL = "TestWebauthn"

async def register_user(username: str):
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
            user_verification = UserVerificationRequirement.PREFERRED
        ),
    )
    registration_options_json = options_to_json(registration_options)
    return registration_options_json

async def registration_check(registration_response):
    response_data = json.loads(registration_response)
    challenge = response_data.get("challenge")
    username = response_data["user"]["name"]
    verified_credential = verify_registration_response(
        registration_response,
        {"username": registration_response["username"].encode()},
    )
    inserting_user = coll.insert_one({"username": verified_credential.username, "credential_id": verified_credential.credential_id})
    return inserting_user