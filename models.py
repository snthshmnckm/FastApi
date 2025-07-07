from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    name : str
    email : str

class UserCreate(User):
    password: str

class UserUpdate(User):
    password: Optional[str] = None

class UserResponse(User):
    id: str 

class UserLogin(BaseModel):
    email: str
    password : str

'''
    1.In order to add response model, added UserCreate,
UserUpdate,UserResponse classes.
    2.in UserResponse _id is changed to id since in pydantic _id
is considered as private so, "id" won't be seen in the response
So, removed underscore. Visit serializer of this version too. 
'''