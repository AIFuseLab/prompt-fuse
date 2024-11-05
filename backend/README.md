# Prompt Manager

# Run the backend
uvicorn app.main:app --reload


# Remove Existing Database Volume
docker-compose down -v


# Remove Database Container and Volume
docker-compose down -v

# Remove all unused Docker objects
docker system prune -a --volumes


# Test Commands

#### Run all tests
pytest

#### Run tests with detailed output
pytest -v

#### Run tests with print statements
pytest -s

#### Run a specific test file
pytest tests/test_projects.py

#### Run a specific test function
pytest tests/test_projects.py::test_create_project_success