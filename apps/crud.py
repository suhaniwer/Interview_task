from db_connection import *
from apps.auth import *
from jose import jwt
from datetime import timedelta , datetime

# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("Secret_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



def get_user_from_token(token: str = Depends(oauth2_scheme)):
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        cursor.execute("SELECT * FROM user WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    


def admin_access(user: dict = Depends(get_user_from_token)):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT roleId FROM user WHERE id = %s", (user['id'],))
    role_id = cursor.fetchone()
    
    if role_id is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if role_id["roleId"] != 1: 
        raise HTTPException(status_code=403, detail="Unautherized")
    return user


# Token save in DB
def save_access_token(user_id, token, ttl):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    sql = "INSERT INTO accesstoken (token, ttl, userId) VALUES (%s, %s, %s)"
    values = (token, ttl, user_id)
    cursor.execute(sql, values)
    db.commit()
    cursor.close()
    db.close()


# Check authentication
async def check_auth(auth_values):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user WHERE cellnumber = %s", (auth_values['cellnumber'],))
    user = cursor.fetchone()
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid Cellnumber")
    
    decryp_pass = await decrypted_password(user['password'])
    if auth_values['password'] != decryp_pass:
        raise HTTPException(status_code=400, detail="Incorrect Password")
    
    data={"sub": str(user['id'])}
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # save token in DB
    print(expire)
    save_access_token(user['id'], encoded_jwt, str(expire))

    return {"access_token": encoded_jwt, "token_type": "bearer"}


# Create USer
async def new_user_create(user_values):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Check Mobile Number 
    cursor.execute("SELECT * FROM user WHERE cellnumber = %s", (user_values['cellnumber'],))
    exist_cellnumber = cursor.fetchone()
    if exist_cellnumber:
        raise HTTPException(status_code=400, detail="Cellnumber already exists")
    
    # Check Email 
    cursor.execute("SELECT * FROM user WHERE email = %s", (user_values['email'],))
    existing_user_by_email = cursor.fetchone()
    if existing_user_by_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Image store
    profile_pic = None
    if user_values['profile_pic']:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        extension = user_values['profile_pic'].filename.split('.')[-1]  # Get file extension
        filename = f"{timestamp}.{extension}"
        
        # Save image to 'static/uploads/'
        file_path = os.path.join("static/uploads/", filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(user_values['profile_pic'].file.read())  # Use profile_pic.file.read()
        
        profile_pic = f"/static/uploads/{filename}"

    encryp_pass = await encrypted_password(user_values['password'])
        
    cursor.execute("""
        INSERT INTO user (name, email, cellnumber, password, profilepic, created, modified, roleId)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (user_values['name'], user_values['email'], user_values['cellnumber'], encryp_pass, profile_pic, datetime.utcnow(), datetime.utcnow(), user_values['roleId']))  

    db.commit()

    # Close the database connection
    cursor.close()
    db.close()

    return {"message": "User created successfully"}


# Get USer
async def get_userdetails(user_id,current_user):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if user_id != current_user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to access this data")

    # Check user
    cursor.execute("SELECT * FROM user WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
   
    role = ""
    if user['roleId'] == 2:
        role = "User"

    return {"data":{"id": user['id'],
                    "name": user['name'],
                    "cellnumber": user['cellnumber'],
                    "email": user['email'],
                    "created": user['created'],
                    "roleID": role,
                    "profile-pic": user['profilepic']
                    }}

# update user
async def update_user_details(updated_values):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    encryp_pass = encrypted_password(updated_values['password'])

    cursor.execute("UPDATE user SET name = %s, cellnumber = %s, password= %s, email = %s, roleId = %s WHERE id = %s",
                   (updated_values['name'], updated_values['cellnumber'], encryp_pass, updated_values['email'], updated_values['roleId'], updated_values['user_id']))
    db.commit()

    return {"message": "Details Update Successfully"}


# detele user
async def api_user_delete(user_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("UPDATE user SET deletedAt = %s WHERE id = %s", (datetime.utcnow(), user_id))
    db.commit()

    return {"message": "User Temp deleted successfully"}

# get all user
async def get_all_user():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user WHERE roleId != 1 AND deletedAt IS NULL")
    users = cursor.fetchall()

    data = []
    for x in users:
        data.append({"name":x['name'],
                     "cellnumber" : x['cellnumber'],
                     "roleId" : x['roleId'],
                     "email" : x['email'],
                     "created": x['created'],
                     "profile-pic": x['profilepic'],
                     "primary-key":x['id'],
                     })

    return {"data":data}