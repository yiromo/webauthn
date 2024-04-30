from fastapi import APIRouter, Request
from models.model import User
from schemas.schema import register_user, registration_check

router = APIRouter(
    prefix="/webauth",
    tags=["Auth"]
)

@router.post("/register/")
async def regis_user(username: str):
    return await register_user(username)


@router.post("/finish_reg/")
async def finish_reg(response):
    return await registration_check(response)

@router.post("/authenticate/")
async def authenticate_user(name: str):
    pass

