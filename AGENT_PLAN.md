# IQStocker v2.0 - AI Agent Implementation Plan

## 📋 Overview

This document provides a step-by-step implementation plan for AI agents (especially in Cursor IDE) to build IQStocker v2.0.

## 🔌 Available MCP Servers

The following MCP (Model Context Protocol) servers are configured and should be used when relevant:

1. **aiogram Docs** (`mcp_aiogram_Docs_*`)
   - **Use when**: Working with aiogram handlers, FSM states, keyboards, or any aiogram API
   - **Functions**: `search_aiogram_documentation()`, `fetch_aiogram_documentation()`, `search_aiogram_code()`
   - **Best for**: Finding correct aiogram patterns, API usage, FSM examples

2. **Supabase** (`mcp_supabase_*`)
   - **Use when**: Database operations, migrations, schema changes, querying data
   - **Functions**: `list_tables()`, `execute_sql()`, `apply_migration()`, `list_migrations()`
   - **Best for**: Database management, testing queries, checking schema

3. **Railway** (`mcp_Railway_*`)
   - **Use when**: Deployment, checking logs, managing services, environment variables
   - **Functions**: `deploy()`, `get-logs()`, `list-services()`, `set-variables()`
   - **Best for**: Deployment operations, troubleshooting production issues

4. **GitHub** (`mcp_github_*`)
   - **Use when**: Searching code examples, creating PRs, reading documentation, finding similar implementations
   - **Functions**: `search_code()`, `search_repositories()`, `get_file_contents()`, `create_pull_request()`
   - **Best for**: Learning from examples, code reuse, documentation lookup

## 🎯 MCP Usage Guidelines

- **ALWAYS** use MCP tools when relevant instead of guessing or using outdated information
- **PREFER** MCP documentation over web searches when working with:
  - aiogram handlers and features
  - Database schema changes
  - Deployment and Railway configuration
  - GitHub code examples
- **CHECK** MCP tools first before implementing complex features
- **VERIFY** implementation patterns using MCP when unsure

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
- **💡 Use MCP**: `mcp_supabase_list_tables()` to verify schema
- **💡 Use MCP**: `mcp_supabase_execute_sql()` to test queries during development

### Phase 3: Bot Handlers
- Implement FSM states
- Create keyboard factories  
- Write handlers for all commands using lexicon_ru.py
- **💡 Use MCP**: `mcp_aiogram_Docs_search_aiogram_documentation()` for handler patterns, FSM examples, keyboard layouts
- **💡 Use MCP**: `mcp_aiogram_Docs_search_aiogram_code()` to find real-world examples

### Phase 4: Analytics Core
- CSV processor
- KPI calculator
- Report generator
- **💡 Use MCP**: `mcp_github_search_code()` for pandas/CSV processing examples

### Phase 5: Background Workers
- ARQ tasks setup
- CSV processing worker
- Periodic tasks
- **💡 Use MCP**: `mcp_github_search_code()` for ARQ task patterns, async worker examples

### Phase 6: Referral System
- IQ Points system (1 point per PRO/ULTRA purchase)
- Point accrual logic (track referral purchases)
- Point exchange system (5 exchange options)
- Statistics and balance tracking
- **💡 Use MCP**: `mcp_supabase_execute_sql()` to test referral queries and statistics
- **💡 Use MCP**: `mcp_github_search_code()` for referral program patterns

### Phase 7: Payment Integration
- Tribute.tg API client
- Webhook handler
- Payment processing
- **💡 Use MCP**: `mcp_github_search_code()` for webhook handler patterns, HMAC verification examples

### Phase 8: Admin Panel
- FastAPI views
- CRUD operations
- Dashboard
- Broadcasting
- **💡 Use MCP**: `mcp_github_search_code()` for FastAPI patterns, CRUD examples
- **💡 Use MCP**: `mcp_supabase_execute_sql()` to test queries for admin views

### Phase 9: Testing & Quality
- Unit tests
- Integration tests
- Mypy strict mode
- Ruff linting
- **💡 Use MCP**: `mcp_github_search_code()` to find testing patterns and examples
- **💡 Use MCP**: `mcp_github_search_repositories()` for similar projects' test suites

### Phase 10: Deployment
- Railway configuration
- Environment variables
- Health checks
- Monitoring
- **💡 Use MCP**: `mcp_Railway_check-railway-status()` to verify CLI setup
- **💡 Use MCP**: `mcp_Railway_deploy()` for deployments
- **💡 Use MCP**: `mcp_Railway_get-logs()` to troubleshoot issues
- **💡 Use MCP**: `mcp_Railway_list-services()` to verify service configuration
- **💡 Use MCP**: `mcp_Railway_set-variables()` to configure environment variables

Refer to tid_v2.md for detailed specifications.
