from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..models.prompt_template import PromptTemplate, PromptTemplateException
from ..schemas.prompt_template import PromptTemplateCreate, PromptTemplateResponse, PromptTemplateUpdate
import sqlalchemy
from ..exceptions.error_messages import ErrorMessages
from typing import List
import uuid

router = APIRouter()

@router.post("/prompt-templates", response_model=PromptTemplateResponse)
def create_prompt_template(prompt_template: PromptTemplateCreate, db: Session = Depends(get_db)):
    try:
        existing_template = db.query(PromptTemplate).filter(PromptTemplate.name == prompt_template.name).first()
        if existing_template:
            raise PromptTemplateException(status_code=400, error_key="PROMPT_TEMPLATE_NAME_EXISTS")
                
        db_prompt_template = PromptTemplate(**prompt_template.dict())
        db.add(db_prompt_template)
        db.commit()
        db.refresh(db_prompt_template)

        return PromptTemplateResponse.from_orm(db_prompt_template)
    except PromptTemplateException as pte:
        db.rollback()
        raise pte
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred while creating the prompt template: Database integrity error",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the prompt template: {str(e)}",
        )

@router.get("/prompt-template/{template_id}", response_model=PromptTemplateResponse)
def read_prompt_template(template_id: str, db: Session = Depends(get_db)):
    try:
        template = db.query(PromptTemplate).filter(PromptTemplate.id == uuid.UUID(template_id)).first()
        if template is None:
            raise PromptTemplateException(status_code=404, error_key="PROMPT_TEMPLATE_NOT_FOUND")
        return PromptTemplateResponse.from_orm(template)
    except ValueError:
        raise PromptTemplateException(status_code=400, error_key="INVALID_PROMPT_TEMPLATE_ID_FORMAT")
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise PromptTemplateException(status_code=500, error_key="DATABASE_ERROR")
    except Exception as e:
        raise PromptTemplateException(
            status_code=500,
            error_key="UNEXPECTED_ERROR",
            detail=f"{ErrorMessages.UNEXPECTED_ERROR}: {str(e)}",
        )

@router.put("/prompt-template/{template_id}", response_model=PromptTemplateResponse)
def update_prompt_template(template_id: str, prompt_template: PromptTemplateUpdate, db: Session = Depends(get_db)):
    try:
        db_template = db.query(PromptTemplate).filter(PromptTemplate.id == uuid.UUID(template_id)).first()
        if db_template is None:
            raise PromptTemplateException(status_code=404, error_key="PROMPT_TEMPLATE_NOT_FOUND")

        for key, value in prompt_template.dict(exclude_unset=True).items():
            setattr(db_template, key, value)

        db.commit()
        db.refresh(db_template)

        return PromptTemplateResponse.from_orm(db_template)
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        if "UniqueViolation" in str(e):
            raise PromptTemplateException(status_code=400, error_key="PROMPT_TEMPLATE_NAME_EXISTS")
        else:
            raise PromptTemplateException(status_code=500, error_key="PROMPT_TEMPLATE_UPDATE_ERROR")
    except ValueError:
        raise PromptTemplateException(status_code=400, error_key="INVALID_PROMPT_TEMPLATE_ID_FORMAT")
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise PromptTemplateException(status_code=500, error_key="DATABASE_ERROR")
    except Exception as e:
        raise PromptTemplateException(
            status_code=500,
            error_key="UNEXPECTED_ERROR",
            detail=f"{ErrorMessages.UNEXPECTED_ERROR}: {str(e)}",
        )

@router.get("/prompt-templates/{project_id}", response_model=List[PromptTemplateResponse])
def list_prompt_templates(
    project_id: str,
    db: Session = Depends(get_db)
):
    try:
        templates = db.query(PromptTemplate).filter(PromptTemplate.project_id == project_id).all()
        
        if not templates:
            return []
        
        return [PromptTemplateResponse.from_orm(template) for template in templates]
    except ValueError:
        raise PromptTemplateException(status_code=400, error_key="INVALID_PROJECT_ID_FORMAT")
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise PromptTemplateException(status_code=500, error_key="DATABASE_ERROR")
    except Exception as e:
        raise PromptTemplateException(
            status_code=500,
            error_key="UNEXPECTED_ERROR",
            detail=f"{ErrorMessages.UNEXPECTED_ERROR}: {str(e)}",
        )

@router.delete("/prompt-template/{template_id}", response_model=dict)
def delete_prompt_template(template_id: str, db: Session = Depends(get_db)):
    try:
        db_template = db.query(PromptTemplate).filter(PromptTemplate.id == uuid.UUID(template_id)).first()
        if db_template is None:
            raise PromptTemplateException(status_code=404, error_key="PROMPT_TEMPLATE_NOT_FOUND")

        db.delete(db_template)
        db.commit()

        return {"message": "Prompt Template Deleted Successfully"}
    except ValueError:
        raise PromptTemplateException(status_code=400, error_key="INVALID_PROMPT_TEMPLATE_ID_FORMAT")
    except sqlalchemy.exc.SQLAlchemyError as e:
        db.rollback()
        raise PromptTemplateException(status_code=500, error_key="DATABASE_ERROR")
    except Exception as e:
        raise PromptTemplateException(
            status_code=500,
            error_key="UNEXPECTED_ERROR",
            detail=f"{ErrorMessages.UNEXPECTED_ERROR}: {str(e)}",
        )
