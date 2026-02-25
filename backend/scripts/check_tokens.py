import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

from src.infrastructure.services.token_encryption import decrypt_token
from src.infrastructure.config import get_settings

async def main():
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT user_id, mp_access_token FROM instructor_profiles"))
        rows = result.fetchall()
        for row in rows:
            user_id = row[0]
            encrypted_token = row[1]
            if encrypted_token:
                try:
                    token = decrypt_token(encrypted_token)
                    prefix = token[:8]
                    print(f"User {user_id}: token starts with {prefix}")
                except Exception as e:
                    print(f"User {user_id}: decrypt error {e}")
            else:
                print(f"User {user_id}: no token")
            
if __name__ == "__main__":
    asyncio.run(main())
