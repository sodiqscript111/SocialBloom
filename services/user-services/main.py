import uvicorn
from fastapi import FastAPI
from app.api.routes import user, auth, social, matching

from db.database import engine
from app.models.user import Base, User

app = FastAPI(title="User Service", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(social.router)
app.include_router(matching.router)

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    try:
        from events.consumer import start_user_event_consumer
        start_user_event_consumer()
    except Exception as e:
        print(f"Warning: Failed to start event consumer: {e}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)