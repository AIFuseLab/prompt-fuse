import pytest
from fastapi.testclient import TestClient
import uuid
from app.utils.exceptions.errors import get_error_message

def test_create_project_success(client):
    response = client.post(
        "/api/v1/project",
        json={"name": "Test Project", "description": "Test Description"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "Test Description"
    assert "id" in data
    
def test_create_project_success_no_description(client):
    response = client.post(
        "/api/v1/project",
        json={"name": "Test Project", "description": ""}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == ""
    assert "id" in data

def test_create_project_duplicate_name(client):
    # Create first project
    client.post(
        "/api/v1/project",
        json={"name": "Testing Project API", "description": "Test Description"}
    )
    
    # Try to create project with same name
    response = client.post(
        "/api/v1/project",
        json={"name": "Testing Project API", "description": "Test Description"}
    )
    assert response.status_code == 400
    response_data = response.json()
    assert response_data["error_key"] == "PROJECT_NAME_EXISTS"
    assert get_error_message("PROJECT_NAME_EXISTS") in response_data["message"]

def test_get_project_success(client):
    # Create a project first
    create_response = client.post(
        "/api/v1/project",
        json={"name": "Test Project Two", "description": "test"}
    )
    project_id = create_response.json()["id"]
    
    response = client.get(f"/api/v1/project/{project_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project Two"
    assert data["description"] == "test"

def test_get_project_not_found(client):
    random_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/project/{random_id}")
    assert response.status_code == 404
    assert "PROJECT_NOT_FOUND" in response.text

def test_update_project_success(client):
    # Create a project first
    create_response = client.post(
        "/api/v1/project",
        json={"name": "Test Project", "description": "Test Description"}
    )
    project_id = create_response.json()["id"]
    
    # Update the project
    response = client.put(
        f"/api/v1/project/{project_id}",
        json={"name": "Updated Project", "description": "Updated Description"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Project"
    assert data["description"] == "Updated Description"
    
def test_update_project_duplicate_name(client):
    # Create first project
    first_project = client.post(
        "/api/v1/project",
        json={"name": "Test Project", "description": "Test Description"}
    )
    first_project_id = first_project.json()["id"]
    
    # Create second project
    second_project = client.post(
        "/api/v1/project",
        json={"name": "Test Project Two", "description": "Test Description"}
    )
    
    # Try to update first project with second project's name
    update_response = client.put(
        f"/api/v1/project/{first_project_id}",
        json={"name": "Test Project Two", "description": "Updated Description"}
    )

    
    assert update_response.status_code == 400
    response_data = update_response.json()
    assert response_data["error_key"] == "PROJECT_NAME_EXISTS"
    assert get_error_message("PROJECT_NAME_EXISTS") in response_data["message"]

def test_delete_project_success(client):
    # Create a project first
    create_response = client.post(
        "/api/v1/project",
        json={"name": "Test Project", "description": "Test Description"}
    )
    project_id = create_response.json()["id"]
    
    # Delete the project
    response = client.delete(f"/api/v1/project/{project_id}")
    assert response.status_code == 200
    
    # Verify project is deleted
    get_response = client.get(f"/api/v1/project/{project_id}")
    assert get_response.status_code == 404
    
def test_delete_project_not_found(client):
    random_id = str(uuid.uuid4())
    response = client.delete(f"/api/v1/project/{random_id}")
    assert response.status_code == 404
    
def test_update_project_empty_name(client):
    create_response = client.post(
        "/api/v1/project",
        json={"name": "Test Project", "description": "Test Description"}
    )
    project_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/project/{project_id}",
        json={"name": "", "description": "Updated Description"}
    )
    
    assert response.status_code == 400
    response_data = response.json()
    assert response_data["error_key"] == "PROJECT_NAME_EMPTY"
    assert get_error_message("PROJECT_NAME_EMPTY") in response_data["message"]
    
    
def test_create_project_empty_name(client):
    response = client.post(
        "/api/v1/project",
        json={"name": "", "description": "Test Description"}
    )
    assert response.status_code == 400
    response_data = response.json()
    assert response_data["error_key"] == "PROJECT_NAME_EMPTY"
    assert get_error_message("PROJECT_NAME_EMPTY") in response_data["message"]
    

# Test Delete Entire Project