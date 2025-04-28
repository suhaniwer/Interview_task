from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from fastapi import FastAPI, Depends, HTTPException, Form
from jose import jwt, JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

SECRET_KEY = os.getenv("Secret_KEY")


# Load .env
load_dotenv()

FERNET_KEY = Fernet(os.getenv("FERNET_KEY"))

# Encrypt the password
async def encrypted_password(password):
    encrypt_pass = FERNET_KEY.encrypt(password.encode()).decode('utf-8')
    return encrypt_pass


async def decrypted_password(encrypted_pass):
    decrypted_pass = FERNET_KEY.decrypt(encrypted_pass.encode('utf-8')).decode('utf-8')
    return decrypted_pass


