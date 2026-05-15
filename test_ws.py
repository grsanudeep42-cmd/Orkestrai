import asyncio
import websockets

async def test():
    uri = "ws://localhost:8000/api/v1/ws/orchestration/689121b5-d4ca-405e-903e-66d847ff08a0"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected")
            msg = await websocket.recv()
            print("Received:", msg)
    except Exception as e:
        print("Error:", e)

asyncio.run(test())
