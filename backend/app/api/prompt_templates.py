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
        if not prompt_template.name or prompt_template.name.strip() == "":
            raise PromptTemplateException(
                status_code=400, 
                error_key="INVALID_PROMPT_TEMPLATE_NAME"
            )

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
        raise PromptTemplateException(
            status_code=500,
            error_key="DATABASE_ERROR",
            detail=str(e),
        )
    except Exception as e:
        db.rollback()
        raise PromptTemplateException(
            status_code=500,
            error_key="UNEXPECTED_ERROR",
            detail=str(e),
        )

@router.get("/prompt-template/{template_id}", response_model=PromptTemplateResponse)
def read_prompt_template(template_id: str, db: Session = Depends(get_db)):
    try:
        try:
            template_uuid = uuid.UUID(template_id)
        except ValueError:
            raise PromptTemplateException(
                status_code=400, 
                error_key="INVALID_PROMPT_TEMPLATE_ID_FORMAT"
            )

        template = db.query(PromptTemplate).filter(PromptTemplate.id == template_uuid).first()
        if template is None:
            raise PromptTemplateException(
                status_code=404, 
                error_key="PROMPT_TEMPLATE_NOT_FOUND"
            )
            
        return PromptTemplateResponse.from_orm(template)
        
    except PromptTemplateException as pte:
        raise pte
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise PromptTemplateException(
            status_code=500, 
            error_key="DATABASE_ERROR",
            detail=str(e)
        )
    except Exception as e:
        raise PromptTemplateException(
            status_code=500,
            error_key="UNEXPECTED_ERROR",
            detail=str(e)
        )

@router.put("/prompt-template/{template_id}", response_model=PromptTemplateResponse)
def update_prompt_template(
    template_id: str, 
    template_update: PromptTemplateUpdate, 
    db: Session = Depends(get_db)
):
    try:
        # Validate template name
        if not template_update.name or template_update.name.strip() == "":
            raise PromptTemplateException(
                status_code=400, 
                error_key="INVALID_PROMPT_TEMPLATE_NAME"
            )

        # Validate template_id
        try:
            template_uuid = uuid.UUID(template_id)
        except ValueError:
            raise PromptTemplateException(
                status_code=400, 
                error_key="INVALID_PROMPT_TEMPLATE_ID_FORMAT"
            )

        # Check for existing template with same name (excluding current template)
        existing_template = db.query(PromptTemplate).filter(
            PromptTemplate.name == template_update.name,
            PromptTemplate.id != template_uuid
        ).first()
        
        if existing_template:
            raise PromptTemplateException(
                status_code=400, 
                error_key="PROMPT_TEMPLATE_NAME_EXISTS"
            )

        # Get current template
        db_template = db.query(PromptTemplate).filter(
            PromptTemplate.id == template_uuid
        ).first()
        
        if db_template is None:
            raise PromptTemplateException(
                status_code=404, 
                error_key="PROMPT_TEMPLATE_NOT_FOUND"
            )

        # Update template fields
        for key, value in template_update.dict(exclude_unset=True).items():
            setattr(db_template, key, value)

        db.commit()
        db.refresh(db_template)
        
        return PromptTemplateResponse.from_orm(db_template)
        
    except PromptTemplateException as pte:
        db.rollback()
        raise pte
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        raise PromptTemplateException(
            status_code=500,
            error_key="DATABASE_ERROR",
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise PromptTemplateException(
            status_code=500,
            error_key="UNEXPECTED_ERROR",
            detail=str(e)
        )
           
@router.get("/prompt-templates/{project_id}", response_model=List[PromptTemplateResponse])
def list_prompt_templates(
    project_id: str,
    db: Session = Depends(get_db)
):
    try:
        # Validate project_id is a valid UUID
        try:
            project_uuid = uuid.UUID(project_id)
        except ValueError:
            raise PromptTemplateException(
                status_code=400, 
                error_key="INVALID_PROJECT_ID_FORMAT"
            )
        
        # Query templates with validated UUID
        templates = db.query(PromptTemplate).filter(
            PromptTemplate.project_id == project_uuid
        ).all()
        
        if not templates:
            return []
        
        return [PromptTemplateResponse.from_orm(template) for template in templates]
        
    except PromptTemplateException as pte:
        raise pte
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise PromptTemplateException(
            status_code=500, 
            error_key="DATABASE_ERROR",
            detail=str(e)
        )
    except Exception as e:
        raise PromptTemplateException(
            status_code=500,
            error_key="UNEXPECTED_ERROR",
            detail=str(e)
        )

@router.delete("/prompt-template/{template_id}", response_model=dict)
def delete_prompt_template(template_id: str, db: Session = Depends(get_db)):
    try:
        # Validate template_id
        try:
            template_uuid = uuid.UUID(template_id)
        except ValueError:
            raise PromptTemplateException(
                status_code=400, 
                error_key="INVALID_PROMPT_TEMPLATE_ID_FORMAT"
            )
        
        # Find and delete template
        db_template = db.query(PromptTemplate).filter(
            PromptTemplate.id == template_uuid
        ).first()
        
        if db_template is None:
            raise PromptTemplateException(
                status_code=404, 
                error_key="PROMPT_TEMPLATE_NOT_FOUND"
            )

        db.delete(db_template)
        db.commit()

        return {"message": "Prompt Template Deleted Successfully"}
        
    except PromptTemplateException as pte:
        # Re-raise our custom exceptions
        raise pte
    except sqlalchemy.exc.SQLAlchemyError as e:
        db.rollback()
        raise PromptTemplateException(
            status_code=500, 
            error_key="DATABASE_ERROR",
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise PromptTemplateException(
            status_code=500,
            error_key="UNEXPECTED_ERROR",
            detail=str(e)
        )
