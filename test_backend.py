import requests
import json

BASE_URL = "http://localhost:8000"
token = None

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health: {response.status_code} - {response.text}")
    assert response.status_code == 200

def test_root():
    response = requests.get(f"{BASE_URL}/")
    print(f"Root: {response.status_code} - {response.text}")
    assert response.status_code == 200

def test_register():
    params = {
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "testpass"
    }
    response = requests.post(f"{BASE_URL}/auth/register", params=params)
    print(f"Register: {response.status_code} - {response.text}")
    if response.status_code == 200:
        return True
    return False

def test_login():
    global token
    data = {
        "username": "testuser",
        "password": "testpass"
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=data)
    print(f"Login: {response.status_code} - {response.text}")
    if response.status_code == 200:
        token = response.json().get("access_token")
        return True
    return False

def test_me():
    if not token:
        print("No token, skipping /me")
        return
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Me: {response.status_code} - {response.text}")
    assert response.status_code == 200

def test_logout():
    response = requests.post(f"{BASE_URL}/auth/logout")
    print(f"Logout: {response.status_code} - {response.text}")
    assert response.status_code == 200

def test_qkd_run():
    params = {
        "key_length": 50,
        "noise_level": 5.0,
        "detector_efficiency": 95.0,
        "eavesdropper_present": False
    }
    response = requests.post(f"{BASE_URL}/qkd/run", json=params)
    print(f"QKD Run: {response.status_code} - {response.text}")
    if response.status_code == 200:
        session_id = response.json().get("session_id")
        return session_id
    return None

def test_qkd_session(session_id):
    if not session_id:
        return
    response = requests.get(f"{BASE_URL}/qkd/session/{session_id}")
    print(f"QKD Session: {response.status_code} - {response.text}")
    assert response.status_code == 200

def test_qkd_stats():
    response = requests.get(f"{BASE_URL}/qkd/stats")
    print(f"QKD Stats: {response.status_code} - {response.text}")
    assert response.status_code == 200

def test_sessions_list():
    response = requests.get(f"{BASE_URL}/sessions/")
    print(f"Sessions List: {response.status_code} - {response.text}")
    assert response.status_code == 200

def test_sessions_stats():
    response = requests.get(f"{BASE_URL}/sessions/stats/summary")
    print(f"Sessions Stats: {response.status_code} - {response.text}")
    assert response.status_code == 200

def test_edge_cases():
    # Invalid register
    params = {"username": "", "email": "invalid", "password": "short"}
    response = requests.post(f"{BASE_URL}/auth/register", params=params)
    print(f"Invalid Register: {response.status_code}")

    # Invalid login
    data = {"username": "wrong", "password": "wrong"}
    response = requests.post(f"{BASE_URL}/auth/login", data=data)
    print(f"Invalid Login: {response.status_code}")

    # Invalid QKD params
    params = {"key_length": 1000, "noise_level": 50}
    response = requests.post(f"{BASE_URL}/qkd/run", json=params)
    print(f"Invalid QKD: {response.status_code}")

    # Non-existent session
    response = requests.get(f"{BASE_URL}/qkd/session/nonexistent")
    print(f"Non-existent Session: {response.status_code}")

    response = requests.get(f"{BASE_URL}/sessions/nonexistent")
    print(f"Non-existent Session (sessions): {response.status_code}")

    response = requests.delete(f"{BASE_URL}/sessions/nonexistent")
    print(f"Delete Non-existent: {response.status_code}")

if __name__ == "__main__":
    try:
        test_health()
        test_root()
        test_register()
        test_login()
        test_me()
        test_logout()
        session_id = test_qkd_run()
        test_qkd_session(session_id)
        test_qkd_stats()
        test_sessions_list()
        test_sessions_stats()
        test_edge_cases()
        print("All tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
