from fastapi.templating import Jinja2Templates
from src.display.filters import to_days

templates = Jinja2Templates(directory="templates")
templates.env.filters["to_days"] = to_days
