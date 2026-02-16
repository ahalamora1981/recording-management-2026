# Recording Management System

A web application for querying and managing call recordings from the Verba (VFC) platform.

## Features

- **Authentication**: Secure login system with role-based access
- **Admin Panel**: Manage user accounts (admin only)
- **Recording Query**: Search recordings by time range and participant name
- **Download & Play**: Download recordings and play them directly in the browser

## Tech Stack

- **Frontend**: Vue.js 3 + Vite
- **Backend**: Python FastAPI
- **Database**: SQLite

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.8+

### Installation

1. **Backend Setup**

```bash
cd backend
pip install -r requirements.txt
```

2. **Frontend Setup**

```bash
cd frontend
npm install
```

### Running the Application

1. **Start the Backend** (in one terminal)

```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

2. **Start the Frontend** (in another terminal)

```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:5173`

### Default Credentials

- **Username**: `admin`
- **Password**: `admin123`

## API Endpoints

- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `GET /api/me` - Get current user
- `GET /api/users` - List users (admin only)
- `POST /api/users` - Create user (admin only)
- `DELETE /api/users/{id}` - Delete user (admin only)
- `POST /api/query` - Query recordings
- `GET /api/download/{ccrd_id}` - Download recording

## Verba Integration

The system integrates with Verba (VFC) Capture platform to:
- Authenticate with the Verba API
- Search for call recordings by time range and participant
- Download audio recordings in MP3 format
