# Prompt Manager

# Run the backend
uvicorn app.main:app --reload


# Remove Existing Database Volume
docker-compose down -v


# Remove Database Container and Volume
docker-compose down -v

# Remove all unused Docker objects
docker system prune -a --volumes