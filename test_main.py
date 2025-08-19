from fastapi.testclient import TestClient
from main import app, history, HISTORY_MAX

client = TestClient(app)

def test_basic_division():
    history.clear()
    r = client.post("/calculate", params={"expr": "30/4"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 7.5) < 1e-9

def test_percent_subtraction():
    history.clear()
    r = client.post("/calculate", params={"expr": "100 - 6%"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 94.0) < 1e-9

def test_standalone_percent():
    history.clear()
    r = client.post("/calculate", params={"expr": "6%"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 0.06) < 1e-9

def test_invalid_expr_returns_ok_false():
    history.clear()
    r = client.post("/calculate", params={"expr": "2**(3"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is False
    assert "error" in data and data["error"] != ""

# --- History API Tests ---

def test_get_history_empty():
    """Test retrieving history when it's empty."""
    history.clear()
    response = client.get("/history")
    assert response.status_code == 200
    assert response.json()["history"] == []

def test_get_history_with_limit():
    """Test retrieving a limited number of history items."""
    history.clear()
    client.post("/calculate", params={"expr": "1+1"})
    client.post("/calculate", params={"expr": "2*2"})
    client.post("/calculate", params={"expr": "3/3"})
    
    response = client.get("/history", params={"limit": 2})
    assert response.status_code == 200
    history_data = response.json()["history"]
    assert len(history_data) == 2
    assert history_data[0]["expression"] == "2*2"
    assert history_data[1]["expression"] == "3/3"

def test_get_history_full_list():
    """Test retrieving the full history list."""
    history.clear()
    client.post("/calculate", params={"expr": "10-5"})
    client.post("/calculate", params={"expr": "100/10"})
    
    response = client.get("/history")
    assert response.status_code == 200
    history_data = response.json()["history"]
    assert len(history_data) == 2
    assert history_data[0]["expression"] == "10-5"
    assert history_data[1]["expression"] == "100/10"

def test_clear_history():
    """Test clearing the history."""
    # First, add some items to history
    client.post("/calculate", params={"expr": "1+1"})
    client.post("/calculate", params={"expr": "2*2"})
    
    # Then, clear it
    response = client.delete("/history")
    assert response.status_code == 200
    assert response.json()["message"] == "History cleared successfully."
    
    # Finally, check if history is empty
    response_check = client.get("/history")
    assert response_check.status_code == 200
    assert response_check.json()["history"] == []
    
def test_history_clears_after_delete_multiple_times():
    """
    Test that the delete endpoint works consistently, even if called multiple times.
    """
    client.post("/calculate", params={"expr": "5+5"})
    client.delete("/history")
    client.post("/calculate", params={"expr": "12*2"})
    
    response = client.delete("/history")
    assert response.status_code == 200
    assert response.json()["message"] == "History cleared successfully."
    
    response_check = client.get("/history")
    assert response_check.status_code == 200
    assert response_check.json()["history"] == []