from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from src.config import BASE_PATH
from src.display.filters import to_days

templates = Jinja2Templates(directory=f"{BASE_PATH}/templates")
templates.env.filters["to_days"] = to_days


async def t_error(request: Request, status_code: int, detail: str) -> templates.TemplateResponse:
    return templates.TemplateResponse("error.html", {
        "request": request,
        "status_code": status_code,
        "detail": detail
    }, status_code=status_code)
