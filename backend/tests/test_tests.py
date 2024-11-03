import pytest
from fastapi.testclient import TestClient
import uuid
from app.utils.exceptions.errors import get_error_message
import io


# def test_read_test_success(client):
    # First create an LLM
    # llm_response = client.post(
    #     "/api/v1/llms",
    #     json={
    #         "name": "Test Claude",
    #         "llm_model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
    #         "access_key": "test_access_key",
    #         "secret_access_key": "test_secret_key",
    #         "aws_region": "us-east-1"
    #     }
    # )
    # print("--llm--")
    # print(llm_response.json())
    # print("----")
    
    # llm_id = str(llm_response.json()["id"])

    # # Then create a prompt using the LLM's ID
    # prompt_response = client.post(
    #     "/api/v1/prompt",
    #     json={
    #         "prompt": "Test prompt",
    #         "name": "Test Prompt",
    #         "llm_id": llm_id
    #     }
    # )
    # print("--prompt--")
    # print(prompt_response.json())
    # print("----")
    # prompt_id = str(prompt_response.json()["id"])

    # create_response = client.post(
    #     "/api/v1/test/text",
    #     json={
    #         "test_name": "Test to Read",
    #         "user_input": "Sample input",
    #         "prompt_ids": [prompt_id]
    #     }
    # )
    # print("--create--")
    # print(create_response.json())
    # print("----")
    # test_id = str(create_response.json()["id"])
    
    # # Read the test
    # response = client.get(f"/api/v1/test/{test_id}")
    
    # assert response.status_code == 200
    # data = response.json()
    # assert data["test_name"] == "Test to Read"
    # assert data["user_input"] == "Sample input"
    
# def test_update_test_success(client):
#     # First create an LLM
#     llm_response = client.post(
#         "/api/v1/llms",
#         json={
#             "name": "Test Claude",
#             "llm_model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
#             "access_key": "test_access_key",
#             "secret_access_key": "test_secret_key",
#             "aws_region": "us-east-1"
#         }
#     )
#     print("--llm--")
#     print(llm_response.json())
#     print("----")
    
#     llm_id = str(llm_response.json()["id"])
#     # First create a test
#     prompt_response = client.post(
#         "/api/v1/prompt",
#         json={"prompt": "Test prompt", "name": "Test Prompt", "llm_id": llm_id}
#     )
#     print("--prompt--")
#     print(prompt_response.json())
#     print("----")
#     prompt_id = str(prompt_response.json()["id"])

#     create_response = client.post(
#         "/api/v1/test/text",
#         json={
#             "test_name": "Test to Update",
#             "user_input": "Original input",
#             "prompt_ids": [prompt_id]
#         }
#     )
#     print("--create--")
#     print(create_response.json())
#     print("----")
#     test_id = str(create_response.json()["id"])
    
#     response = client.put(
#         f"/api/v1/tests/{test_id}",
#         json={
#             "test_name": "Updated Test Name",
#             "user_input": "Updated input"
#         }
#     )
#     print("--update--")
#     print(response.json())
#     print("----")
    
#     assert response.status_code == 200
#     data = response.json()
#     assert data["test_name"] == "Updated Test Name"
#     assert data["user_input"] == "Updated input"


# def test_delete_test_success(client):
#     # First create a test and prompt
#     prompt_response = client.post(
#         "/api/v1/prompt",
#         json={"prompt": "Test prompt", "name": "Test Prompt", "llm_id": "claude-3-opus-20240229"}
#     )
    
#     prompt_id = prompt_response.json()["id"]
    
#     create_response = client.post(
#         "/api/v1/test/text",
#         json={
#             "test_name": "Test to Delete",
#             "user_input": "Delete me",
#             "prompt_ids": [prompt_id]
#         }
#     )
#     test_id = create_response.json()["id"]
    
#     response = client.delete(f"/api/v1/test/{test_id}/prompt/{prompt_id}")
    
#     assert response.status_code == 200
#     data = response.json()
#     assert "successfully" in data["message"]

# def test_list_tests_by_prompt(client):
#     # First create a prompt and multiple tests
#     prompt_response = client.post(
#         "/api/v1/prompt",
#         json={"prompt": "Test prompt", "name": "Test Prompt", "llm_id": "claude-3-opus-20240229"}
#     )
#     prompt_id = prompt_response.json()["id"]

#     # Create two tests with the same prompt
#     client.post(
#         "/api/v1/test/text",
#         json={
#             "test_name": "Test 1",
#             "user_input": "Input 1",
#             "prompt_ids": [prompt_id]
#         }
#     )
    
#     client.post(
#         "/api/v1/test/text",
#         json={
#             "test_name": "Test 2",
#             "user_input": "Input 2",
#             "prompt_ids": [prompt_id]
#         }
#     )
    
#     response = client.get(f"/api/v1/tests/{prompt_id}")
    
#     assert response.status_code == 200
#     data = response.json()
#     assert len(data) == 2
#     assert any(test["test_name"] == "Test 1" for test in data)
#     assert any(test["test_name"] == "Test 2" for test in data)

def test_create_test_invalid_prompt_ids(client):
    random_id = str(uuid.uuid4())
    response = client.post(
        "/api/v1/test/text",
        json={
            "test_name": "Invalid Test",
            "user_input": "Test input",
            "prompt_ids": [random_id]
        }
    )
    
    assert response.status_code == 400
    assert "INVALID_PROMPT_IDS" in response.text
    
def test_read_test_not_found(client):
    random_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/test/{random_id}")
    
    assert response.status_code == 404
    error_response = response.json()
    assert error_response["error_key"] == "TEST_NOT_FOUND"
    
# def test_create_text_test_success(client):
#     # First create a prompt to use
#     prompt_response = client.post(
#         "/api/v1/prompt",
#         json={"prompt": "Test prompt", "name": "Test Prompt", "llm_id": "claude-3-opus-20240229"}
#     )
#     prompt_id = prompt_response.json()["id"]

#     response = client.post(
#         "/api/v1/test/text",
#         json={
#             "test_name": "Test Case 1",
#             "user_input": "Sample user input",
#             "prompt_ids": [prompt_id]
#         }
#     )
    
#     assert response.status_code == 200
#     data = response.json()
#     assert data["test_name"] == "Test Case 1"
#     assert data["user_input"] == "Sample user input"
#     assert "id" in data

# def test_create_image_test_success(client):
#     # First create a prompt to use
#     prompt_response = client.post(
#         "/api/v1/prompt",
#         json={"prompt": "Test prompt", "name": "Test Prompt", "llm_id": "claude-3-opus-20240229"}
#     )
#     prompt_id = prompt_response.json()["id"]

#     # Create a dummy image file
#     image_content = b"fake image content"
#     image = io.BytesIO(image_content)

#     response = client.post(
#         "/api/v1/test/image",
#         data={
#             "test_name": "Image Test Case",
#             "prompt_ids": f'["{prompt_id}"]',
#             "input_type": "image",
#         },
#         files={"image_input": ("test.jpg", image, "image/jpeg")}
#     )
    
#     assert response.status_code == 200
#     assert response.json()["message"] == "Test Image created successfully"
