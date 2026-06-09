# CodeGuard — Automated Code Analysis System

CodeGuard is a backend code-quality system that integrates with a custom version-control tool called **wit**.  
Every time you run `wit push`, the system sends your committed Python files to a FastAPI server, analyses them with the AST module, and returns visual graphs plus structured warnings.

---

## Features

| Check | Trigger |
|---|---|
| **Function Too Long** | Any function with more than 20 lines |
| **File Too Long** | Any file with more than 200 lines |
| **Unused Variable** | Variable assigned inside a function but never read |
| **Missing Docstring** | Function without a docstring |
| **Non-English Name** (bonus) | Identifier that contains non-ASCII characters (e.g. Hebrew) |

### Graphs returned by `/analyze`

1. **Pie Chart** — proportion of each issue type  
2. **Histogram** — distribution of function lengths  
3. **Bar Chart** — number of issues per file  
4. **Line Graph** *(bonus — appears after the 2nd push)* — total issues over time

---

## Folder Structure

```
codeguard-wit-analyzer-python/
├── backend/
│   ├── analyzer.py       # AST-based static analysis engine
│   ├── main.py           # FastAPI application (/analyze and /alerts endpoints)
│   ├── visualizer.py     # Matplotlib chart generator + push history
│   └── push_history.json # Created automatically; stores issue counts over time
├── cli.py                # Click CLI — exposes the 'wit' command
├── core.py               # WitManager — init / add / commit / log / checkout / push
├── ui.py                 # Abstract base class for the UI layer
├── setup.py              # Package definition; installs the 'wit' console command
├── requirements.txt      # Python dependencies
├── wit.bat               # Windows batch wrapper (alternative to pip install)
└── README.md
```

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Step 1 — Clone / download the project

```
git clone <repo-url>
cd codeguard-wit-analyzer-python
```

### Step 2 — Install dependencies

```
pip install -r requirements.txt
```

### Step 3 — Install the `wit` command

```
pip install -e .
```

After this step you can type `wit` from any directory (as long as the virtual environment is active).

> **Windows alternative (no pip install needed):**  
> Add the project folder to your PATH, then type `wit` — it will run `wit.bat` which calls `cli.py` directly.

---

## Running the Server

Open a terminal in the project root and run:

```
python -m uvicorn backend.main:app --reload
```

The server starts at **http://127.0.0.1:8000**.  
Interactive API docs are available at **http://127.0.0.1:8000/docs**.

---

## Using wit

Open a **second** terminal in the folder you want to track (can be any folder with `.py` files).

```bash
# 1. Initialise a repository
wit init

# 2. Stage files (use a filename or '.' for everything)
wit add .

# 3. Commit staged files
wit commit -m "Initial commit"

# 4. View commit history
wit log

# 5. Push to CodeGuard for analysis
wit push
```

After `wit push`:
- Warnings are printed in the terminal.
- A `code_analysis_report.png` file is saved in the current folder.

---

## API Endpoints

### `POST /analyze`

Accepts one or more Python source files and returns a **PNG image** containing all analysis graphs.

**Request:** `multipart/form-data` — field name `files`, one entry per file.  
**Response:** `image/png` — saved by the client as `code_analysis_report.png`.

---

### `POST /alerts`

Accepts the same files and returns a **JSON** object with structured warnings.

**Request:** `multipart/form-data` — field name `files`.  
**Response:**

```json
{
  "total": 3,
  "alerts": [
    {
      "file": "core.py",
      "line": 45,
      "error_type": "Missing Docstring",
      "message": "Function 'compare_folders' in 'core.py' at line 45 is missing a docstring."
    },
    {
      "file": "utils.py",
      "line": 12,
      "error_type": "Unused Variable",
      "message": "Variable 'temp' in 'utils.py' at line 12 is assigned but never used."
    }
  ]
}
```

---

## Quick Demo

```bash
# Terminal 1 — start the server
python -m uvicorn backend.main:app --reload

# Terminal 2 — run wit in some project folder
cd my_project
wit init
wit add .
wit commit -m "First push"
wit push
```
