from fastapi import FastAPI
from routes import image,user
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost",
    "http://16.170.246.12"
    "http://localhost:3000",
    "https://discord.com",
    "chrome-extension://jmfmagommddgbnmfpgnemdcmpekcjiic"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get('/')
def root():
    return {"text": "welcome to amadou.ai API"}


app.include_router(image.router)
app.include_router(user.router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)