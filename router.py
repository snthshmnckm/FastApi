from fastapi import APIRouter,HTTPException,status,Depends
from models import UserCreate,UserUpdate,UserResponse,UserLogin
from config import conn
from bson import ObjectId
from serializer import userEntity,usersEntity
from typing import List
import logging
from logging.handlers import RotatingFileHandler
from fastapi.security import OAuth2PasswordBearer
from security import create_access_token,decode_access_token
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    "app.log", maxBytes= 1_048_576, backupCount=5
    )
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)

user = APIRouter()


user_collection = conn.local.user
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") 

def verify_token(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_email = payload.get("sub")
    if user_email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: no subject found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = user_collection.find_one({"email": user_email})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_email


#Login
@user.post("/token")
async def login(login_data : UserLogin):
    user = user_collection.find_one({"email" : login_data.email})

    if not user or user.get("password") != login_data.password:
        raise HTTPException(status_code=400,detail= "Invalid email or password")

    access_token = create_access_token({"sub" : login_data.email})
    return {"access_token" : access_token , "token_type" : "bearer"}



#Create
@user.post('/', response_model=UserResponse,status_code=201)
async def create_user(new_user: UserCreate, token : str= Depends(verify_token)): #UserCreate is the reference of our model and we are saving to the "user" variable; i.e user: UserCreate
    
    logger.info(f"Creating user with email:{new_user.email}")
    user_collection.insert_one(dict(new_user))
    logger.debug("User inserted successfully.")
    created_user = user_collection.find_one({"email" : new_user.email})
    return usersEntity(created_user)

#Retrieve all
@user.get('/',response_model = List[UserResponse]) # Why List? since displaying list of dict & name,email,id is enough so UserResponse model
async def get_all_user(token: str = Depends(verify_token)):
    logger.info("Fetching all users")
    users = usersEntity(user_collection.find())
    logger.debug(f"Fetched {len(users)} users.")
    return users

#Retrieve one
@user.get('/{id}', response_model=UserResponse)
async def find_one_user(id,token: str = Depends(verify_token)):
    logger.info(f"Fetching user {id}")
    try:
        the_one = user_collection.find_one({"_id":ObjectId(id)})
    except Exception as e:
        logger.error(f"Invalid id: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")

    if not the_one:
        logger.warning("User not found: %s",id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No user with this {id}.")
    logger.debug(f"User found : {the_one['email']}")
    return userEntity(the_one) 

#Update
@user.put('/{id}',response_model=UserResponse)
async def update_user(id : str, user : UserUpdate,token: str = Depends(verify_token)):
    logger.info("Updating user with id : %s", id)
    existing_user = user_collection.find_one({"_id":ObjectId(id)})
    if not existing_user:
        logger.warning("User not found for update %s",id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No user with this {id}.")
    
    user_collection.find_one_and_update({"_id":ObjectId(id)},{"$set":dict(user)})
    updated_user = user_collection.find_one({"_id":ObjectId(id)})
    logger.debug("User updated successfully: %s",updated_user["email"])
    return userEntity(updated_user)

#Delete
@user.delete('/{id}',response_model=UserResponse)
async def delete_user(id : str,token: str = Depends(verify_token)):
    logger.info("Deleting user with id: %s",id)
    deleted_user = user_collection.find_one_and_delete({"_id":ObjectId(id)})
    if not deleted_user:
        logger.warning("User not found for deletion: %s",id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No user with this {id}.")
    logger.debug("User deleted: %s",deleted_user["email"])
    return userEntity(deleted_user)