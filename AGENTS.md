# AGENTS.md - Recording Management System

A web application for querying and managing call recordings from the Verba (VFC) platform.

## Project Overview

- **Frontend**: Vue.js 3 + Vite (port 3000)
- **Backend**: Python FastAPI (port 8000)
- **Database**: SQLite (`backend/recording_management.db`)

## Build, Run, and Test Commands

### Frontend

```bash
cd frontend
npm install
npm run dev      # Dev server with API proxy to localhost:8000
npm run build    # Production build
npm run preview  # Preview production build
```

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py   # Auto-reload enabled
# Or: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Running a Single Test

No tests configured. To add:
- Frontend: `npm install -D vitest @vue/test-utils` + configure in `vite.config.js`
- Backend: `pip install pytest` + create `tests/` directory

### Linting

No linting configured. To add:
- Frontend: `npm install -D eslint prettier`
- Backend: `pip install ruff` + run `ruff check .`

## Code Style Guidelines

### General Principles

- Keep code concise and readable
- Use meaningful, descriptive names
- Avoid unnecessary comments (code should be self-explanatory)
- Follow existing patterns in each codebase

### Frontend (Vue.js 3)

**File Structure:**
```
frontend/src/
├── components/    # Reusable Vue components (PascalCase)
├── views/         # Page-level components (PascalCase)
├── composables/   # Vue composables/hooks (camelCase)
├── router/        # Vue Router configuration
├── assets/        # Static assets
├── main.js        # App entry point
└── style.css      # Global CSS variables
```

**Vue 3 Composition API:**
- Use `<script setup>` syntax for all new components
- Use `ref` for primitives, `reactive` for objects
- Define props with `defineProps`, events with `defineEmits`

**Imports Order:** Vue/Vue Router → Third-party → Composables → Components

```javascript
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useI18n } from '../composables/useI18n'
import SomeComponent from '../components/SomeComponent.vue'
```

**Template Conventions:**
- Use `v-if`/`v-else` for conditional rendering
- Use `v-for` with `:key` for lists
- Use kebab-case for attributes: `<my-component :prop-name="value">`
- Prefer `v-model` over `:value` + `@input`

**Styling:**
- Use scoped styles (`<style scoped>`)
- Use CSS custom properties from `style.css`
- Use flexbox/grid for layouts

### Backend (Python FastAPI)

**File Structure:**
```
backend/
├── main.py         # All endpoints
├── recordings/      # Downloaded audio (backend/recordings/{year}/{month}/)
└── .venv/           # Virtual environment
```

**Imports Order:** Standard library → Third-party → Local

```python
import os
import logging
from typing import Optional
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
```

**Type Hints & Pydantic:**
- Use type hints for function parameters and return types
- Use `Optional[T]` for nullable types
- Use Pydantic models for request/response validation

```python
class LoginRequest(BaseModel):
    username: str
    password: str
```

**Error Handling:**
- Use `HTTPException` with appropriate status codes
- Return descriptive error messages
- Log errors using the `logging` module

**Database:**
- Use `get_db()` context manager for SQLite connections
- Use parameterized queries to prevent SQL injection

**API Patterns:**
- RESTful conventions: GET/POST/DELETE
- Use `/api/` prefix for all API endpoints
- Use Bearer token authentication with `HTTPBearer`

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Vue components | PascalCase | `LoginView.vue`, `AudioPlayer.vue` |
| Composables | camelCase | `useI18n.js` |
| Vue templates | kebab-case | `<audio-player>` |
| Python functions | snake_case | `get_users()` |
| Python classes | PascalCase | `LoginRequest` |
| Database tables | snake_case | `users`, `recordings` |

### Security Considerations

- Never commit secrets, API keys, or credentials to version control
- Use environment variables for sensitive data
- CORS is `allow_origins=["*"]` - restrict in production

### Default Credentials (Development Only)

- Username: `admin`, Password: `admin123`

## Additional Notes

- Frontend proxies `/api` to backend port 8000
- Recordings stored in `backend/recordings/{year}/{month}/`
- Use `window.$modal.alert(message, title)` for alert dialogs
- Auth stores: `token`, `username`, `isAdmin`, `userId` in localStorage

## Verifying Changes

After making changes:
1. Run `npm run build` in frontend
2. Verify backend starts: `cd backend && python main.py`
3. Test functionality in browser
4. Check browser console for JS errors
5. Check backend console for Python errors/warnings
