
import asyncio
import json
import os
import secrets
import sys
import urllib.request
import urllib.parse
from urllib.error import HTTPError

# Configuration
API_URL = "http://localhost:8000"

def generate_random_email():
    return f"test_student_{secrets.token_hex(4)}@example.com"

def make_request(method, url, data=None, headers=None):
    if headers is None:
        headers = {}
    
    encoded_data = None
    if data:
        if headers.get("Content-Type") == "application/json":
            encoded_data = json.dumps(data).encode('utf-8')
        else:
            encoded_data = urllib.parse.urlencode(data).encode('utf-8')
            
    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, response.read().decode('utf-8')
    except HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        print(f"Request Error: {e}")
        return 500, str(e)

def verify_query():
    email = generate_random_email()
    password = "SecurePassword123!"
    full_name = "Test Student"
    
    print(f"--- Starting Query Verification (urllib) for {email} ---")

    # 1. Register Student
    print(f"Registering student...")
    payload = {
        "email": email,
        "password": password,
        "full_name": full_name,
        "user_type": "student",
        "phone": "11999999999",
        "cpf": secrets.token_hex(5), # Fake CPF
        "birth_date": "2000-01-01",
        "biological_sex": "Masculino"
    }
    
    status, body = make_request("POST", f"{API_URL}/auth/register", payload, {"Content-Type": "application/json"})
    
    if status != 201:
        print(f"Registration failed: {status} {body}")
        return False
        
    print("Registration successful.")

    # 2. Login
    print("Logging in...")
    login_data = {
        "email": email,
        "password": password
    }
    # Form data for OAuth2 login
    status, body = make_request("POST", f"{API_URL}/auth/login", login_data, {"Content-Type": "application/json"})
    
    if status != 200:
        print(f"Login failed: {status} {body}")
        return False
        
    token = json.loads(body)["access_token"]
    print(f"Login successful. Token acquired.")

    # 3. Search Instructors
    print("Triggering Search...")
    headers = {"Authorization": f"Bearer {token}"}
    params = urllib.parse.urlencode({
        "latitude": -15.7695228,
        "longitude": -47.8887014,
        "radius_km": 10,
        "limit": 50
    })
    
    status, body = make_request("GET", f"{API_URL}/api/v1/student/instructors/search?{params}", None, headers)
    
    if status == 200:
        print("Search successful (200 OK). Query executed.")
        return True
    else:
        print(f"Search failed: {status} {body}")
        return False

if __name__ == "__main__":
    success = verify_query()
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
