from fastapi import APIRouter
from models.model import User

router = APIRouter(
    prefix="/webauth",
    tags=["Auth"]
)

@router.post("/register/")
async def register_user(username: str):
    pass
    #user_id = str(uuid.uuid4())
    #user_document = {"_id": user_id, "username": username} 
    #result = collection.insert_one(user_document)
    #return {"message": "Data inserted successfully", "id": user_id, "name": username}


@router.post("/finish_reg/")
async def finish_reg():
    pass

@router.post("/authenticate/")
async def authenticate_user(name: str):
    pass

