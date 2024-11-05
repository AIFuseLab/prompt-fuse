import pytest
from uuid import UUID, uuid4
import sys
sys.path.append("..")
from app.models.llm import LLM

# import boto3
# from botocore.exceptions import ClientError
# import json
# from unittest.mock import MagicMock, patch
# import pytest

@pytest.fixture
def sample_llm(test_db):
    llm = LLM(
        id=uuid4(),
        name="test-llm",
        description="Test Description",
        access_key="test-access-key",
        secret_access_key="test-secret-key",
        aws_region="us-west-2",
        llm_model_id="anthropic.claude-v2"
    )
    test_db.add(llm)
    test_db.commit()
    return llm

def test_create_llm(client):
    llm_data = {
        "name": "new-llm",
        "description": "Test Description",
        "access_key": "test-access-key",
        "secret_access_key": "test-secret-key",
        "aws_region": "us-west-2",
        "llm_model_id": "anthropic.claude-v2"
    }
    
    response = client.post("/api/v1/llms", json=llm_data)
    assert response.status_code == 200
    assert response.json()["name"] == llm_data["name"]
    assert response.json()["description"] == llm_data["description"]

def test_create_duplicate_llm(client, sample_llm):
    llm_data = {
        "name": sample_llm.name,
        "description": "Different description",
        "access_key": "different-key",
        "secret_access_key": "different-secret",
        "aws_region": "us-east-1",
        "llm_model_id": "anthropic.claude-v2"
    }
    
    response = client.post("/api/v1/llms", json=llm_data)
    
    assert response.status_code == 400
    
    response_data = response.json()
    assert "detail" in response_data
    assert response_data["detail"]["error_key"] == "LLM_NAME_EXISTS"

def test_read_llm(client, sample_llm):
    response = client.get(f"/api/v1/llm/{sample_llm.id}")
    assert response.status_code == 200
    assert response.json()["name"] == sample_llm.name
    assert response.json()["description"] == sample_llm.description

def test_read_nonexistent_llm(client):
    response = client.get(f"/api/v1/llm/{uuid4()}")
    assert response.status_code == 404
    assert "LLM_NOT_FOUND" in str(response.json())

def test_update_llm(client, sample_llm):
    update_data = {
        "name": "updated-llm",
        "description": "Updated description",
        "aws_region": "us-east-1"
    }
    
    response = client.put(f"/api/v1/llm/{sample_llm.id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["description"] == update_data["description"]
    assert response.json()["name"] == update_data["name"]

def test_update_nonexistent_llm(client):
    update_data = {
        "description": "Updated description",
        "aws_region": "us-east-1"
    }
    
    response = client.put(f"/api/v1/llm/{uuid4()}", json=update_data)
    assert response.status_code == 404
    assert "LLM_NOT_FOUND" in str(response.json())

def test_list_llms(client, sample_llm):
    response = client.get("/api/v1/llms")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1
    assert response.json()[0]["name"] == sample_llm.name

def test_delete_llm(client, sample_llm):
    response = client.delete(f"/api/v1/llm/{sample_llm.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "LLM Deleted Successfully"

    # Verify llm is deleted
    deleted_check = client.get(f"/api/v1/llm/{sample_llm.id}")
    assert deleted_check.status_code == 404

def test_delete_nonexistent_llm(client):
    response = client.delete(f"/api/v1/llm/{uuid4()}")
    assert response.status_code == 404
    
    response_data = response.json()
    assert "error_key" in response_data
    assert response_data["error_key"] == "LLM_NOT_FOUND"

def test_invalid_uuid_format(client):
    response = client.get("/api/v1/llm/invalid-uuid")
    assert response.status_code == 400
    assert "INVALID_LLM_ID_FORMAT" in str(response.json())

# def test_converse_with_llm(client, sample_llm):
#     conversation_data = {
#         "llm_id": str(sample_llm.id),
#         "user_input": "Hello",
#         "prompt": "You are a helpful assistant",
#         "temperature": 0.7,
#         "max_tokens": 100,
#         "top_p": 0.9
#     }
    
#     response = client.post("/api/v1/llm/converse", json=conversation_data)
#     assert response.status_code == 200
#     assert "response" in response.json()

# @pytest.mark.asyncio
# @patch('boto3.client')
# async def test_converse_with_llm(mock_boto3_client, client, sample_llm):
#     # Mock AWS Bedrock response
#     mock_response = {
#         'body': MagicMock()
#     }
#     mock_response['body'].read.return_value = json.dumps({
#         'completion': 'This is a test response'
#     })
    
#     mock_bedrock = MagicMock()
#     mock_bedrock.invoke_model.return_value = mock_response
#     mock_boto3_client.return_value = mock_bedrock

#     conversation_data = {
#         "llm_id": str(sample_llm.id),
#         "user_input": "Hello",
#         "prompt": "You are a helpful assistant",
#         "temperature": 0.7,
#         "max_tokens": 100,
#         "top_p": 0.9
#     }
    
#     response = client.post("/api/v1/llm/converse", json=conversation_data)
#     assert response.status_code == 200
    
#     response_data = response.json()
#     assert "response" in response_data
#     assert isinstance(response_data["response"], str)

#     # Verify AWS Bedrock was called correctly
#     mock_bedrock.invoke_model.assert_called_once()
    
# def test_converse_with_nonexistent_llm(client):
#     conversation_data = {
#         "llm_id": str(uuid4()),
#         "user_input": "Hello",
#         "prompt": "You are a helpful assistant",
#         "temperature": 0.7,
#         "max_tokens": 100,
#         "top_p": 0.9
#     }
    
#     response = client.post("/api/v1/llm/converse", json=conversation_data)
#     assert response.status_code == 404
#     assert "LLM_NOT_FOUND" in str(response.json())

# @pytest.mark.asyncio
# async def test_converse_with_nonexistent_llm(client):
#     conversation_data = {
#         "llm_id": str(uuid4()),
#         "user_input": "Hello",
#         "prompt": "You are a helpful assistant",
#         "temperature": 0.7,
#         "max_tokens": 100,
#         "top_p": 0.9
#     }
    
#     response = client.post("/api/v1/llm/converse", json=conversation_data)
#     assert response.status_code == 404
    
#     response_data = response.json()
#     assert "error_key" in response_data
#     assert response_data["error_key"] == "LLM_NOT_FOUND"