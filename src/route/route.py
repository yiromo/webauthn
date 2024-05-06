from fastapi import APIRouter, Request, HTTPException
from models.model import User
from schemas.schema import register_user, registration_check, hander_verify_authentication_response, handler_generate_authentication_options

router = APIRouter(
    prefix="/webauth",
    tags=["Auth"]
)

@router.get("/register_options/")
async def regis_user(username: str):
    options = await register_user(username)
    return options

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
async def authenticate_opts(name: str):
#handler_generate_authentication_options
    options = await handler_generate_authentication_options(name)
    return options

@router.post("/verify_authenticate/")
async def ver_authenticate(request: Request):
    try:
        data = await request.json()
        username = data.get('username')
        verification_result = await hander_verify_authentication_response(request, username)
        return {"verification_result": verification_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
