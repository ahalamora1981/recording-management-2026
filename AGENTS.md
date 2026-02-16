# AGENTS.md - Recording Management System

## Project Overview

This is a web application for querying and managing call recordings from the Verba (VFC) platform.

- **Frontend**: Vue.js 3 + Vite
- **Backend**: Python FastAPI
- **Database**: SQLite

## Build, Run, and Test Commands

### Frontend (Vue.js 3)

```bash
cd frontend

# Install dependencies
npm install

# Development server (port 3000, proxies /api to localhost:8000)
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

### Backend (FastAPI)

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server (auto-reload enabled)
python main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Running a Single Test

**No tests are currently configured in this project.** To add tests:

- Frontend: Add Vitest (`npm install -D vitest @vue/test-utils`) and configure in `vite.config.js`
- Backend: Add pytest (`pip install pytest`) and create `tests/` directory

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
├── components/    # Reusable Vue components
├── views/         # Page-level components
├── composables/   # Vue composables (hooks)
├── router/       # Vue Router configuration
├── assets/       # Static assets
├── main.js       # App entry point
└── style.css     # Global styles
```

**Vue 3 Composition API:**
- Use `<script setup>` syntax for all new components
- Use `ref` for primitives, `reactive` for objects
- Import Vue APIs explicitly: `import { ref, computed, onMounted } from 'vue'`

**Imports Order:**
1. Vue/Vue Router imports
2. Third-party libraries (axios, etc.)
3. Local components/composables
4. Relative path imports

**Example:**
```javascript
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useI18n } from '../composables/useI18n'
import { useTheme } from '../composables/useTheme'
import SomeComponent from '../components/SomeComponent.vue'
```

**Template Conventions:**
- Use `v-if`/`v-else` for conditional rendering
- Use `v-for` with `:key` for lists
- Use kebab-case for attributes: `<my-component :prop-name="value">`
- Prefer `v-model` over `:value` + `@input`

**Styling:**
- Use scoped styles (`<style scoped>`)
- Follow CSS custom properties defined in `style.css`
- Use flexbox for layouts
- Use `var(--variable-name)` for theme colors

### Backend (Python FastAPI)

**File Structure:**
```
backend/
├── main.py           # Main application (all endpoints here currently)
├── recordings/       # Downloaded audio files
└── .venv/           # Virtual environment
```

**Imports Order:**
1. Standard library
2. Third-party packages
3. Local imports

**Type Hints:**
- Use type hints for function parameters and return types
- Use `Optional[T]` for nullable types
- Use Pydantic models for request/response validation

**Example:**
```python
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/login")
def login(request: LoginRequest) -> dict:
    ...
```

**Error Handling:**
- Use `HTTPException` for HTTP errors with appropriate status codes
- Return descriptive error messages: `raise HTTPException(status_code=401, detail="Invalid credentials")`
- Log errors appropriately using the `logging` module

**Database:**
- Use the `get_db()` context manager for SQLite connections
- Use parameterized queries to prevent SQL injection
- Close connections in `finally` block or use context manager

**API Patterns:**
- Use RESTful conventions: GET for retrieval, POST for creation, DELETE for deletion
- Use `/api/` prefix for all API endpoints
- Return JSON responses (dicts are automatically serialized)

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Vue components | PascalCase | `LoginView.vue`, `AudioPlayer.vue` |
| Composables | camelCase | `useI18n.js`, `useTheme.js` |
| Vue files | kebab-case in templates | `<audio-player>`, `<nav-bar>` |
| Python functions | snake_case | `def get_users()`, `def hash_password()` |
| Python classes | PascalCase | `class LoginRequest(BaseModel)` |
| Python constants | UPPER_SNAKE_CASE | `DATABASE = "..."` |
| Database tables | snake_case | `users`, `recordings` |

### Security Considerations

- Never commit secrets, API keys, or credentials to version control
- Use environment variables or configuration files for sensitive data
- The backend has hardcoded API keys for VFC integration - these should be externalized
- CORS is set to `allow_origins=["*"]` - restrict in production

### Default Credentials (Development Only)

- Username: `admin`
- Password: `admin123`

## Additional Notes

- Backend runs on port 8000, Frontend proxies API calls to it
- Frontend dev server runs on port 3000 (configured in `vite.config.js`)
- SQLite database: `backend/recording_management.db`
- Recordings are stored in `backend/recordings/{year}/{month}/`
