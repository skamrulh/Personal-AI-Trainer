# PT Coach — Local MVP (Complete Build)

This repository contains a full local MVP for an Intelligent Physical Therapy & Form Coach:
- React frontend using MoveNet (client-side) for pose detection
- Flask backend for session management, form analysis, and OpenAI integration
- Redis for session/frame storage and caching
- Docker + docker-compose for local development
- Terraform infra skeleton for AWS deployment (ECS, RDS, ElastiCache, S3)
- GitHub Actions skeleton for CI/CD

## Quickstart (Local, Docker)

1. Copy `.env.example` to `.env` and set `OPENAI_API_KEY`.
2. Build & start:
```bash
docker compose up --build
