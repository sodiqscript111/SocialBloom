import uvicorn
from fastapi import FastAPI
from app.api.routes import booking, campaign, payment, review, chat
from events.consumer import start_booking_event_consumer

from db.database import engine
from app.models.booking import Base
import app.models.booking
import app.models.campaign
import app.models.payment
import app.models.review
import app.models.chat

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Booking Service", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(booking.router)
app.include_router(campaign.router)
app.include_router(payment.router)
app.include_router(review.router)
app.include_router(chat.router)

@app.on_event("startup")
async def startup_event():
    start_booking_event_consumer()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
