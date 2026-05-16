import asyncio
import sys
import os

# Add the current directory to sys.path so we can import app modules
sys.path.insert(0, os.path.abspath("."))

from app.agents.pitch_agent import PitchAgent
from app.agents.builder_agent import BuilderAgent

async def test():
    pitch_agent = PitchAgent()
    builder_agent = BuilderAgent()
    
    strategy_output = {"project_name": "Test Project"}
    architecture_output = {}
    
    print("Testing BuilderAgent...")
    try:
        await builder_agent.generate_implementation_plan(strategy_output, architecture_output, "test input")
    except Exception as e:
        print(f"Exception: {e}")
        
    print("Testing PitchAgent...")
    try:
        await pitch_agent.generate_pitch_materials(strategy_output, architecture_output, {}, {}, "test input")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test())
