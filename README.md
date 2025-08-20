Let me quickly scan the database schema and key endpoints to ensure the README is accurate and precise. I'll read the database schema file and skim the Flask routes to capture exact endpoints and behavior.
Read file: /Users/anuragdeshmukh/Everything/EDI SEM 5/newapp/database.py

Let me quickly scan the remaining Flask routes in `EDI_project_enhanced.py` to list all available endpoints precisely for the README.
Read file: /Users/anuragdeshmukh/Everything/EDI SEM 5/newapp/EDI_project_enhanced.py

Read file: /Users/anuragdeshmukh/Everything/EDI SEM 5/newapp/EDI_project_enhanced.py

Read file: /Users/anuragdeshmukh/Everything/EDI SEM 5/newapp/pdf_parser.py

I'll scan the database schema and Flask endpoints to make sure every command and detail below matches the code, then give you a precise README section you can paste in.

### Project Overview
- Backend: Flask API (`EDI_project_enhanced.py`) on port 5002
- PDF Parsing: `pdf_parser.py` extracts colleges, branches, and cutoff data
- Database: SQLite (`college_cutoffs.db`) with `colleges`, `branches`, `cutoff_data`
- Local LLM: Ollama (`gemma3:1b`) for general queries; Cohere fallback (optional)
- Frontend: React app in the same `newapp` folder (port 3000), CORS enabled

### Prerequisites
- Python 3 (use python3)
- Node.js + npm (for frontend)
- curl (for testing API)
- Optional: conda (if you prefer)
- Optional: Cohere API key in `.env`

### Installation
- Create and activate a Python env (choose one):

```bash
# Option A: venv
cd /Users/anuragdeshmukh/Everything/EDI\ SEM\ 5/newapp
python3 -m venv .venv
source .venv/bin/activate

# Option B: conda
conda create -n edi python=3.11 -y
conda activate edi
```

- Install Python dependencies:

```bash
pip install flask flask-cors PyPDF2 pandas openpyxl fuzzywuzzy python-Levenshtein requests python-dotenv cohere argostranslate
```

- Install and prepare Ollama (local LLM):

```bash
# Use the helper script (recommended)
bash install_ollama.sh

# Or manually:
# 1) Install Ollama from https://ollama.com
# 2) Then pull the model:
ollama pull gemma3:1b
```

- Optional: Cohere fallback
  - Create `.env` in `newapp` with:
    ```
    COHERE_API_KEY=your_key_here
    ```

### Run the Backend
```bash
cd /Users/anuragdeshmukh/Everything/EDI\ SEM\ 5/newapp
python3 EDI_project_enhanced.py
```
- Server: http://localhost:5002
- Health check:
```bash
curl http://localhost:5002/health
```

### API Endpoints
- POST `/chat` — Enhanced chatbot (college and general queries)
- POST `/upload-pdf` — Upload and parse PDF; stores data into DB
- GET `/colleges` — List/search colleges (`?search=coep`)
- GET `/college/<college_code>` — Details for one college
- GET `/database-stats` — Counts of colleges/branches/cutoffs
- GET `/health` — Health check

### Quick Tests (curl)
- General chat:
```bash
curl -X POST http://localhost:5002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How to prepare for engineering entrance exams?"}'
```

- College search:
```bash
curl -X POST http://localhost:5002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find colleges in Pune"}'
```

- Cutoff (COEP example):
```bash
curl -X POST http://localhost:5002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the cutoff for COEP Electronics?"}'
```

- Upload and parse PDF:
```bash
# From newapp folder; uses included cutoff.pdf
curl -X POST http://localhost:5002/upload-pdf \
  -F "file=@cutoff.pdf"
```

- List colleges:
```bash
curl "http://localhost:5002/colleges?search=coep"
```

- Get one college:
```bash
curl "http://localhost:5002/college/16006"
```

- Database stats:
```bash
curl http://localhost:5002/database-stats
```

### Database Details (SQLite)
- File: `college_cutoffs.db` (in `newapp`)
- Tables:
  - `colleges`:
    - `college_code` TEXT UNIQUE, `college_name` TEXT
  - `branches`:
    - `college_id` FK, `branch_code` TEXT, `branch_name` TEXT, `status` TEXT
    - UNIQUE on `(college_id, branch_code)`
  - `cutoff_data`:
    - `branch_id` FK, `stage` TEXT, `category` TEXT, `rank` INTEGER, `percentage` REAL
    - UNIQUE on `(branch_id, stage, category)`
- Indexes: college_code, branch_code, and cutoff (branch_id, stage, category)
- Reset DB:
```bash
rm college_cutoffs.db
python3 EDI_project_enhanced.py   # auto-recreates tables on start
```
- Inspect DB:
```bash
sqlite3 college_cutoffs.db
.tables
.schema colleges
SELECT COUNT(*) FROM colleges;
SELECT * FROM colleges LIMIT 5;
```

### PDF Parsing
- Parser: `pdf_parser.py` (`EnhancedCollegeParser`)
  - Extracts:
    - College code/name by strict line start match (`^\d{5} - Name`)
    - Branch code/name, status
    - Stages/categories with rank/percentage (robust to line breaks)
  - Handles multi-college PDFs; stores into DB via `database.py`
- Test on included sample:
```bash
python3 test_full_pdf.py
# or
python3 test_real_pdf.py
```

### Frontend (React)
```bash
cd /Users/anuragdeshmukh/Everything/EDI\ SEM\ 5/newapp
npm install
npm start
```
- Opens at http://localhost:3000
- Chat and PDF upload components call backend at http://localhost:5002
- If you see connection issues, ensure the backend is running and CORS is enabled (it is in `EDI_project_enhanced.py`)

### Useful Test Scripts
- `test_enhanced_chatbot.py` — Samples for various chatbot queries
- `test_full_pdf.py` / `test_real_pdf.py` — Run parser and show stats
- `test_pdf_parser.py` — Parser + DB integration tests (mock + samples)

Run:
```bash
python3 test_enhanced_chatbot.py
python3 test_full_pdf.py
python3 test_real_pdf.py
python3 test_pdf_parser.py
```

### Running Everything Together
1) Start backend:
```bash
cd /Users/anuragdeshmukh/Everything/EDI\ SEM\ 5/newapp
python3 EDI_project_enhanced.py
```
2) Start frontend in a new terminal:
```bash
cd /Users/anuragdeshmukh/Everything/EDI\ SEM\ 5/newapp
npm start
```
3) Optional: Upload PDF to populate DB, then chat from the frontend.

### Troubleshooting
- Port 5002 in use:
```bash
lsof -i :5002
kill -9 <PID>
```
- Ollama not responding:
  - Ensure Ollama is running (Mac app or `ollama serve`)
  - `ollama pull gemma3:1b`
- Cohere fallback not used:
  - Add `COHERE_API_KEY` in `.env`
- Large PDF errors:
  - Max upload set to 16MB; adjust `MAX_CONTENT_LENGTH` in `EDI_project_enhanced.py` if needed
- Reset DB if data looks wrong:
```bash
rm college_cutoffs.db
python3 EDI_project_enhanced.py
```

### Files to Know
- Backend: `EDI_project_enhanced.py`
- Parser: `pdf_parser.py`
- Database: `database.py`
- DB file: `college_cutoffs.db`
- Sample PDF: `cutoff.pdf`
- Frontend: `src/` and `package.json`
- README docs: `ENHANCED_CHATBOT_README.md`

### Suggested README Additions
- Example screenshots of:
  - Successful `/upload-pdf` response
  - `/database-stats` after parsing
  - Chat replies for college and general queries
- Performance notes:
  - Parser is optimized for large PDFs (1400+ pages); uses robust regex and staged extraction
- Data provenance:
  - Mention the source/format of PDF if public

- Added improvements:
  - Clean output formatting for chat responses
  - Helpful tips appended to responses for user guidance

- Security:
  - This is a dev server; use a production WSGI server for deployment

- License/Contributors: As applicable

- Model note:
  - Local LLM: `gemma3:1b` via Ollama on `localhost:11434`
  - Cohere fallback: optional, used when local model unavailable

- Frontend integration:
  - Ensure `Chatbot.jsx` and any upload components point to port 5002

- Logging:
  - `logging` is used throughout; enable debug in `pdf_parser.py` if needed

- CORS:
  - Enabled globally for convenience (`flask_cors`)

That’s everything you need to run and test the full stack and to document it precisely in your README.
