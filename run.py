import uvicorn
from src.main import app
from src.config import HOST, PORT

if __name__ == "__main__":
    uvicorn.run("run:app", host=HOST, port=PORT, reload=True)
