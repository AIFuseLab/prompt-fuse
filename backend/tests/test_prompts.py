import pytest
from uuid import UUID, uuid4
import sys
sys.path.append("..")
from app.models.prompt import Prompt
from app.models.llm import LLM
from app.schemas.prompt import PromptCreate, PromptUpdate

@pytest.fixture
def sample_llm(test_db):
    llm = LLM(id=uuid4(), name="test-llm")
    test_db.add(llm)
    test_db.commit()
    return llm

@pytest.fixture
def sample_prompt(test_db, sample_llm):
    prompt = Prompt(
        id=uuid4(),
        name="test-prompt",
        prompt="This is a test prompt",
        notes="Test notes",
        version=1.0,
        llm_id=sample_llm.id,
        prompt_template_id=uuid4()
    )
    test_db.add(prompt)
    test_db.commit()
    return prompt

def test_create_prompt(client, test_db, sample_llm):
    prompt_data = {
        "name": "new-prompt",
        "prompt": "Test prompt content",
        "notes": "Test notes",
        "version": 1.0,
        "llm_id": str(sample_llm.id),
        "prompt_template_id": str(uuid4())
    }
    
    response = client.post("/api/v1/prompt", json=prompt_data)
    assert response.status_code == 200
    assert response.json()["name"] == prompt_data["name"]
    assert response.json()["prompt"] == prompt_data["prompt"]

def test_create_duplicate_prompt(client, sample_prompt):
    prompt_data = {
        "name": sample_prompt.name,
        "prompt": "Different prompt content",
        "notes": "Different notes",
        "version": 1.0,
        "llm_id": str(sample_prompt.llm_id),
        "prompt_template_id": str(sample_prompt.prompt_template_id)
    }
        
    response = client.post("/api/v1/prompt", json=prompt_data)
    
    assert response.status_code == 400
    assert "PROMPT_NAME_EXISTS" in str(response.json())

def test_read_prompt(client, sample_prompt):
    response = client.get(f"/api/v1/prompt/{sample_prompt.id}")
    assert response.status_code == 200
    assert response.json()["name"] == sample_prompt.name
    assert response.json()["prompt"] == sample_prompt.prompt

def test_read_nonexistent_prompt(client):
    response = client.get(f"/api/v1/prompt/{uuid4()}")
    assert response.status_code == 404
    assert "PROMPT_NOT_FOUND" in str(response.json())

def test_update_prompt(client, sample_prompt):
    update_data = {
        "prompt": "Updated prompt content",
        "notes": "Updated notes"
    }
    
    response = client.put(f"/api/v1/prompt/{sample_prompt.id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["prompt"] == update_data["prompt"]
    assert response.json()["notes"] == update_data["notes"]
    assert float(response.json()["version"]) == 2.0  # Version should be incremented

def test_update_nonexistent_prompt(client):
    update_data = {
        "prompt": "Updated prompt content",
        "notes": "Updated notes"
    }
    
    response = client.put(f"/api/v1/prompt/{uuid4()}", json=update_data)
    assert response.status_code == 404
    assert "PROMPT_NOT_FOUND" in str(response.json())

def test_list_prompts(client, sample_prompt):
    response = client.get(f"/api/v1/prompts/{sample_prompt.prompt_template_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1
    assert response.json()[0]["name"] == sample_prompt.name

def test_delete_prompt(client, sample_prompt):
    response = client.delete(f"/api/v1/prompt/{sample_prompt.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Prompt Deleted Successfully"

    # Verify prompt is deleted
    deleted_check = client.get(f"/api/v1/prompt/{sample_prompt.id}")
    assert deleted_check.status_code == 404

def test_delete_nonexistent_prompt(client):
    response = client.delete(f"/api/v1/prompt/{uuid4()}")
    assert response.status_code == 404
    assert "PROMPT_NOT_FOUND" in str(response.json())

def test_invalid_uuid_format(client):
    response = client.get("/api/v1/prompt/invalid-uuid")
    assert response.status_code == 400
    assert "INVALID_PROMPT_ID_FORMAT" in str(response.json())
    
# Test Delete Prompt Template & It's associated Prompts
