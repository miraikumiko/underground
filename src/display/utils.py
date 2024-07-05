from fastapi.templating import Jinja2Templates
from src.config import BASE_PATH
from src.display.filters import to_days

templates = Jinja2Templates(directory=f"{BASE_PATH}/templates")
templates.env.filters["to_days"] = to_days
