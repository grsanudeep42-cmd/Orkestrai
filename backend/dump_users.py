import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from app.db.models.user import User

async def dump_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        print(f"Total users: {len(users)}")
        for u in users:
            print(f"User: {u.username}")
            print(f"  bob_key: {u.bob_key}")
            print(f"  openai_key: {u.openai_key}")
            print(f"  gemini_key: {u.gemini_key}")
            print(f"  groq_key: {u.groq_key}")

if __name__ == "__main__":
    asyncio.run(dump_users())
