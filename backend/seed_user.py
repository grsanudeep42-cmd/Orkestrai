import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import AsyncSessionLocal
from app.db.models.user import User

async def seed_user():
    async with AsyncSessionLocal() as session:
        # Create a test user
        new_user = User(
            username="test_user_bob",
            password_hash="fake_hash",
            bob_key="bob_prod_bob-user_2x9tL9VkYhKSpmRVxMj9D48EZksp7Ui3kGTdY3WnPRBex9oG4W9CbUvZXWLhpWyshqDvpsPLQdadjftDNUmQzhM1_8XJPTGyQkoSs7cTxAZuVFRm9yBtPr8HAAzi5vZZ1nPe6"
        )
        session.add(new_user)
        await session.commit()
        print("Test user created with bob_key.")

if __name__ == "__main__":
    asyncio.run(seed_user())
