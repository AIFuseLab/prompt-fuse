from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..models.llm import LLM, LLMException
from ..schemas.llm import LLMCreate, LLMResponse, LLMUpdate, ConversationInput
import sqlalchemy
from ..exceptions.error_messages import ErrorMessages
from typing import List
import uuid
import boto3
from ..schemas.llm import ImageConversationInput
from botocore.exceptions import ClientError
import json

router = APIRouter()

@router.post("/llms", response_model=LLMResponse)
def create_llm(llm: LLMCreate, db: Session = Depends(get_db)):
    try:
        existing_llm = db.query(LLM).filter(LLM.name == llm.name).first()
        if existing_llm:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "LLM with this name already exists",
                    "error_key": "LLM_NAME_EXISTS"
                }
            )
        
        # Create new LLM
        db_llm = LLM(**llm.dict())
        db.add(db_llm)
        db.commit()
        db.refresh(db_llm)
        
        return LLMResponse.from_orm(db_llm)
        
    except HTTPException as he:
        db.rollback()
        raise he
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Database integrity error",
                "error_key": "DATABASE_ERROR"
            }
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"An unexpected error occurred: {str(e)}",
                "error_key": "INTERNAL_ERROR"
            }
        )
        
@router.get("/llm/{llm_id}", response_model=LLMResponse)
def read_llm(llm_id: str, db: Session = Depends(get_db)):
    try:
        # Validate UUID
        try:
            uuid_obj = uuid.UUID(llm_id)
        except ValueError:
            raise LLMException(
                status_code=400,
                error_key="INVALID_LLM_ID_FORMAT"            )
        
        # Query LLM
        llm = db.query(LLM).filter(LLM.id == uuid_obj).first()
        if llm is None:
            raise LLMException(
                status_code=404,
                error_key="LLM_NOT_FOUND"            )
            
        return LLMResponse.from_orm(llm)
        
    except HTTPException as he:
        raise he
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise LLMException(
            status_code=500,
            error_key="DATABASE_ERROR"
        )
    except Exception as e:
        raise LLMException(
            status_code=500,
            error_key="INTERNAL_ERROR",
            detail=f"An unexpected error occurred: {str(e)}",
        )


@router.put("/llm/{llm_id}", response_model=LLMResponse)
def update_llm(llm_id: str, llm: LLMUpdate, db: Session = Depends(get_db)):
    try:
        # Validate UUID
        try:
            uuid_obj = uuid.UUID(llm_id)
        except ValueError:
            raise LLMException(
                status_code=400,
                error_key="INVALID_LLM_ID_FORMAT"
            )
        
        # Check if LLM exists
        db_llm = db.query(LLM).filter(LLM.id == uuid_obj).first()
        if db_llm is None:
            raise LLMException(
                status_code=404,
                error_key="LLM_NOT_FOUND"
            )

        # Update LLM fields
        for key, value in llm.dict(exclude_unset=True).items():
            setattr(db_llm, key, value)

        try:
            db.commit()
            db.refresh(db_llm)
        except sqlalchemy.exc.IntegrityError as e:
            db.rollback()
            raise LLMException(
                status_code=400,
                error_key="LLM_NAME_EXISTS"
            )

        return LLMResponse.from_orm(db_llm)
        
    except HTTPException as he:
        raise he
    except sqlalchemy.exc.SQLAlchemyError as e:
        db.rollback()
        raise LLMException(
            status_code=500,
            error_key="DATABASE_ERROR"
        )
    except Exception as e:
        db.rollback()
        raise LLMException(
            status_code=500,
            error_key="INTERNAL_ERROR",
            detail=f"An unexpected error occurred: {str(e)}",
        )

@router.get("/llms", response_model=List[LLMResponse])
def list_llms(db: Session = Depends(get_db)):
    try:
        llms = db.query(LLM).all()
        
        return [LLMResponse.from_orm(llm) for llm in llms]
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise LLMException(status_code=500, error_key="DATABASE_ERROR")
    except Exception as e:
        raise LLMException(
            status_code=500,
            error_key="UNEXPECTED_ERROR",
            detail=f"{ErrorMessages.UNEXPECTED_ERROR}: {str(e)}",
        )


@router.delete("/llm/{llm_id}", response_model=dict)
def delete_llm(llm_id: str, db: Session = Depends(get_db)):
    try:
        # Validate UUID
        try:
            uuid_obj = uuid.UUID(llm_id)
        except ValueError:
            raise LLMException(
                status_code=400,
                error_key="INVALID_LLM_ID_FORMAT"
            )
        
        # Check if LLM exists
        db_llm = db.query(LLM).filter(LLM.id == uuid_obj).first()
        if db_llm is None:
            raise LLMException(
                status_code=404,
                error_key="LLM_NOT_FOUND"
                
            )

        # Delete LLM
        db.delete(db_llm)
        db.commit()

        return {"message": "LLM Deleted Successfully"}
        
    except HTTPException as he:
        raise he
    except sqlalchemy.exc.SQLAlchemyError as e:
        db.rollback()
        raise LLMException(
            status_code=500,
            error_key="DATABASE_ERROR"
        )
    except Exception as e:
        db.rollback()
        raise LLMException(
            status_code=500,
            error_key="INTERNAL_ERROR",

        )

@router.post("/llm/converse", response_model=dict)
async def converse_with_llm(conversation_input: ConversationInput, db: Session = Depends(get_db)):
    try:
        # Validate UUID
        try:
            uuid_obj = uuid.UUID(conversation_input.llm_id)
        except ValueError:
            raise LLMException(
                status_code=400,
                error_key="INVALID_LLM_ID_FORMAT"
            )
        
        # Get LLM
        llm = db.query(LLM).filter(LLM.id == uuid_obj).first()
        if llm is None:
            raise LLMException(
                status_code=404,
                error_key="LLM_NOT_FOUND"
            )

        # Configure AWS credentials
        bedrock = boto3.client(
            service_name='bedrock-runtime',
            aws_access_key_id=llm.access_key,
            aws_secret_access_key=llm.secret_access_key,
            region_name=llm.aws_region
        )

        # Prepare the prompt
        prompt_content = f"{conversation_input.prompt}\n\nHuman: {conversation_input.user_input}\n\nAssistant:"

        # Prepare the request body
        request_body = {
            "prompt": prompt_content,
            "max_tokens_to_sample": conversation_input.max_tokens,
            "temperature": conversation_input.temperature,
            "top_p": conversation_input.top_p,
        }

        try:
            # Make the API call to AWS Bedrock
            response = bedrock.invoke_model(
                modelId=llm.llm_model_id,
                body=json.dumps(request_body)
            )
            
            # Parse the response
            response_body = json.loads(response['body'].read())
            llm_response = response_body.get('completion', '')

            return {"message": llm_response}

        except ClientError as e:
            raise LLMException(
                status_code=500,
                error_key="AWS_API_ERROR",
                detail=f"AWS Bedrock API error: {str(e)}",
            )

    except HTTPException as he:
        raise he
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise LLMException( 
            status_code=500,
            error_key="DATABASE_ERROR",
            detail=str(e),
        )
    except Exception as e:
        raise LLMException(
            status_code=500,
            error_key="INTERNAL_ERROR",
            detail=str(e),
        )

@router.post("/llm/converse-image", response_model=dict)
async def converse_with_llm_image(
    conversation_input: ImageConversationInput,
    db: Session = Depends(get_db),
):
    """
    Sends a message with text and image to a model.
    """
    try:
        # Validate UUID
        try:
            uuid_obj = uuid.UUID(conversation_input.llm_id)
        except ValueError:
            raise LLMException(
                status_code=400,
                error_key="INVALID_LLM_ID_FORMAT"
            )

        # Get LLM
        llm = db.query(LLM).filter(LLM.id == uuid_obj).first()
        if llm is None:
            raise LLMException(
                status_code=404,
                error_key="LLM_NOT_FOUND"
            )

        # Configure AWS client
        bedrock = boto3.client(
            service_name="bedrock-runtime",
            aws_access_key_id=llm.access_key,
            aws_secret_access_key=llm.secret_access_key,
            region_name=llm.aws_region,
        )

        if conversation_input.image is None:
            raise LLMException(
                status_code=400,
                error_key="IMAGE_REQUIRED"
            )

        image_content = conversation_input.image
        if not image_content:
            raise LLMException(
                status_code=400,
                error_key="EMPTY_IMAGE"
            )

        # Prepare message
        message = {
            "role": "user",
            "content": [
                {"text": conversation_input.prompt},
                {"image": {"format": "jpeg", "source": {"bytes": image_content}}},
            ],
        }

        try:
            response = bedrock.converse(
                modelId=llm.llm_model_id,
                messages=[message],
                inferenceConfig={
                    "temperature": conversation_input.temperature,
                    "maxTokens": conversation_input.max_tokens,
                    "topP": conversation_input.top_p,
                },
            )
            return response

        except ClientError as e:
            raise LLMException(
                status_code=500,
                error_key="AWS_API_ERROR",
                detail=str(e),
            
            )

    except HTTPException as he:
        raise he
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise LLMException(
            status_code=500,
            error_key="DATABASE_ERROR",
            detail=str(e),
        )
    except Exception as e:
        raise LLMException(
            status_code=500,
            error_key="INTERNAL_ERROR",
            detail=str(e),
        )