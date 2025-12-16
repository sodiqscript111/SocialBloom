import uvicorn
from fastapi import FastAPI
from app.api.routes import user, auth, social

app = FastAPI(title="User Service", version="1.0.0")

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(social.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)