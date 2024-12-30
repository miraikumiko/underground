import asyncio
import uvicorn
from src.main import app
from src.config import HOST, PORT


async def main():
    uvicorn.run("run:app", host=HOST, port=PORT, reload=True)


if __name__ == "__main__":
    asyncio.run(main())
