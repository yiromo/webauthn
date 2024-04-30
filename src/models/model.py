from pydantic import BaseModel

class User(BaseModel):
    username: str
    display_name: str
    key: str
    