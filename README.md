# Prompt Fuse (v0.1.0 - beta)

Prompt Fuse is an open-source tool for managing, testing, and automatically versioning LLM prompts. With Prompt Fuse developers can easily organize prompts, track versions, and experiment with individual prompt tests, all through a streamlined interface.

> **Note**: This project is currently in beta version and under active development.

## Features

- AWS-based LLM integration and management
- Prompt version tracking
- Prompt testing interface
    - Text
    - Image

## Tech Stack

### Backend
- Python
- FastAPI
- PostgreSQL

### Frontend
- React
- TypeScript
- HTML
- CSS

## Getting Started

### Docker Installation

1. Install [Docker](https://www.docker.com/products/docker-desktop/)
2. Run the following command:

```bash
docker-compose up --build
```

### Local Installation

**Frontend:**
```bash
cd frontend
npm install
npm run start
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Roadmap (v1.0.0)

### Core Features
- User Authentication & Authorization
- Additional LLM Provider Integration
- Function Calling Support
- Prompt Comparison Tools

### Developer Experience
- Comprehensive Documentation
- Testing Framework Implementation
- Enhanced Logging System
- Web Based Interface

### Infrastructure
- Performance Optimizations
- Scalability Improvements

### User Experience
- UI/UX Enhancements
- Advanced Prompt Management Features
- Interactive Dashboard Improvements