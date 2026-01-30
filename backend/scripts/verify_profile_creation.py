
import asyncio
import os
import secrets
import sys
from uuid import uuid4

import asyncpg
import httpx

# Configuration
API_URL = "http://localhost:8000"
DB_URL = os.getenv("DATABASE_URL", "postgresql://godrive:godrive_dev_password@postgres:5432/godrive_db")

def generate_random_email():
    return f"test_instructor_{secrets.token_hex(4)}@example.com"

async def verify_profile_creation():
    email = generate_random_email()
    password = "SecurePassword123!"
    full_name = "Test Instructor"
    
    print(f"--- Starting Verification for {email} ---")

    # 1. Register User via API
    headers = {"Content-Type": "application/json"}
    payload = {
        "email": email,
        "password": password,
        "full_name": full_name,
        "user_type": "instructor"
    }

    try:
        async with httpx.AsyncClient() as client:
            print(f"Registering user...")
            response = await client.post(f"{API_URL}/auth/register", json=payload)
            
            if response.status_code != 201:
                print(f"Failed to register: {response.status_code}")
                print(response.text)
                return False
            
            user_data = response.json()
            user_id = user_data["id"]
            print(f"User registered successfully. ID: {user_id}")

    except Exception as e:
        print(f"API Error: {e}")
        return False

    # 2. Verify Database Records
    try:
        conn = await asyncpg.connect(DB_URL)
        
        # Check User Table
        print("Checking users table...")
        user_row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        if not user_row:
            print("ERROR: User not found in database!")
            await conn.close()
            return False
        print("User record found.")

        # Check Instructor Profile Table
        print("Checking instructor_profiles table...")
        profile_row = await conn.fetchrow("SELECT * FROM instructor_profiles WHERE user_id = $1", user_id)
        
        await conn.close()

        if profile_row:
            print("SUCCESS: Instructor profile found!")
            print(f"Profile ID: {profile_row['id']}")
            return True
        else:
            print("FAILURE: Instructor profile NOT found.")
            return False

    except Exception as e:
        print(f"Database Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(verify_profile_creation())
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
