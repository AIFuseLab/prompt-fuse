from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..models.project import Project, ProjectException
from ..models.prompt_template import PromptTemplate
from ..schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
import sqlalchemy
from ..exceptions.error_messages import ErrorMessages
from typing import List
import uuid
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from ..utils.logger.logger import logger

router = APIRouter()

@router.post("/project", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    try:
        existing_project = (
            db.query(Project).filter(Project.name == project.name).first()
        )
        if existing_project:
            raise ProjectException(status_code=400, error_key="PROJECT_NAME_EXISTS")

        db_project = Project(name=project.name, description=project.description)
        db.add(db_project)
        db.commit()
        db.refresh(db_project)

        return ProjectResponse(
            id=str(db_project.id),
            name=db_project.name,
            description=db_project.description,
            creation_date=db_project.creation_date,
            last_updated=db_project.last_updated,
        )
    except ProjectException as pe:
        db.rollback()
        raise pe
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        raise ProjectException(
            status_code=400,
            error_key="PROJECT_NAME_EXISTS"
        )
    except Exception as e:
        db.rollback()
        raise ProjectException(
            status_code=500,
            error_key="UNEXPECTED_ERROR",
            detail=str(e)
        )


@router.get("/project/{project_id}", response_model=ProjectResponse)
def read_project(project_id: str, db: Session = Depends(get_db)):
    try:
        try:
            project_uuid = uuid.UUID(project_id)
        except ValueError:
            raise ProjectException(status_code=400, error_key="INVALID_PROJECT_ID_FORMAT")

        project = db.query(Project).filter(Project.id == project_uuid).first()

        if project is None:
            raise ProjectException(status_code=404, error_key="PROJECT_NOT_FOUND")

        return {
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
            "creation_date": project.creation_date,
            "last_updated": project.last_updated,
        }
    except ProjectException as pe:
        raise pe
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise ProjectException(status_code=500, error_key="DATABASE_ERROR")
    except Exception as e:
        raise ProjectException(
            status_code=500,
            error_key="UNEXPECTED_ERROR",
            detail=str(e)
        )


@router.put("/project/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str, project: ProjectUpdate, db: Session = Depends(get_db)
):
    try:
        try:
            project_uuid = uuid.UUID(project_id)
        except ValueError:
            raise ProjectException(status_code=400, error_key="INVALID_PROJECT_ID_FORMAT")

        db_project = db.query(Project).filter(Project.id == project_uuid).first()

        if db_project is None:
            raise ProjectException(status_code=404, error_key="PROJECT_NOT_FOUND")

        if project.name is not None:
            existing_project = db.query(Project).filter(
                Project.name == project.name,
                Project.id != project_uuid  # Exclude current project
            ).first()
            if existing_project:
                raise ProjectException(status_code=400, error_key="PROJECT_NAME_EXISTS")
    
        if project.name is not None:
            db_project.name = project.name
        if project.description is not None:
            db_project.description = project.description

        db.commit()
        db.refresh(db_project)

        return ProjectResponse(
            id=str(db_project.id),
            name=db_project.name,
            description=db_project.description,
            creation_date=db_project.creation_date,
            last_updated=db_project.last_updated,
        )
    except ProjectException as pe:
        db.rollback()
        raise pe
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        if "UniqueViolation" in str(e):
            raise ProjectException(status_code=400, error_key="PROJECT_NAME_EXISTS")
        raise ProjectException(status_code=500, error_key="PROJECT_UPDATE_ERROR")
    except sqlalchemy.exc.SQLAlchemyError as e:
        db.rollback()
        raise ProjectException(status_code=500, error_key="DATABASE_ERROR")
    except Exception as e:
        db.rollback()
        raise ProjectException(
            status_code=500,
            error_key="UNEXPECTED_ERROR",
            detail=str(e)
        )

@router.get("/projects", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    try:
        projects = db.query(Project).order_by(Project.creation_date.desc()).all()

        return [
            {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "creation_date": project.creation_date,
                "last_updated": project.last_updated,
            }
            for project in projects
        ]
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.delete("/project/{project_id}", response_model=dict)
def delete_project(project_id: str, db: Session = Depends(get_db)):
    try:
        try:
            uuid_obj = uuid.UUID(project_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid project ID format")

        # Check if the project exists
        project = db.query(Project).filter(Project.id == uuid_obj).first()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        # Delete all related prompts
        delete_prompts_query = text(
            "DELETE FROM prompts WHERE prompt_template_id IN "
            "(SELECT id FROM prompt_template WHERE project_id = :project_id)"
        )
        db.execute(delete_prompts_query, {"project_id": str(uuid_obj)})

        # Delete all related prompt templates
        delete_prompt_templates_query = text(
            "DELETE FROM prompt_template WHERE project_id = :project_id"
        )
        db.execute(delete_prompt_templates_query, {"project_id": str(uuid_obj)})

        db.delete(project)
        
        db.commit()
        return {"message": "Project and all related data deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, error_key="DATABASE_ERROR", detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            error_key="UNEXPECTED_ERROR",
            detail=str(e)
        )
