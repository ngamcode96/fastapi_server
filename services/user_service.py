from config.database import userCollection
from schemas.user_schema import users_serializer
from models.User import User
from fastapi import HTTPException

async def get_user_info(email):
    user = users_serializer(userCollection.find({"email" : email}))
    return user

async def update_user(email: str, user_update):
    # Find the user with the given email in the database
    user =  userCollection.find_one({"email": email})
    
    # If the user with the given email doesn't exist, return an error response
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    userCollection.replace_one({"_id": user["_id"]}, user_update)
    
    return user


def canRemoveBg(user, nb_img):

    if (user["nb_images"] + nb_img) <= user["nb_images_total"]:
        return True
    else:
        return False