def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_register_user(client):
    payload = {
        "email": "test@example.com",
        "password": "securepassword",
        "username": "testuser",
        "role": "creator",
        "full_name": "Test User"
    }
    response = client.post("/register", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data
    assert "password" not in data

def test_register_duplicate_email(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "securepassword",
        "username": "dupuser",
        "role": "creator"
    }
    
    # Register first time
    response1 = client.post("/register", json=payload)
    assert response1.status_code == 200
    
    # Register second time
    response2 = client.post("/register", json=payload)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Email already registered"
