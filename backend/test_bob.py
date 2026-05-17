import asyncio
import os
import sys
from unittest.mock import patch, MagicMock

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from app.db.models.user import User
from app.llm.bob_provider import BobProvider

class MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP Error {self.status_code}")

async def test_bob():
    async with AsyncSessionLocal() as session:
        # Get user with bob_key
        result = await session.execute(select(User).where(User.bob_key.is_not(None)))
        user = result.scalars().first()
        
        if not user:
            print("No user found with bob_key in DB.")
            return

        print(f"Found user {user.username} with a bob_key: {user.bob_key[:15]}...")
        print("Testing BobProvider with mocked HTTP request...")
        
        provider = BobProvider(api_key=user.bob_key)
        
        # Mock response data
        mock_data = {
            "choices": [
                {
                    "message": {
                        "content": "Bob is working!"
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            }
        }
        
        with patch("httpx.AsyncClient.post") as mock_post:
            # Setup mock to return an async response
            async def async_return(*args, **kwargs):
                return MockResponse(mock_data)
                
            mock_post.side_effect = async_return
            
            try:
                content, stats = await provider.generate_text(
                    system_prompt="You are a helpful assistant.",
                    user_prompt="Say 'Bob is working!' if you receive this message."
                )
                print("\nSuccess! Bob logic is fully working!")
                print("====================================")
                print("Provider Name:", provider.name)
                print("Response:", content)
                print("Stats:", stats)
                
                # Verify the mocked call to ensure headers were set correctly
                call_args = mock_post.call_args
                headers = call_args.kwargs.get("headers", {})
                auth_header = headers.get("Authorization")
                if auth_header == f"Bearer {user.bob_key}":
                    print("✅ Authorization header correctly used the DB key.")
                else:
                    print("❌ Authorization header mismatch!")
                    
            except Exception as e:
                print("Error testing Bob:")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_bob())
