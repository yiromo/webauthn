from fastapi import APIRouter, Request, HTTPException, Response
import json
from models.model import User
from schemas.register import register_user, registration_check
from schemas.auth import hander_verify_authentication_response, handler_generate_authentication_options, check_user_in_db

router = APIRouter(
    prefix="/webauth",
    tags=["Auth"]
)

@router.get("/register_options/")
async def regis_user(username: str):
    return await register_user(username)

@router.post("/verify_registration/")
async def finish_reg(request: Request):
    try:
        data = await request.json()
        username = data.get('username') 
        verification_result = await registration_check(request, username)  
        return {"verification_result": verification_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/authenticate_options/")
async def authenticate_opts(username: str):
    return await handler_generate_authentication_options(username)

@router.post("/verify_authenticate/")
async def ver_authenticate(request: Request):
    try:
        verification_result = await hander_verify_authentication_response(request)
        return {"verification_result": verification_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/check_db/")
async def check_username(username: str):
    try:
        user = await check_user_in_db(username)
        # Convert the user object to JSON
        user_json = json.dumps(user)
        return Response(content=user_json, media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))