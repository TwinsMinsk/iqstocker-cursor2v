# IQStocker v2.0 - AI Agent Implementation Plan

## 📋 Overview

This document provides a step-by-step implementation plan for AI agents (especially in Cursor IDE) to build IQStocker v2.0.

## 10 Implementation Phases

### Phase 1: Setup & Configuration
- Run scaffold.sh to create project structure
- Install Poetry dependencies
- Configure .env file
- Initialize Alembic migrations

### Phase 2: Database Layer  
- Copy models.py
- Create all repositories (analytics, themes, referrals, payments)
- Set up connection pooling

### Phase 3: Bot Handlers
- Implement FSM states
- Create keyboard factories  
- Write handlers for all commands using lexicon_ru.py

### Phase 4: Analytics Core
- CSV processor
- KPI calculator
- Report generator

### Phase 5: Background Workers
- ARQ tasks setup
- CSV processing worker
- Periodic tasks

### Phase 6: Referral System
- IQ Points system (1 point per PRO/ULTRA purchase)
- Point accrual logic (track referral purchases)
- Point exchange system (5 exchange options)
- Statistics and balance tracking

### Phase 7: Payment Integration
- Tribute.tg API client
- Webhook handler
- Payment processing

### Phase 8: Admin Panel
- FastAPI views
- CRUD operations
- Dashboard
- Broadcasting

### Phase 9: Testing & Quality
- Unit tests
- Integration tests
- Mypy strict mode
- Ruff linting

### Phase 10: Deployment
- Railway configuration
- Environment variables
- Health checks
- Monitoring

Refer to tid_v2.md for detailed specifications.
