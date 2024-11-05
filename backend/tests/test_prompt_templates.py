import pytest
from uuid import UUID, uuid4
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime
import sys
sys.path.append("..")
from app.models.prompt_template import PromptTemplate

test_template_data = {
    "name": "Test Template",
    "description": "Test description",
    "project_id": str(uuid4()),
    "creation_date": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
    "number_of_prompts": 0
}

@pytest.fixture
def sample_template(test_db: Session):
    template = PromptTemplate(
        id=uuid4(),
        name="Sample Template",
        description="Sample description",
        project_id=uuid4(),
        creation_date=datetime.now(),
        updated_at=datetime.now(),
        number_of_prompts=0,
    )
    
    test_db.add(template)
    test_db.commit()
    test_db.refresh(template)
    
    yield template
    
    # Cleanup after test
    test_db.delete(template)
    test_db.commit()

def test_create_prompt_template(client: TestClient):    
    response = client.post("/api/v1/prompt-templates", json=test_template_data)

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == test_template_data["name"]
    assert data["description"] == test_template_data["description"]
    assert "id" in data

def test_create_duplicate_template(client: TestClient):
    # First, create the initial template
    first_response = client.post("/api/v1/prompt-templates", json=test_template_data)
    assert first_response.status_code == 200

    response = client.post("/api/v1/prompt-templates", json=test_template_data)
    
    assert response.status_code == 400
    assert "error_key" in response.json()
    assert response.json()["error_key"] == "PROMPT_TEMPLATE_NAME_EXISTS"

def test_read_prompt_template(client: TestClient, sample_template: PromptTemplate):
    response = client.get(f"/api/v1/prompt-template/{sample_template.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_template.name
    assert data["description"] == sample_template.description

def test_read_nonexistent_template(client: TestClient):
    response = client.get(f"/api/v1/prompt-template/{uuid4()}")
    assert response.status_code == 404
    assert response.json()["error_key"] == "PROMPT_TEMPLATE_NOT_FOUND"

def test_update_prompt_template(client: TestClient, sample_template: PromptTemplate):
    update_data = {
        "name": "Updated Template Name",
        "description": "Updated description"
    }
    response = client.put(
        f"/api/v1/prompt-template/{sample_template.id}",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]

def test_list_prompt_templates(client: TestClient, sample_template: PromptTemplate):
    project_id = str(sample_template.project_id)
    
    response = client.get(f"/api/v1/prompt-templates/{project_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["id"] == str(sample_template.id)

def test_delete_prompt_template(client: TestClient, sample_template: PromptTemplate):
    response = client.delete(f"/api/v1/prompt-template/{sample_template.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Prompt Template Deleted Successfully"

    # Verify template is deleted
    response = client.get(f"/api/v1/prompt-template/{sample_template.id}")
    assert response.status_code == 404


def test_delete_nonexistent_template(client: TestClient):
    response = client.delete(f"/api/v1/prompt-template/{uuid4()}")
    assert response.status_code == 404
    assert response.json()["error_key"] == "PROMPT_TEMPLATE_NOT_FOUND"


def test_delete_invalid_template_id(client: TestClient):
    response = client.delete(f"/api/v1/prompt-template/{'invalid_id'}")
    assert response.status_code == 400
    assert response.json()["error_key"] == "INVALID_PROMPT_TEMPLATE_ID_FORMAT"

def test_create_template_with_empty_name(client: TestClient):
    response = client.post("/api/v1/prompt-templates", json={"name": "", "description": "Test description", "project_id": str(uuid4())})
    assert response.status_code == 400
    assert response.json()["error_key"] == "INVALID_PROMPT_TEMPLATE_NAME"


def test_update_template_with_empty_name(client: TestClient, sample_template: PromptTemplate):
    response = client.put(f"/api/v1/prompt-template/{sample_template.id}", json={"name": "", "description": "Test description"})
    assert response.status_code == 400
    assert response.json()["error_key"] == "INVALID_PROMPT_TEMPLATE_NAME"
    
def test_update_template_with_empty_description(client: TestClient, sample_template: PromptTemplate):
    response = client.put(f"/api/v1/prompt-template/{sample_template.id}", json={"name": "Test Template", "description": ""})
    assert response.status_code == 200

def test_update_template_with_duplicate_name(client: TestClient, sample_template: PromptTemplate):
    # create a new template with the same name
    first_response = client.post("/api/v1/prompt-templates", json={"name": "Duplicate Template", "description": "Test description", "project_id": str(uuid4())})
    assert first_response.status_code == 200
    
    second_response = client.post("/api/v1/prompt-templates", json={"name": "Duplicate Template Two", "description": "Test description", "project_id": str(uuid4())})
    assert second_response.status_code == 200
    
    response = client.put(f"/api/v1/prompt-template/{first_response.json()['id']}", json={"name": "Duplicate Template Two", "description": "Test description"})
    assert response.status_code == 400
    assert response.json()["error_key"] == "PROMPT_TEMPLATE_NAME_EXISTS"
