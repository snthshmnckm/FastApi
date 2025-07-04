from fastapi import APIRouter,HTTPException,status
from models import UserCreate,UserUpdate,UserResponse
from config import conn
from bson import ObjectId
from serializer import userEntity,usersEntity
from typing import List
import logging

user = APIRouter()
user_collection = conn.local.user
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler("app.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)

#Create
@user.post('/', response_model=List[UserResponse],status_code=201)
async def create_user(user: UserCreate): #UserCreate is the reference of our model and we are saving to the "user" variable; i.e user: UserCreate
    
    logger.info(f"Creating user with email:{user.email}")
    user_collection.insert_one(dict(user))
    logger.debug("User inserted successfully.")
    return usersEntity(user_collection.find())

#Retrieve
@user.get('/',response_model = List[UserResponse]) # Why List? since displaying list of dict & name,email,id is enough so UserResponse model
async def get_all_user():
    logger.info("Fetching all users")
    users = usersEntity(user_collection.find())
    logger.debug(f"Fetched {len(users)} users.")
    return users

@user.get('/{id}', response_model=UserResponse)
async def find_one_user(id):
    logger.info(f"Fetching user {id}")
    try:
        the_one = user_collection.find_one({"_id":ObjectId(id)})
    except Exception as e:
        logger.error(f"Invalid id: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")

    if not the_one:
        logger.warning("User not found: %s",id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No user with this {id}.")
    logger.debug("User found : %s",the_one["email"])
    return userEntity(the_one) 

#Update
@user.put('/{id}',response_model=UserResponse)
async def update_user(id : str, user : UserUpdate):
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
async def delete_user(id : str):
    logger.info("Deleting user with id: %s",id)
    deleted_user = user_collection.find_one_and_delete({"_id":ObjectId(id)})
    if not deleted_user:
        logger.warning("User not found for deletion: %s",id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No user with this {id}.")
    logger.debug("User deleted: %s",deleted_user["email"])
    return userEntity(deleted_user)