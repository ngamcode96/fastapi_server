from fastapi import APIRouter,HTTPException,Body
from config.database import userCollection
from models.User import User
from schemas.user_schema import user_serializer, users_serializer
from typing import List

router = APIRouter()

@router.get("/users/")
async def get_users():
    # print(userCollection.find())
    # users = users_serializer()
    users = userCollection.find()
    uu = users_serializer(users)
    return uu


@router.get("/users/{email}")
async def get_user(email):
    user = users_serializer(userCollection.find({"email" : email}))
    return {"status": "success", "user": user}


@router.post("/users/check")
async def check_user(userForm : dict = Body(...)):
    # Find the user with the given email in the database
    user =  userCollection.find_one({"email": userForm["email"]})
    
    # If the user with the given email doesn't exist, return an error response
    if user is None:
        new_user = User(username=userForm["username"], email=userForm["email"])
        new_user_dict = new_user.dict()
        result =  userCollection.insert_one(new_user_dict)
        new_user_dict["_id"] = str(result.inserted_id)
        return {"type": "user_info", "status": "success", "user": new_user_dict}
    
    user["_id"] = str(user["_id"])
    return {"type": "user_info", "status": "success", "user": user}

    


@router.post("/users/add")
async def add_user(user : User):

    user = users_serializer(userCollection.find({"username" : user.username}))

    if (len(user) == 0):
        user_dict = user.dict()
        result =  userCollection.insert_one(user_dict)
        user_dict["_id"] = str(result.inserted_id)
        # user = user_serializer(userCollection.find({"_id" : u.inserted_id}))
        return {"status": "success", "user": user_dict}
    else:
        raise HTTPException(status_code=500, detail="user already exist!")


