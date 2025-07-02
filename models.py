from pydantic import BaseModel
from bson import ObjectId
class User(BaseModel):
    name : str
    email : str
    password : str
class R_model(BaseModel):
    id : str
    name : str
    email : str
    password : str