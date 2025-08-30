# AI CREAT – Backend (FastAPI + Celery)

Production-ready backend for asset processing: authentication, projects/assets upload & analysis, AI generation (provider-agnostic), manual edits, content moderation, and admin configuration.

## Tech Stack
- FastAPI (Python 3.11), Pydantic v1  
- PostgreSQL + SQLAlchemy + Alembic  
- Celery + RabbitMQ, Redis (cache/broker auxiliary)  
- Local file storage (default): `/data/uploads`, `/data/generated`  
- Provider-agnostic AI layer (OpenAI, Gemini, Mock)  

## Quick Start
### 0) Prereqs
- Docker & Docker Compose  
- Git  

### 1) Clone & configure env
```bash
git clone <this-repo> ai-creat-backend
cd ai-creat-backend
cp .env.example .env
