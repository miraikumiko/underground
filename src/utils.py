from src.logger import logger


def err_catch(func):
    async def wrapper(*args, **kwargs):
        try:
            await func(*args, **kwargs)
        except Exception as e:
            logger.error(e)
            raise e
    return wrapper
