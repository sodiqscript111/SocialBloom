import pytest
from app.models.booking import Booking

@pytest.fixture(autouse=True)
def mock_grpc_notify(monkeypatch):
    def mock_notify(*args, **kwargs):
        return True, "mock_id"
    import grpc_clients.notification_client
    monkeypatch.setattr(grpc_clients.notification_client, "notify", mock_notify)

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_booking(client, db_session):
    from auth.dependencies import get_current_user
    
    def mock_get_current_user():
        return {"id": 1, "role": "user", "email": "test@test.com"}
        
    client.app.dependency_overrides[get_current_user] = mock_get_current_user
    
    response = client.post(
        "/bookings/100",
        json={
            "service_id": 10,
            "scheduled_time": "2027-01-01T10:00:00Z",
            "duration": 60,
            "total_price": 50.0
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["business_id"] == 100
    assert data["creator_id"] == 1
    assert data["total_price"] == 50.0
    
    booking = db_session.query(Booking).filter(Booking.id == data["id"]).first()
    assert booking is not None
    assert booking.status.value == "pending"
