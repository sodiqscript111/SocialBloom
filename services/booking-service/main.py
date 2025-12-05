import uvicorn
from fastapi import FastAPI
from app.api.routes import booking

app = FastAPI()

app.include_router(booking.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
