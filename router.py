from fastapi import APIRouter
from models import User
from config import conn
from bson import ObjectId
from serializer import userEntity,usersEntity

user = APIRouter()

@user.get('/')
async def get_all_user():
    return usersEntity(conn.local.user.find())

@user.get('/{id}')
async def find_one_user(id):
    return usersEntity(conn.local.user.find_one({"_id":ObjectId(id) }))

@user.post('/')
async def create_user(user: User):
    conn.local.user.insert_one(dict(user))
    return usersEntity(conn.local.user.find())

@user.put('/{id}')
async def update_user(id,user : User):
    conn.local.user.find_one_and_update({"_id":ObjectId(id)},{"$set":dict(user)})
    return usersEntity(conn.local.user.find_one({"_id":ObjectId(id) }))

@user.delete('/{id}')
async def delete_user(id,user : User):
    return userEntity(conn.local.user.find_one_and_delete({"_id":ObjectId(id)}))
    
