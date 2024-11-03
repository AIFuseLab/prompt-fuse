from ..models.llm import LLMException
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..models.test import Test, TestException
from ..schemas.test import TestCreate, TestResponse, TestUpdate
import sqlalchemy
from ..exceptions.error_messages import ErrorMessages
from typing import List
import uuid
from ..models.prompt import Prompt
from ..models.test import test_prompt_association
from sqlalchemy import delete
from .llms import converse_with_llm, converse_with_llm_image
from ..schemas.llm import ConversationInput, ImageConversationInput
from datetime import datetime
import gpt3_tokenizer
from typing import Optional
import json
import base64

router = APIRouter()

@router.post("/test/text", response_model=TestResponse)
async def create_test(test: TestCreate, db: Session = Depends(get_db)):
    try:
        db_test = Test(test_name=test.test_name, user_input=test.user_input)


        db.add(db_test)
        db.flush()

        prompts = db.query(Prompt).filter(Prompt.id.in_(test.prompt_ids)).all()


        if len(prompts) != len(test.prompt_ids):
            raise TestException(status_code=400, error_key="INVALID_PROMPT_IDS")

        for prompt in prompts:
            
            conversation_input = ConversationInput(
                llm_id=prompt.llm_id,
                user_input=test.user_input,
                prompt=prompt.prompt,
            )

            
            llm_response = await converse_with_llm(conversation_input, db)


            try:
                association = db.execute(
                    test_prompt_association.insert().values(
                        test_id=db_test.id,
                        prompt_id=prompt.id,
                        llm_response=llm_response["response"]["output"]["message"]["content"][0]["text"],
                        input_tokens=llm_response["response"]["usage"]["inputTokens"],
                        output_tokens=llm_response["response"]["usage"]["outputTokens"],
                        total_tokens=llm_response["response"]["usage"]["totalTokens"],
                        latency_ms=llm_response["response"]["metrics"]["latencyMs"],
                        prompt_tokens=gpt3_tokenizer.count_tokens(prompt.prompt),
                        user_input_tokens=gpt3_tokenizer.count_tokens(test.user_input),
                    )
                )
                print(f"Association inserted")
                db.flush()
            except Exception as e:
                raise LLMException(
                    status_code=500,
                    error_key="CONVERSATION_ERROR",
                    detail=f"Model invocation error: {str(e)}",
                )

        db.commit()
        db.refresh(db_test)
        

        return TestResponse.from_orm(db_test)
    except TestException as te:
        db.rollback()
        raise te
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred while creating the test: Database integrity error",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the test: {str(e)}",
        )


@router.post("/test/image", response_model=dict)
async def create_test(
    # test: TestCreate, db: Session = Depends(get_db)
    test_name: str = Form(...),
    prompt_ids: str = Form(...),
    input_type: str = Form(...),
    text_input: Optional[str] = Form(None),
    image_input: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    try:
        if image_input is None or image_input.file is None:
            raise HTTPException(status_code=400, detail="No image file provided")

        image_content = await image_input.read()

        if not image_content:
            raise HTTPException(status_code=400, detail="Image content is empty")

        # db_test = Test(test_name=test_name, image=image_input.file.read())
        # db.add(db_test)
        # db.flush()
        
        image_input.file.seek(0)
        image_data = image_input.file.read()
        db_test = Test(test_name=test_name, image=image_data)
        db.add(db_test)
        db.flush()

        try:
            if isinstance(prompt_ids, str):
                prompt_ids = json.loads(prompt_ids)
            prompt_ids = [uuid.UUID(id) for id in prompt_ids]
            prompts = db.query(Prompt).filter(Prompt.id.in_(prompt_ids)).all()
        except Exception as e:
            raise LLMException(
                status_code=500,
                error_key="CONVERSATION_ERROR",
                detail=f"Model invocation error: {str(e)}",
            )


        if len(prompts) != len(prompt_ids):
            raise TestException(status_code=400, error_key="INVALID_PROMPT_IDS")

        for prompt in prompts:
 
            img_conversation_input = ImageConversationInput(
                llm_id=prompt.llm_id,
                image=image_content,
                prompt=prompt.prompt,
            )
            llm_response = await converse_with_llm_image(img_conversation_input, db)

            
            try:
                association = db.execute(
                    test_prompt_association.insert().values(
                        test_id=db_test.id,
                        prompt_id=prompt.id,
                        llm_response=llm_response["output"]["message"][
                            "content"
                        ][0]["text"],
                        input_tokens=llm_response["usage"]["inputTokens"],
                        output_tokens=llm_response["usage"]["outputTokens"],
                        total_tokens=llm_response["usage"]["totalTokens"],
                        latency_ms=llm_response["metrics"]["latencyMs"],
                        prompt_tokens=gpt3_tokenizer.count_tokens(prompt.prompt),
                        # user_input_tokens=gpt3_tokenizer.count_tokens(text_input) if text_input else '0',
                    )
                )

                db.flush()
            except Exception as e:
                raise LLMException(
                    status_code=500,
                    error_key="CONVERSATION_ERROR",
                    detail=f"Model invocation error: {str(e)}",
                )
        

        
        db.commit()
        db.refresh(db_test)
        
        
        return {"message": "Test Image created successfully"}
    except TestException as te:
        db.rollback()
        raise te
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred while creating the test: Database integrity error",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the test: {str(e)}",
        )


@router.get("/test/{test_id}", response_model=TestResponse)
def read_test(test_id: str, db: Session = Depends(get_db)):
    try:
        # Validate UUID format
        try:
            test_uuid = uuid.UUID(test_id)
        except ValueError:
            raise TestException(
                status_code=400,
                error_key="INVALID_TEST_ID_FORMAT"
            )
        
        # Query the test using the validated UUID
        test = db.query(Test).filter(Test.id == test_uuid).first()
        if test is None:
            raise TestException(
                status_code=404,
                error_key="TEST_NOT_FOUND"
            )
            
        return TestResponse.from_orm(test)
        
    except TestException as te:
        raise te
    except Exception as e:
        raise TestException(
            status_code=500,
            error_key="INTERNAL_ERROR",
            detail=str(e)
        )


@router.put("/tests/{test_id}", response_model=TestResponse)
def update_test(test_id: str, test: TestUpdate, db: Session = Depends(get_db)):
    try:
        try:
            uuid.UUID(test_id)
        except ValueError:
            raise TestException(status_code=400, error_key="INVALID_TEST_ID_FORMAT")
        
        db_test = db.query(Test).filter(Test.id == uuid.UUID(test_id)).first()
        if db_test is None:
            raise TestException(status_code=404, error_key="TEST_NOT_FOUND")

        for key, value in test.dict(exclude_unset=True).items():
            setattr(db_test, key, value)

        db.commit()
        db.refresh(db_test)

        return TestResponse.from_orm(db_test)
    except ValueError:
        raise TestException(status_code=400, error_key="INVALID_TEST_ID_FORMAT")
    except sqlalchemy.exc.SQLAlchemyError as e:
        db.rollback()
        raise TestException(status_code=500, error_key="DATABASE_ERROR")
    except Exception as e:
        raise TestException(
            status_code=500,
            error_key="UNEXPECTED_ERROR",
            detail=f"{ErrorMessages.UNEXPECTED_ERROR}: {str(e)}",
        )


@router.delete("/test/{test_id}/prompt/{prompt_id}", response_model=dict)
def delete_test(test_id: str, prompt_id: str, db: Session = Depends(get_db)):
    try:
        try:
            uuid.UUID(test_id)
        except ValueError:
            raise TestException(status_code=400, error_key="INVALID_TEST_ID_FORMAT")
        
        db_test = db.query(Test).filter(Test.id == uuid.UUID(test_id)).first()
        if db_test is None:
            return {"message": "Test not found"}


        association_count = (
            db.query(test_prompt_association)
            .filter(test_prompt_association.c.test_id == db_test.id)
            .count()
        )


        if association_count == 1:
            db.query(test_prompt_association).filter(
                test_prompt_association.c.test_id == db_test.id
            ).delete()
            db.delete(db_test)
            message = "Test and its single association deleted successfully"
        elif association_count > 1:
            db.execute(
                delete(test_prompt_association)
                .where(test_prompt_association.c.test_id == db_test.id)
                .where(test_prompt_association.c.prompt_id == uuid.UUID(prompt_id))
            )
            message = (
                "One association deleted, test retained due to multiple associations"
            )
        else:
            db.delete(db_test)
            message = "Test deleted successfully (no associations found)"

        db.commit()
        return {"message": message}

    except ValueError:
        raise TestException(status_code=400, error_key="INVALID_TEST_ID_FORMAT")
    except sqlalchemy.exc.SQLAlchemyError as e:
        db.rollback()
        raise TestException(status_code=500, error_key="DATABASE_ERROR")
    except Exception as e:
        raise TestException(
            status_code=500,
            error_key="UNEXPECTED_ERROR",
            detail=f"{ErrorMessages.UNEXPECTED_ERROR}: {str(e)}",
        )


@router.get("/tests/{prompt_id}", response_model=List[TestResponse])
def list_tests(prompt_id: str, db: Session = Depends(get_db)):
    try:
        try:
            uuid.UUID(prompt_id)
        except ValueError:
            raise TestException(status_code=400, error_key="INVALID_PROMPT_ID_FORMAT")
        
        uuid_prompt_id = uuid.UUID(prompt_id)
        tests = (
            db.query(Test)
            .join(test_prompt_association)
            .filter(test_prompt_association.c.prompt_id == uuid_prompt_id)
            .all()
        )

        test_responses = []
        for test in tests:
            association = (
                db.query(test_prompt_association)
                .filter(
                    test_prompt_association.c.test_id == test.id,
                    test_prompt_association.c.prompt_id == uuid_prompt_id,
                )
                .first()
            )
            
            llm_response = association.llm_response if association else None
            if test.image:
                image = base64.b64encode(test.image).decode("utf-8")
            else:
                image = None
            
            test_response = TestResponse(
                id=test.id,
                test_name=test.test_name,
                user_input=test.user_input,
                creation_date=test.creation_date,
                llm_response=llm_response,
                input_tokens=association.input_tokens,
                output_tokens=association.output_tokens,
                total_tokens=association.total_tokens,
                latency_ms=association.latency_ms,
                prompt_tokens=association.prompt_tokens,
                user_input_tokens=association.user_input_tokens,
                image=image,
            )
            test_responses.append(test_response)

        return test_responses
    except ValueError:
        raise TestException(status_code=400, error_key="INVALID_PROMPT_ID_FORMAT")
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise TestException(status_code=500, error_key="DATABASE_ERROR")
    except Exception as e:
        raise TestException(
            status_code=500,
            error_key="UNEXPECTED_ERROR",
            detail=f"{ErrorMessages.UNEXPECTED_ERROR}: {str(e)}",
        )
