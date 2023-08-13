from bson import ObjectId

def user_serializer(user) -> dict:
    return {
        "id" : user["_id"],
        "username": user["username"],
        "email": user["email"],
        "plan": user["plan"],
        "nb_images": user["nb_images"],
        "nb_images_total": user["nb_images_total"]
    }

def users_serializer(users) -> list:
    list_users = []
    for user in users:
        user["_id"] = str(user["_id"])
        list_users.append(user_serializer(user))
    return list_users

