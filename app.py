from doctest import debug
from unittest import result
from fastapi import FastAPI, Depends, HTTPException, Form
import os
from dotenv import load_dotenv
from apps.schema import *
from apps.crud import *
import uvicorn
from fastapi.security import OAuth2PasswordBearer , OAuth2PasswordRequestForm



app = FastAPI(title="SuflamTech")

UPLOAD_FOLDER = "static/uploads/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Login Users
@app.post("/api/users/login", response_model=Token)
async def users_login(form_data: OAuth2PasswordRequestForm = Depends()):
    results = await check_auth({"cellnumber":form_data.username,"password":form_data.password})    
    return results


# Create USer
@app.post("/api/users")
async def create_user(name: str = Form(...),
    email: str = Form(...),
    cellnumber: str = Form(...),
    password: str = Form(...),
    profile_pic: Optional[UploadFile] = File(None),  # Profile picture (optional)
    current_user: dict = Depends(admin_access)):
    
    create_json = {"name":name,
                   "email":email,
                   "cellnumber":cellnumber,
                   "password":password,
                   "profile_pic":profile_pic,
                   "roleId":2
                   }
    
    new_user = await new_user_create(create_json)

    return new_user

# Get USers
@app.get("/api/users/{user_id}")
async def get_user(user_id: int,current_user: dict = Depends(get_user_from_token)):
    details = await get_userdetails(user_id, current_user)

    return details


# Update User
@app.patch("/api/users/{user_id}")
async def update_user(user_id: int,
                    name: Optional[str] = None,
                    email: Optional[str] = None,
                    password:  Optional[str] = None,
                    cellnumber: Optional[str] = None,
                    current_user: dict = Depends(admin_access)):
    
    update_json = {"name":name,
                   "email":email,
                   "cellnumber":cellnumber,
                   "password":password,
                   "roleId":2,
                   "user_id":user_id
                   }
    data = await update_user_details(update_json)
    return data


# get all user details
@app.get("/api/users")
async def user_list(current_user: dict = Depends(admin_access)):
    user_details = await get_all_user()

    return user_details


# Delete user
@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int, current_user: dict = Depends(admin_access)):
    user_detele = await api_user_delete(user_id)
    return user_detele


if __name__ == "__main__":
    uvicorn.run(app, port=7000)