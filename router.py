from fastapi import APIRouter,HTTPException,logger
from models import UserCreate,UserUpdate,UserResponse
from config import conn
from bson import ObjectId
from serializer import userEntity,usersEntity
from typing import List
import logging

user = APIRouter()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log")
    ]
)

#Create
@user.post('/', response_model=List[UserResponse],status_code=201)
async def create_user(user: UserCreate):
    logger.info("Creating user with email: %s",user.email)
    conn.local.user.insert_one(dict(user))
    logger.debug("User inserted successfully.")
    return usersEntity(conn.local.user.find())

#Retrieve
@user.get('/',response_model = List[UserResponse]) # Why List? since displaying list of dict & name,email,id is enough so UserResponse model
async def get_all_user():
    logger.info("Fetching all users")
    users = usersEntity(conn.local.user.find())
    logger.debug("Fetched %d users",len(users))
    return users

@user.get('/{id}', response_model=UserResponse)
async def find_one_user(id):
    logger.info("Fetching user %s",id)
    try:
        the_one = conn.local.user.find_one({"_id":ObjectId(id)})
    except Exception as e:
        logger.error("Invalid id: %s",e)
        raise HTTPException(status_code=400, detail="Invalid ID format")

    if not the_one:
        logger.warning("User not found: %s",id)
        raise HTTPException(status_code=404, detail= f"No user with this {id}.")
    logger.debug("User found : %s",the_one["email"])
    return userEntity(the_one) 

#Update
@user.put('/{id}',response_model=UserResponse)
async def update_user(id : str, user : UserUpdate):
    logger.info("Updating user with id : %s", id)
    existing_user = conn.local.user.find_one({"_id":ObjectId(id)})
    if not existing_user:
        logger.warning("User not found for update %s",id)
        raise HTTPException(status_code=404, detail= f"No user with this {id}.")
    
    conn.local.user.find_one_and_update({"_id":ObjectId(id)},{"$set":dict(user)})
    updated_user = conn.local.user.find_one({"_id":ObjectId(id)})
    logger.debug("User updated successfully: %s",updated_user["email"])
    return userEntity(updated_user)

#Delete
@user.delete('/{id}',response_model=UserResponse)
async def delete_user(id : str):
    logger.info("Deleting user with id: %s",id)
    deleted_user = conn.local.user.find_one_and_delete({"_id":ObjectId(id)})
    if not deleted_user:
        logger.warning("User not found for deletion: %s",id)
        raise HTTPException(status_code=404, detail= f"No user with this {id}.")
    logger.debug("User deleted: %s",deleted_user["email"])
    return userEntity(deleted_user)