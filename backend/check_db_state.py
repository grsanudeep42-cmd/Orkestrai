import asyncio
from app.db.session import engine
from sqlalchemy import text

async def check_db():
    try:
        async with engine.connect() as conn:
            # Check users
            res = await conn.execute(text("SELECT id, username FROM users"))
            print("--- USERS ---")
            users = res.fetchall()
            for u in users:
                print(f"User: {u.id} | {u.username}")
            
            # Check projects
            res = await conn.execute(text("SELECT id, name, user_id, status FROM projects"))
            print("\n--- PROJECTS ---")
            projects = res.fetchall()
            if not projects:
                print("No projects found in database.")
            for p in projects:
                print(f"Project: {p.id} | Name: {p.name} | UserID: {p.user_id} | Status: {p.status}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_db())
