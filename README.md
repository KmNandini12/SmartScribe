# SmartScribe: Enterprise Document Intelligence Platform

SmartScribe is an enterprise-grade, asynchronous document intelligence platform that ingests, parses, and extracts verifiable takeaways from meeting transcripts. It replaces generative LLM APIs with a self-hosted, deterministic semantic processing pipeline to eliminate hallucinations and data leakage.

## Core Architecture
- **API Gateway:** High-concurrency FastAPI service handling file uploads and status queries.
- **Message Broker:** Redis 7 managing async task queues and payload SHA-256 deduplication.
- **Task Worker Pool:** Celery 5 running local dense vector embeddings (`sentence-transformers`) and deterministic K-Means clustering.
- **Database:** PostgreSQL 16 storing document vectors via JSONB fields.
- **Frontend:** Next.js & React UI with an interactive split-pane verification inspector.

## Resiliency & Engineering
- **Sub-150ms API Latency:** Offloading compute to Celery allows the API to return HTTP 202 Accepted instantly.
- **Singleton ML Loader:** Prevents Worker Out-of-Memory (OOM) crashes.
- **Zero-Data Loss:** `task_acks_late` and a cron zombie sweeper ensure dropped jobs are safely retried.

## Quickstart (Docker Compose)
Deploy the entire 5-tier architecture locally with one command:
```bash
docker-compose up --build -d
```
Access the dashboard at `http://localhost:3000`.

## Benchmarks
Load tested with **k6** simulating 50 concurrent enterprise transcript uploads:
- `http_req_duration`: p(95) < 150ms
- `http_req_failed`: 0.00% 
