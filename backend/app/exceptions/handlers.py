from fastapi import Request
from fastapi.responses import JSONResponse
from ..models.project import ProjectException
from ..models.prompt_template import PromptTemplateException
from ..models.prompt import PromptException
from ..models.llm import LLMException

async def project_exception_handler(request: Request, exc: ProjectException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )

async def prompt_template_exception_handler(request: Request, exc: PromptTemplateException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )

async def prompt_exception_handler(request: Request, exc: PromptException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )
    
async def llm_exception_handler(request: Request, exc: LLMException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )