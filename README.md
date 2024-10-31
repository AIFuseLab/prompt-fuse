# Prompt Fuse
Prompt Fuse is an open-source tool for managing, testing, and automatically versioning LLM prompts. With Prompt Fuse developers can easily organize prompts, track versions, and experiment with individual prompt tests, all through a streamlined interface.


# IMPORTANT NOTE
This project is still under development. This is the first beta version so you might find some bugs. 


# Explaination
- This project is a tool for managing, testing, and automatically versioning LLM prompts.
- It is designed to be used with AWS based LLMs.

# Current Features
- Only Support AWS Based LLMs


# Todo
- Dockerization

# Roadmap
- UI/UX Improvements
- Function Calling
- Add More LLM Providers
- User Authentication
- Testing
- Documentation
- Prompt Comparison
- Cloud Option
- Logging


# Tech Stack
## Backend
- Python
- FastAPI
- PostgreSQL
## Frontend
- Html
- Css
- Typescript
- React



# Run App Using Docker
1. Install [Docker](https://www.docker.com/products/docker-desktop/)
2. Run
```
docker compose up
```


# Run App Using Local
Frontend:
```
cd frontend
npm install
npm run start
```

Backend:
```
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```