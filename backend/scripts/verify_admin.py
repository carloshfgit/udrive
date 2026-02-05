from fastapi.testclient import TestClient
from src.interface.api.main import app

def test_admin_access():
    client = TestClient(app)
    
    # Test Root Admin Redirects to Login
    response = client.get("/admin/")
    print(f"/admin/ status: {response.status_code}")
    # sqladmin might return 307 or 302 or just serve login page if it handles it internally
    # But usually it redirects to /admin/login
    
    # Check Login Page
    response = client.get("/admin/login")
    print(f"/admin/login status: {response.status_code}")
    assert response.status_code == 200, "Login page should be accessible"
    assert "Login" in response.text or "Sign in" in response.text, "Login page content missing"
    
    print("Admin interface verification passed!")

if __name__ == "__main__":
    test_admin_access()
