# DocuExcel - AI Document Data Extractor

Extract unstructured documents into flat Excel sheets using an LLM-powered pipeline.

---

## What this project does

This project accepts documents (PDF, DOCX, images, spreadsheets), extracts textual content, runs an LLM to identify key metadata, and appends the results into an Excel file. It provides a small web UI to upload files, preview the current Excel dataset, clear data, and download the generated spreadsheet.

This project provides:

- A REST backend (FastAPI) that handles uploads, runs parsing and LLM extraction, and stores results in an Excel file.
- A minimal frontend UI for uploading documents, previewing the current Excel rows, clearing the sheet, and downloading the Excel file.

## Features

- Upload documents via the web UI or the `/upload` endpoint.
- Automatic text extraction via `ParserService` (document parsing in `app/services/parser_service.py`).
- LLM-based information extraction via `LLMService` (see `app/services/llm_service.py`).
- Results are flattened and appended to `outputs/extracted_data.xlsx` by `ExcelService`.
- Preview current rows using the UI (GET `/api/data`).
- Download the Excel (`GET /api/download`) or clear data (`POST /api/clear`).

## Repository layout

- `app/`
  - `main.py` — FastAPI app and static mount
  - `api/routes.py` — API endpoints: `/upload`, `/api/data`, `/api/download`, `/api/clear`
  - `services/` — service modules
    - `parser_service.py` — extract text from files
    - `llm_service.py` — call LLM to extract structured JSON
    - `excel_service.py` — flatten and append rows to Excel
  - `static/` — frontend assets (`index.html`, `app.js`, `style.css`)
- `outputs/` — generated Excel files (created at runtime)
- `uploads/` — temporary uploaded files
- `requirements.txt` — Python dependencies

## Requirements / Prerequisites

- Python 3.10+ (use a virtualenv or `.venv`).
- Git (optional, for cloning).
- A SarvamAI API key (used by `LLMService`). Set `SARVAM_API_KEY` in a `.env` file or environment.

## Quick setup (development)

1. Clone the repo and enter the folder:

```bash
git clone https://github.com/ATRI-llm/doc_to_excel_extractor
cd doc_to_excel_extractor
```

2. (Recommended) Create and activate a virtual environment:

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Add environment variables. Create a `.env` file in the project root with:

```
SARVAM_API_KEY=your_api_key_here
```

5. Start the app (development server):

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

6. Open the UI in your browser at `http://localhost:8000/` (or `http://<host_ip>:8000/`).

## How the Excel columns are chosen

- The backend expects the LLM to return a JSON object like:

```json
{
  "document_type": "",
  "summary": "",
  "entities": { },
  "important_dates": [],
  "important_numbers": []
}
```

- `ExcelService.append_data()` (in `app/services/excel_service.py`) maps the LLM output into Excel columns:
  - Fixed columns: `Filename`, `Document Type`, `Summary`, `Important Dates`, `Important Numbers`.
  - Dynamic entity columns: each key in the `entities` dict becomes `Entity: {Clean Key}` (e.g. `vendor_name` -> `Entity: Vendor Name`). New entity columns are added automatically when new keys appear.

## Endpoints (quick reference)

- POST `/upload` — multipart upload. Form field `file` is required. This saves the file to `uploads/`, extracts text, calls the LLM, and appends results to `outputs/extracted_data.xlsx`.
- GET `/api/data` — returns the current Excel rows as JSON.
- GET `/api/download` — downloads the Excel file `extracted_data.xlsx`.
- POST `/api/clear` — deletes the Excel file and clears uploaded files.

## Frontend

- The frontend (in `app/static`) calls the API endpoints. `app/static/app.js` handles:
  - Uploading via `/upload` (FormData)
  - Loading the table via `/api/data`
  - Clearing via `/api/clear`
  - Download redirect to `/api/download`

## Customization notes

- To enforce a strict Excel schema (whitelist or rename columns), modify `ExcelService.append_data()`.
- To change which columns are visible in the UI or how they are displayed, modify `renderTable()` in `app/static/app.js`.
- The LLM prompt and model are in `LLMService.extract_information()`; adapt the prompt to change extraction behavior.

## Troubleshooting

- If the frontend doesn’t pick up CSS/JS changes, do a hard refresh (Ctrl+F5) or clear the browser cache.
- Ensure `SARVAM_API_KEY` is set and valid; without it, `LLMService` will fallback to a safe default output.
- Check console logs where `uvicorn` runs for stack traces.
