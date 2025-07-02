from fastapi import APIRouter
from models import UserCreate,UserUpdate,UserResponse
from config import conn
from bson import ObjectId
from serializer import userEntity,usersEntity
from typing import List
user = APIRouter()

@user.get('/',response_model = List[UserResponse]) # Why List? since displaying list of dict & name,email,id is enough so UserResponse model
async def get_all_user():
    return usersEntity(conn.local.user.find())

@user.get('/{id}', response_model=UserResponse)
async def find_one_user(id):
    return userEntity(conn.local.user.find_one({"_id":ObjectId(id) })) 

@user.post('/', response_model=List[UserResponse])
async def create_user(user: UserCreate):
    conn.local.user.insert_one(dict(user))
    return usersEntity(conn.local.user.find())

@user.put('/{id}',response_model=UserResponse)
async def update_user(id : str, user : UserUpdate):
    conn.local.user.find_one_and_update({"_id":ObjectId(id)},{"$set":dict(user)})
    return userEntity(conn.local.user.find_one({"_id":ObjectId(id) }))

@user.delete('/{id}',response_model=UserResponse)
async def delete_user(id : str,):
    return userEntity(conn.local.user.find_one_and_delete({"_id":ObjectId(id)}))
    
'''
    
'''