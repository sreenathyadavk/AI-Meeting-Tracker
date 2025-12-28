# 🎙️ AI Meeting Tracker

**Self-hosted AI-powered meeting transcription and task extraction**

## ✨ Features

- 🎯 **Upload recordings** (MP3, MP4, WAV, M4A) - up to 1.5 hours
- 🎙️ **Transcribe with Whisper** (local, no API costs)
- 🤖 **Extract tasks with Ollama** (Llama 3.1 or Mistral)
- 💬 **Chat about meetings** - ask questions about transcript
- 📚 **Meeting history** - last 10 meetings in sidebar
- 💾 **Database persistence** - SQLite storage for all meetings
- ✅ **Structured tasks** with owner, deadline, confidence scores
- 🔒 **100% self-hosted** - no cloud dependencies, privacy-first

## 🛠️ Tech Stack

- **Backend:** Python 3.11+ with FastAPI  
- **Database:** SQLite with SQLAlchemy ORM
- **Transcription:** OpenAI Whisper (100% local, no API)
- **AI Extraction:** Ollama (Llama 3.1 8B)
- **Frontend:** Vue 3 + Vite + Vue Router
- **Styling:** Custom CSS with glassmorphism design

## 📋 System Requirements

- **Python:** 3.11 or higher
- **Node.js:** 18+ 
- **RAM:** 10GB+ (for Whisper + Ollama)
- **Disk:** ~5GB for AI models
- **GPU:** Optional (CPU works fine, just slower)
- **OS:** Linux, macOS, Windows (WSL)
- **FFmpeg:** Required for audio processing

## 🚀 Quick Start

### 0. Install FFmpeg (Required)

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Check installation
ffmpeg -version
```

### 1. Install Ollama

```bash
chmod +x scripts/install_ollama.sh
./scripts/install_ollama.sh
```

This will:
- Install Ollama
- Pull Llama 3.1 8B model (~4.7GB)

### 2. Setup Backend

```bash
chmod +x setup_backend.sh
./setup_backend.sh
```

### 3. Setup Frontend

```bash
chmod +x setup_frontend.sh
./setup_frontend.sh
```

### 4. Run the Application

**Terminal 1** - Start Backend:
```bash
cd backend
source venv/bin/activate
python main.py
```

Backend runs on: `http://localhost:8000`

**Terminal 2** - Start Frontend:
```bash
cd frontend
npm run dev
```

Frontend runs on: `http://localhost:5173`

### 5. Test It

1. Open `http://localhost:5173` in your browser
2. Upload a meeting recording
3. Click "Process Recording"
4. Wait for transcription + AI extraction (~1-2 minutes)
5. View extracted tasks with confidence scores!

## 📖 How It Works

1. **Upload** → File saved to `backend/uploads/`
2. **Transcribe** → OpenAI Whisper converts full audio to text (up to 1.5 hours)
3. **Extract** → Ollama (Llama 3.1) identifies action items from transcript
4. **Store** → Meeting, tasks, and metadata saved to SQLite database
5. **Display** → Tasks shown with owner, deadline, and confidence scores
6. **Chat** → Ask questions about the meeting using AI

## 📁 Project Structure

```
ProjectX/
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── database.py                # SQLAlchemy models
│   ├── config.py                  # Environment configuration
│   ├── requirements.txt           # Python dependencies
│   ├── modules/
│   │   ├── transcription.py      # Whisper integration
│   │   └── task_extractor.py     # Ollama task extraction
│   ├── uploads/                   # Temporary file storage
│   └── meetings.db                # SQLite database
├── frontend/
│   ├── src/
│   │   ├── App.vue               # Main layout with history sidebar
│   │   ├── pages/
│   │   │   ├── UploadPage.vue    # File upload interface
│   │   │   └── ResultsPage.vue   # Results with chat
│   │   ├── composables/
│   │   │   ├── useHistory.js     # LocalStorage history
│   │   │   └── useSession.js     # Session management  
│   │   ├── router/
│   │   │   └── index.js          # Vue Router config
│   │   ├── style.css             # Modern dark theme
│   │   └── main.js               # Vue entry point
│   └── package.json
├── scripts/
│   └── install_ollama.sh         # Ollama installation
├── .env.example                   # Environment config template
├── .gitignore
├── LICENSE                        # MIT License
└── README.md
```

## 🔧 Configuration

### Change AI Model

Edit `backend/modules/task_extractor.py`:

```python
async def extract_tasks(transcript: str, model: str = "mistral:7b"):
    # Change model here
```

Available models:
- `llama3.1:8b` (default, best accuracy)
- `mistral:7b` (faster, good accuracy)
- `llama2:7b` (lighter)

Pull new models: `ollama pull mistral:7b`

### Change Whisper Model

Edit `backend/modules/transcription.py`:

```python
_model = WhisperModel("medium", device="cpu", compute_type="int8")
```

Models: `tiny`, `base`, `small`, `medium`, `large`

## 🐛 Troubleshooting

**Ollama connection error:**
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve
```

**Whisper model download:**
- First run will download Whisper model (~150MB for base)
- This only happens once

**Port already in use:**
```bash
# Change port in backend/main.py
uvicorn.run(app, host="0.0.0.0", port=8001)
```

## 🎯 Roadmap

**Current Status: Working Prototype with Database ✅**

Completed:
- ✅ SQLite database persistence
- ✅ Meeting history and retrieval
- ✅ Chat feature for Q&A about meetings
- ✅ Full audio transcription (up to 1.5 hours)
- ✅ Vue Router with separate pages
- ✅ Modern UI with glassmorphism
- ✅ Health check API endpoint

Coming Soon (Production Ready):
- 🚧 Docker containerization
- 🚧 Production frontend build
- 🚧 Security hardening (rate limiting, file validation)
- 🚧 Deployment documentation

Future MVP Features:
- 📋 Task editing (CRUD operations)
- 👥 Speaker diarization (identify who said what)
- 📊 Kanban board integration
- 🎨 Enhanced UI animations
- 🧪 Automated tests

## 📝 License

MIT
##
Built with:
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Optimized Whisper
- [Ollama](https://ollama.com/) - Local LLM runtime
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python API
- [Vue 3](https://vuejs.org/) - Progressive framework

---

**Made with ❤️ for productivity nerds who hate cloud subscriptions**
