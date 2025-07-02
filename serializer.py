# def userEntity(item) -> dict:
#     return {
#         "id" : str(item["_id"]),
#         "name" : item["name"],
#         "email" : item["email"],
#         "password" :item["password"]
#     }
# def usersEntity(entity) -> list:
#     return [userEntity(item) for item in entity]
def userEntity(item)->dict:
    return {**{"id":str(item[i]) for i in item if i == "_id"},**{i : item[i] for i in item if i != "_id"}}
def usersEntity(entity)->list:
    return [userEntity(item) for item in entity]

'''
    initially the _id name haven't changed but now _id is 
renamed as "id" to avoid pydantic validation for id.
'''