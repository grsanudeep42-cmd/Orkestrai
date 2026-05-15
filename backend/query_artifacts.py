import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select, text
from app.db.models.generated_artifact import GeneratedArtifact

# AssumingDATABASE_URL is postgresql://postgres:password@localhost:5432/orkstrai
async def run():
    engine = create_async_engine("postgresql+asyncpg://postgres:password@localhost:5432/orkstrai")
    async with AsyncSession(engine) as session:
        result = await session.execute(text("SELECT id, artifact_type, generated_by FROM generated_artifacts WHERE project_id = '7ece684c-2369-4b47-8b2d-b97146aabb0c'"))
        rows = result.fetchall()
        for row in rows:
            print(row)

asyncio.run(run())
