from fastapi import Request
from fastapi.responses import JSONResponse
from ..models.project import ProjectException


async def project_exception_handler(request: Request, exc: ProjectException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )