import os
import tempfile
import logging
import traceback
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Optional
import sqlite3
import hashlib
import secrets
import xml.etree.ElementTree as ET
import requests
from openai import OpenAI
from urllib3.exceptions import InsecureRequestWarning
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from contextlib import contextmanager, asynccontextmanager

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



@asynccontextmanager
async def lifespan(app: FastAPI):
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
    init_db()
    yield


app = FastAPI(title="Recording Management System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

DATABASE = "recording_management.db"

VERBA_CONFIG = {
    "host": "https://mst-vfc.verint.training",
    "api_key": "D466035F-CE26-4E6A-BD4E-891A3BD58807",
    "username": "jonnytaodemo",
    "password": "Jun@7895123"
}

ASR_CONFIG = {
    "api_url": "https://open.bigmodel.cn/api/paas/v4/audio/transcriptions",
    "api_key": "c660899f0ae74d6391059e4683a6ffe9.hAtP5SQGPPucjeI1"
}

LLM_CONFIG = {
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "api_key": "sk-79bf4a6d9e304b059a67a6db843a5ed4",
    "model": "qwen-flash"
}

openai_client = OpenAI(
    base_url=LLM_CONFIG["base_url"],
    api_key=LLM_CONFIG["api_key"]
)

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS recordings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ccrd_id TEXT UNIQUE NOT NULL,
                verba_user_name TEXT,
                start_time TEXT,
                end_time TEXT,
                duration INTEGER,
                local_file_path TEXT,
                transcription TEXT,
                channel TEXT DEFAULT 'call',
                imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor = conn.execute("PRAGMA table_info(recordings)")
        columns = [row[1] for row in cursor.fetchall()]
        if "transcription" not in columns:
            conn.execute("ALTER TABLE recordings ADD COLUMN transcription TEXT")
        if "channel" not in columns:
            conn.execute("ALTER TABLE recordings ADD COLUMN channel TEXT DEFAULT 'call'")
        
        cursor = conn.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            admin_password = hashlib.sha256("admin123".encode()).hexdigest()
            conn.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                ("admin", admin_password, 1)
            )
        conn.commit()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash

def create_token(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    with get_db() as conn:
        conn.execute(
            "INSERT INTO tokens (user_id, token, expires_at) VALUES (?, ?, ?)",
            (user_id, token, datetime.now() + timedelta(days=1))
        )
        conn.commit()
    return token

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT user_id, expires_at FROM tokens WHERE token = ?",
            (token,)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Invalid token")
        if datetime.fromisoformat(row["expires_at"]) < datetime.now():
            conn.execute("DELETE FROM tokens WHERE token = ?", (token,))
            conn.commit()
            raise HTTPException(status_code=401, detail="Token expired")
        cursor = conn.execute("SELECT id, username, is_admin FROM users WHERE id = ?", (row["user_id"],))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return {"id": user["id"], "username": user["username"], "is_admin": user["is_admin"]}

class LoginRequest(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str

class QueryRequest(BaseModel):
    start_time: str
    end_time: str
    participant_name: Optional[str] = None

class ImportRequest(BaseModel):
    recordings: list

class Recording(BaseModel):
    ccrd_id: str
    verba_user_name: str
    start_time: str
    end_time: str
    duration: int


@app.post("/api/login")
def login(request: LoginRequest):
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT id, username, password_hash, is_admin FROM users WHERE username = ?",
            (request.username,)
        )
        user = cursor.fetchone()
        if not user or not verify_password(request.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_token(user["id"])
        return {
            "token": token,
            "username": user["username"],
            "is_admin": bool(user["is_admin"]),
            "user_id": user["id"]
        }


@app.post("/api/logout")
def logout(user: dict = Depends(verify_token)):
    return {"message": "Logged out successfully"}

@app.get("/api/users")
def get_users(user: dict = Depends(verify_token)):
    if not user["is_admin"]:
        raise HTTPException(status_code=403, detail="Admin only")
    with get_db() as conn:
        cursor = conn.execute("SELECT id, username, is_admin, created_at FROM users")
        users = []
        for row in cursor.fetchall():
            user_dict = dict(row)
            user_dict['is_admin'] = bool(user_dict['is_admin'])
            users.append(user_dict)
    return users

@app.post("/api/users")
def create_user(request: UserCreate, user: dict = Depends(verify_token)):
    if not user["is_admin"]:
        raise HTTPException(status_code=403, detail="Admin only")
    password_hash = hash_password(request.password)
    with get_db() as conn:
        try:
            conn.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
                (request.username, password_hash, 0)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "User created successfully"}

@app.delete("/api/users/{user_id}")
def delete_user(user_id: int, user: dict = Depends(verify_token)):
    if not user["is_admin"]:
        raise HTTPException(status_code=403, detail="Admin only")
    if user_id == user["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    with get_db() as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    return {"message": "User deleted successfully"}

@app.post("/api/query")
def query_local_recordings(request: QueryRequest, user: dict = Depends(verify_token)):
    try:
        with get_db() as conn:
            start_time = request.start_time.replace('T', ' ')
            end_time = request.end_time.replace('T', ' ')
            
            query = """
                SELECT ccrd_id, verba_user_name, start_time, duration, local_file_path, transcription, channel
                FROM recordings 
                WHERE start_time >= ? AND start_time <= ?
            """
            params = [start_time, end_time]
            
            if request.participant_name:
                query += " AND verba_user_name LIKE ?"
                params.append(f"%{request.participant_name}%")
            
            query += " ORDER BY start_time DESC"
            
            cursor = conn.execute(query, params)
            recordings = []
            for row in cursor.fetchall():
                recordings.append({
                    "ccrd_id": row["ccrd_id"],
                    "verba_user_name": row["verba_user_name"],
                    "start_time": row["start_time"],
                    "duration": row["duration"],
                    "local_path": row["local_file_path"],
                    "channel": row["channel"] or "call",
                    "transcribed": "Yes" if row["transcription"] and row["transcription"].strip() else "No"
                })
            
            return recordings
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query/vfc")
def query_vfc_recordings(request: QueryRequest, user: dict = Depends(verify_token)):
    try:
        auth_response = requests.get(
            f"{VERBA_CONFIG['host']}/verba/api",
            params={
                "action": "RequestToken",
                "apiKey": VERBA_CONFIG["api_key"],
                "userName": VERBA_CONFIG["username"],
                "password": VERBA_CONFIG["password"]
            },
            timeout=30,
            verify=False
        )
        
        root = ET.fromstring(auth_response.text)
        response_elem = root.find(".//Response")
        if response_elem is None:
            raise Exception(f"Invalid response from Verba API: {auth_response.text[:500]}")
        
        if response_elem.get("code") != "0":
            raise Exception(f"Authentication failed: {auth_response.text[:500]}")
        
        token = response_elem.get("token")
        
        session_id = root.find(".//SessionId")
        jsessionid = session_id.text if session_id is not None else ""
        
        cookies = {}
        if jsessionid:
            cookies = {"JSESSIONID": jsessionid}
        
        start_time = request.start_time.replace('T', ' ')
        end_time = request.end_time.replace('T', ' ')
        
        params = {
            "action": "SearchCalls",
            "apiKey": VERBA_CONFIG["api_key"],
            "token": token,
            "pagelen": 100,
            "returnMetadata": 1,
            "start": start_time,
            "end": end_time
        }
        
        if request.participant_name:
            params["participant_name"] = request.participant_name
        
        search_response = requests.get(
            f"{VERBA_CONFIG['host']}/verba/api",
            params=params,
            cookies=cookies,
            timeout=30,
            verify=False
        )
        
        root = ET.fromstring(search_response.text)
        
        recordings = []
        
        verbacdrlist = root if root.tag == "verbacdrlist" else root.find(".//verbacdrlist")
        
        if verbacdrlist is None:
            print(f"DEBUG: No verbacdrlist. Response: {search_response.text[:1000]}")
            return recordings
        
        for ccdr in verbacdrlist.findall("verbacdr"):
            ccrd_id = ccdr.findtext("ccdr_id") or ccdr.findtext("ccdrId") or ccdr.findtext("id") or ccdr.get("index", "")
            verba_user_name = ccdr.findtext("verba_user_name") or ccdr.findtext("user") or ""
            start_time = ccdr.findtext("starttime") or ccdr.findtext("start_time") or ccdr.findtext("startdate") or ""
            end_time = ccdr.findtext("endtime") or ccdr.findtext("end_time") or ccdr.findtext("enddate") or ""
            duration_str = ccdr.findtext("duration") or "0"
            try:
                parts = duration_str.split(':')
                duration = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2]) if len(parts) == 3 else int(duration_str)
            except Exception as e:
                logger.error(f"Error parsing duration {duration_str} for ccrd_id {ccrd_id}: {e}")
                duration = 0
            
            recordings.append({
                "ccrd_id": ccrd_id,
                "verba_user_name": verba_user_name,
                "start_time": start_time,
                "end_time": end_time,
                "duration": duration
            })
        
        return recordings
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/import")
def import_recordings(request: ImportRequest, user: dict = Depends(verify_token)):
    try:
        import_dir = "recordings"
        os.makedirs(import_dir, exist_ok=True)
        
        auth_response = requests.get(
            f"{VERBA_CONFIG['host']}/verba/api",
            params={
                "action": "RequestToken",
                "apiKey": VERBA_CONFIG["api_key"],
                "userName": VERBA_CONFIG["username"],
                "password": VERBA_CONFIG["password"]
            },
            timeout=30,
            verify=False
        )
        
        root = ET.fromstring(auth_response.text)
        response_elem = root.find(".//Response")
        if response_elem is None:
            raise Exception("Failed to authenticate with VFC")
        
        token = response_elem.get("token")
        session_id = root.find(".//SessionId")
        jsessionid = session_id.text if session_id is not None else ""
        
        cookies = {}
        if jsessionid:
            cookies = {"JSESSIONID": jsessionid}
        
        imported = []
        failed = []
        
        for rec in request.recordings:
            try:
                ccrd_id = rec.get("ccrd_id")
                if not ccrd_id:
                    print(f"DEBUG: Recording has no ccrd_id: {rec}")
                    failed.append({"ccrd_id": "unknown", "error": "No ccrd_id", "rec": str(rec)})
                    continue
                
                with get_db() as conn:
                    cursor = conn.execute(
                        "SELECT ccrd_id FROM recordings WHERE ccrd_id = ?",
                        (ccrd_id,)
                    )
                    if cursor.fetchone():
                        failed.append({"ccrd_id": ccrd_id, "error": "Already exists in database"})
                        continue
                
                print(f"DEBUG: Downloading {ccrd_id}")
                
                media_response = requests.get(
                    f"{VERBA_CONFIG['host']}/verba/api",
                    params={
                        "action": "GetMediaEncoded",
                        "apiKey": VERBA_CONFIG["api_key"],
                        "token": token,
                        "cid": ccrd_id,
                        "format": "mp3"
                    },
                    cookies=cookies,
                    timeout=60,
                    verify=False
                )
                
                if media_response.status_code != 200:
                    print(f"DEBUG: Failed to download {ccrd_id}, status: {media_response.status_code}")
                    failed.append({"ccrd_id": ccrd_id, "error": f"Failed to download, status: {media_response.status_code}"})
                    continue
                
                start_time = rec.get("start_time", "")
                print(f"DEBUG: start_time = {start_time}")
                if start_time:
                    try:
                        start_time_clean = start_time.split('.')[0]
                        dt = datetime.strptime(start_time_clean, "%Y-%m-%d %H:%M:%S")
                        year = dt.strftime("%Y")
                        month = dt.strftime("%m")
                        import_dir = os.path.join("recordings", year, month)
                    except Exception as e:
                        print(f"DEBUG: Failed to parse start_time: {e}")
                        import_dir = "recordings"
                else:
                    import_dir = "recordings"
                
                print(f"DEBUG: import_dir = {import_dir}")
                os.makedirs(import_dir, exist_ok=True)
                file_path = os.path.join(import_dir, f"{ccrd_id}.mp3")
                with open(file_path, 'wb') as f:
                    f.write(media_response.content)
                
                with get_db() as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO recordings 
                        (ccrd_id, verba_user_name, start_time, end_time, duration, local_file_path, channel)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (ccrd_id, rec.get("verba_user_name"), rec.get("start_time"), 
                          rec.get("end_time"), rec.get("duration"), file_path, "call"))
                    conn.commit()
                
                imported.append({"ccrd_id": ccrd_id, "status": "imported"})
                
            except Exception as e:
                failed.append({"ccrd_id": rec.get("ccrd_id"), "error": str(e)})
        
        return {"imported": imported, "failed": failed}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{ccrd_id}")
def download_recording(ccrd_id: str, user: dict = Depends(verify_token)):
    try:
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT local_file_path FROM recordings WHERE ccrd_id = ?",
                (ccrd_id,)
            )
            row = cursor.fetchone()
            
            if row and row["local_file_path"] and os.path.exists(row["local_file_path"]):
                file_path = row["local_file_path"]
                with open(file_path, 'rb') as f:
                    content = f.read()
                return StreamingResponse(
                    iter([content]),
                    media_type="audio/mpeg",
                    headers={
                        "Content-Disposition": f"attachment; filename={ccrd_id}.mp3"
                    }
                )
        
        auth_response = requests.get(
            f"{VERBA_CONFIG['host']}/verba/api",
            params={
                "action": "RequestToken",
                "apiKey": VERBA_CONFIG["api_key"],
                "userName": VERBA_CONFIG["username"],
                "password": VERBA_CONFIG["password"]
            },
            timeout=30,
            verify=False
        )
        
        root = ET.fromstring(auth_response.text)
        response_elem = root.find(".//Response")
        if response_elem is None:
            raise Exception(f"Invalid response from Verba API: {auth_response.text[:500]}")
        
        if response_elem.get("code") != "0":
            raise Exception(f"Authentication failed: {auth_response.text[:500]}")
        
        token = response_elem.get("token")
        
        session_id = root.find(".//SessionId")
        jsessionid = session_id.text if session_id is not None else ""
        
        cookies = {}
        if jsessionid:
            cookies = {"JSESSIONID": jsessionid}
        
        media_response = requests.get(
            f"{VERBA_CONFIG['host']}/verba/api",
            params={
                "action": "GetMediaEncoded",
                "apiKey": VERBA_CONFIG["api_key"],
                "token": token,
                "cid": ccrd_id,
                "format": "mp3"
            },
            cookies=cookies,
            headers={"Authorization": f"Bearer {token}"},
            timeout=60,
            verify=False
        )
        
        if media_response.status_code != 200:
            raise HTTPException(status_code=404, detail="Recording not found")
        
        return StreamingResponse(
            iter([media_response.content]),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename={ccrd_id}.mp3"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def chunk_audio(wav_path: str, chunk_duration: int = 30, overlap: int = 2) -> list:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", wav_path],
        capture_output=True, text=True, check=True
    )
    total_duration = float(result.stdout.strip())
    
    chunks = []
    start = 0
    chunk_num = 0
    while start < total_duration:
        end = min(start + chunk_duration, total_duration)
        chunk_path = tempfile.mktemp(suffix=f"_chunk{chunk_num}.wav")
        subprocess.run(
            ["ffmpeg", "-y", "-i", wav_path, "-ss", str(start), "-to", str(end), "-ar", "16000", "-ac", "1", chunk_path],
            capture_output=True, check=True
        )
        chunks.append({"path": chunk_path, "start": start, "end": end, "num": chunk_num})
        start = start + chunk_duration - overlap
        chunk_num += 1
    
    return chunks

def call_asr_api(chunk_path: str) -> str:
    with open(chunk_path, "rb") as f:
        files = {"file": (os.path.basename(chunk_path), f)}
        data = {"model": "glm-asr-2512"}
        headers = {"Authorization": f"Bearer {ASR_CONFIG['api_key']}"}
        response = requests.post(
            ASR_CONFIG["api_url"],
            files=files,
            data=data,
            headers=headers,
            verify=False,
            timeout=60
        )
    
    if response.status_code != 200:
        logger.error(f"ASR chunk error: {response.status_code} - {response.text}")
        return ""
    
    result = response.json()
    return result.get("text", "") or result.get("data", {}).get("text", "")

def process_with_llm(transcriptions: list) -> str:
    transcriptions_text = "\n".join([f"[{t['time']}] {t['text']}" for t in transcriptions])
    
    combined = " ".join([t["text"] for t in transcriptions])
    is_chinese = any('\u4e00' <= char <= '\u9fff' for char in combined)
    
    if is_chinese:
        speaker_label = "说话人"
    else:
        speaker_label = "Speaker"
    
    system_prompt = f"""# Task: Transcription Refinement

## Instructions:
- Read the ASR transcription and output it with speaker separation
- Each sentence MUST be on a separate line
- Use EXACTLY this format for each line: "[{speaker_label} A] sentence here" or "[{speaker_label} B] sentence here"
- Use {speaker_label} A, {speaker_label} B, {speaker_label} C, etc. for different speakers
- Maintain the original chronological order
- Do NOT add any explanations, comments, or additional text
- Output ONLY the formatted dialogue

## Output Format:
[{speaker_label} A] sentence here
[{speaker_label} B] sentence here
...

"""

    try:
        response = openai_client.chat.completions.create(
            model=LLM_CONFIG["model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"ASR Transcription:\n{transcriptions_text}"}
            ],
            max_tokens=8192,
            temperature=0.7,
            timeout=120
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"LLM error: {e}")
        return "\n".join([f"{t['text']}" for t in transcriptions])

@app.post("/api/recordings/{ccrd_id}/transcribe")
def transcribe_recording(ccrd_id: str, user: dict = Depends(verify_token)):
    try:
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT local_file_path, transcription FROM recordings WHERE ccrd_id = ?",
                (ccrd_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Recording not found")
            
            if row["transcription"]:
                return {"transcription": row["transcription"]}
            
            file_path = row["local_file_path"]
            if not file_path or not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="Audio file not found")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        logger.info(f"Transcribing file: {file_path}, ext: {file_ext}")
        
        wav_path = file_path
        if file_ext != ".wav":
            logger.info(f"Converting {file_ext} to wav...")
            wav_path = tempfile.mktemp(suffix=".wav")
            subprocess.run(
                ["ffmpeg", "-y", "-i", file_path, "-ar", "16000", "-ac", "1", wav_path],
                capture_output=True, check=True
            )
            logger.info(f"Converted to: {wav_path}")
        
        try:
            logger.info("Chunking audio into 30-second segments with 2-second overlap...")
            chunks = chunk_audio(wav_path, chunk_duration=30, overlap=2)
            logger.info(f"Created {len(chunks)} audio chunks")
            
            logger.info("Calling ASR API for each chunk concurrently...")
            transcriptions = []
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(call_asr_api, chunk["path"]): chunk for chunk in chunks}
                for future in as_completed(futures):
                    chunk = futures[future]
                    try:
                        text = future.result()
                        transcriptions.append({
                            "num": chunk["num"],
                            "start": chunk["start"],
                            "end": chunk["end"],
                            "time": f"{chunk['start']:.1f}s-{chunk['end']:.1f}s",
                            "text": text
                        })
                        logger.info(f"Chunk {chunk['num']} transcribed: {text[:50]}...")
                    except Exception as e:
                        logger.error(f"Chunk {chunk['num']} failed: {e}")
            
            for chunk in chunks:
                if os.path.exists(chunk["path"]):
                    os.unlink(chunk["path"])
            
            transcriptions.sort(key=lambda x: x["num"])
            combined_text = " ".join([t["text"] for t in transcriptions])
            logger.info(f"Combined ASR result: {combined_text[:200]}...")
            
            logger.info("Processing with LLM for speaker identification...")
            final_transcription = process_with_llm(transcriptions)
            logger.info(f"Final transcription: {final_transcription[:200]}...")
        finally:
            if wav_path != file_path and os.path.exists(wav_path):
                os.unlink(wav_path)
        
        with get_db() as conn:
            conn.execute(
                "UPDATE recordings SET transcription = ? WHERE ccrd_id = ?",
                (final_transcription, ccrd_id)
            )
            conn.commit()
        
        return {"transcription": final_transcription}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcribe error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/recordings/{ccrd_id}")
def delete_recording(ccrd_id: str, user: dict = Depends(verify_token)):
    try:
        file_path = None
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT local_file_path FROM recordings WHERE ccrd_id = ?",
                (ccrd_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Recording not found")
            
            if row["local_file_path"]:
                file_path = row["local_file_path"]
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        logger.info(f"Deleted audio file: {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to delete audio file {file_path}: {e}")
            
            conn.execute("DELETE FROM recordings WHERE ccrd_id = ?", (ccrd_id,))
            conn.commit()
            logger.info(f"Deleted recording from database: {ccrd_id}")
        
        if file_path:
            folder = os.path.dirname(file_path)
            try:
                if os.path.isdir(folder) and not os.listdir(folder):
                    os.rmdir(folder)
                    parent_folder = os.path.dirname(folder)
                    if os.path.isdir(parent_folder) and not os.listdir(parent_folder):
                        os.rmdir(parent_folder)
                    logger.info(f"Removed empty folder: {folder}")
            except Exception as e:
                logger.error(f"Failed to remove empty folder: {e}")
        
        return {"message": "Recording deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete recording error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/me")
def get_current_user(user: dict = Depends(verify_token)):
    return user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
