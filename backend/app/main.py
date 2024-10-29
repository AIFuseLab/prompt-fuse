from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import projects, llms, prompt_templates, prompts, tests
from .db.database import engine, Base
from .exceptions.handlers import project_exception_handler
from .models.project import ProjectException
from .models.test import Test
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(projects.router, tags=["projects"], prefix="/api/v1")
app.include_router(llms.router, tags=["llms"], prefix="/api/v1")
app.include_router(prompt_templates.router, tags=["prompt_templates"], prefix="/api/v1")
app.include_router(prompts.router, tags=["prompts"], prefix="/api/v1")
app.include_router(tests.router, tags=["tests"], prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the Prompt Management System API"}

app.add_exception_handler(ProjectException, project_exception_handler)
