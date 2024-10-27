from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..models.prompt import Prompt, PromptException
from ..models.test import Test
from ..models.llm import LLM
from ..schemas.prompt import PromptCreate, PromptResponse, PromptUpdate
import sqlalchemy
from ..exceptions.error_messages import ErrorMessages
from typing import List
import uuid
from sqlalchemy import func
from ..models.test import test_prompt_association

router = APIRouter()

@router.post("/prompt", response_model=PromptResponse)
def create_prompt(prompt: PromptCreate, db: Session = Depends(get_db)):
    try:
        existing_prompt = db.query(Prompt).filter(Prompt.name == prompt.name).first()
        if existing_prompt:
            raise PromptException(status_code=400, error_key="PROMPT_NAME_EXISTS")
        
        db_prompt = Prompt(**prompt.dict())
        db.add(db_prompt)
        db.commit()
        db.refresh(db_prompt)

        return PromptResponse.from_orm(db_prompt)
    except PromptException as pe:
        db.rollback()
        raise pe
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred while creating the prompt: Database integrity error",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the prompt: {str(e)}",
        )

@router.get("/prompt/{prompt_id}", response_model=PromptResponse)
def read_prompt(prompt_id: str, db: Session = Depends(get_db)):
    try:
        prompt = db.query(Prompt).filter(Prompt.id == uuid.UUID(prompt_id)).first()
        if prompt is None:
            raise PromptException(status_code=404, error_key="PROMPT_NOT_FOUND")
        prompt.llm_model_name = db.query(LLM).filter(LLM.id == prompt.llm_id).first().name
        return PromptResponse.from_orm(prompt)
    except ValueError:
        raise PromptException(status_code=400, error_key="INVALID_PROMPT_ID_FORMAT")
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise PromptException(status_code=500, error_key="DATABASE_ERROR")
    except Exception as e:
        raise PromptException(
            status_code=500,
            error_key="UNEXPECTED_ERROR",
            detail=f"{ErrorMessages.UNEXPECTED_ERROR}: {str(e)}",
        )

@router.put("/prompt/{prompt_id}", response_model=PromptResponse)
def update_prompt(prompt_id: str, prompt: PromptUpdate, db: Session = Depends(get_db)):
    try:
        db_prompt = db.query(Prompt).filter(Prompt.id == uuid.UUID(prompt_id)).first()
        if db_prompt is None:
            raise PromptException(status_code=404, error_key="PROMPT_NOT_FOUND")

        if (prompt.prompt is not None and prompt.prompt != db_prompt.prompt) or (prompt.llm_id is not None and prompt.llm_id != db_prompt.llm_id):
            max_version = db.query(func.max(Prompt.version)).filter(Prompt.prompt_template_id == db_prompt.prompt_template_id).scalar() or 0
            new_prompt = Prompt(
                name=f"{db_prompt.name}_v_{max_version + 1:.1f}",
                prompt=prompt.prompt,
                notes=prompt.notes if prompt.notes is not None else db_prompt.notes,
                version=max_version + 1,
                llm_id=prompt.llm_id if prompt.llm_id is not None else db_prompt.llm_id,
                prompt_template_id=db_prompt.prompt_template_id
            )
            db.add(new_prompt)
            db.commit()
            db.refresh(new_prompt)
            return PromptResponse.from_orm(new_prompt)
        else:
            for key, value in prompt.dict(exclude_unset=True).items():
                if key != 'prompt':
                    setattr(db_prompt, key, value)
            db.commit()
            db.refresh(db_prompt)
            return PromptResponse.from_orm(db_prompt)

    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        if "UniqueViolation" in str(e):
            raise PromptException(status_code=400, error_key="PROMPT_NAME_EXISTS")
        else:
            raise PromptException(status_code=500, error_key="PROMPT_UPDATE_ERROR")
    except ValueError:
        raise PromptException(status_code=400, error_key="INVALID_PROMPT_ID_FORMAT")
    except sqlalchemy.exc.SQLAlchemyError as e:
        db.rollback()
        raise PromptException(status_code=500, error_key="DATABASE_ERROR")
    except Exception as e:
        db.rollback()
        raise PromptException(
            status_code=500,
            error_key="UNEXPECTED_ERROR",
            detail=f"{ErrorMessages.UNEXPECTED_ERROR}: {str(e)}",
        )
        
@router.get("/prompts/{prompt_template_id}", response_model=List[PromptResponse])
def list_prompts(prompt_template_id: str, db: Session = Depends(get_db)):
    try:
        prompts = db.query(Prompt).filter(Prompt.prompt_template_id == uuid.UUID(prompt_template_id)).all()
        for prompt in prompts:
            prompt.llm_model_name = db.query(LLM).filter(LLM.id == prompt.llm_id).first().name
            
        return [PromptResponse.from_orm(prompt) for prompt in prompts]
    except ValueError:
        raise PromptException(status_code=400, error_key="INVALID_PROMPT_TEMPLATE_ID_FORMAT")
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise PromptException(status_code=500, error_key="DATABASE_ERROR")
    except Exception as e:
        raise PromptException(
            status_code=500,
            error_key="UNEXPECTED_ERROR",
            detail=f"{ErrorMessages.UNEXPECTED_ERROR}: {str(e)}",
        )

@router.delete("/prompt/{prompt_id}", response_model=dict)
def delete_prompt(prompt_id: str, db: Session = Depends(get_db)):
    try:
        db_prompt = db.query(Prompt).filter(Prompt.id == uuid.UUID(prompt_id)).first()
        if db_prompt is None:
            raise PromptException(status_code=404, error_key="PROMPT_NOT_FOUND")
        
        db.execute(test_prompt_association.delete().where(
            test_prompt_association.c.prompt_id == uuid.UUID(prompt_id)
        ))
        
        db.delete(db_prompt)
        db.commit()

        return {"message": "Prompt Deleted Successfully"}
    except ValueError:
        raise PromptException(status_code=400, error_key="INVALID_PROMPT_ID_FORMAT")
    except sqlalchemy.exc.SQLAlchemyError as e:
        db.rollback()
        raise PromptException(status_code=500, error_key="DATABASE_ERROR")
    except Exception as e:
        raise PromptException(
            status_code=500,
            error_key="UNEXPECTED_ERROR",
            detail=f"{ErrorMessages.UNEXPECTED_ERROR}: {str(e)}",
        )