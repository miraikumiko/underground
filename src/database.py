from redis.asyncio import from_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from src.config import DB_PATH, REDIS_HOST, REDIS_PORT, BASE_PATH

DATABASE_URL = f"sqlite+aiosqlite:///{BASE_PATH}/{DB_PATH}"
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
r = from_url(REDIS_URL, decode_responses=True)
