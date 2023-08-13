from pydantic import BaseModel
import time


class User(BaseModel):
    username: str
    email: str
    plan: int = 0
    nb_images: int = 0
    nb_images_total = 10
    created_at = time.time_ns()
