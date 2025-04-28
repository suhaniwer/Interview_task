
from pydantic import BaseModel , validator
from typing import Optional
from fastapi import File, UploadFile

class Token(BaseModel):
    access_token: str
    token_type: str
    

class UserCreate(BaseModel):
    name: str
    cellnumber: str
    email: str
    password:str
    profilepic: str

    @validator("name","email","cellnumber", "password",)
    def validate_not_empty(cls, value, field):
        if isinstance(value, str) and not value.strip():
            raise ValueError(f"{field.name} cannot be empty or just whitespace.")
        return value
