from pathlib import Path
import pandas as pd

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from app.services.parser_service import (
    ParserService
)

from app.services.llm_service import (
    LLMService
)

from app.services.excel_service import (
    ExcelService,
    OUTPUT_FILE
)

router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    Path("uploads").mkdir(
        exist_ok=True
    )

    file_path = (
        f"uploads/{file.filename}"
    )

    with open(
        file_path,
        "wb"
    ) as f:

        content = await file.read()

        f.write(content)

    try:
        text = ParserService.extract_text(
            file_path
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse document: {str(e)}")

    structured_data = (
        LLMService.extract_information(
            text
        )
    )

    structured_data["filename"] = (
        file.filename
    )

    ExcelService.append_data(
        structured_data
    )

    return {
        "status": "success",
        "data": structured_data
    }


@router.get("/api/data")
async def get_excel_data():
    try:
        path = Path(OUTPUT_FILE)
        if not path.exists():
            return []

        df = pd.read_excel(OUTPUT_FILE)
        records = df.to_dict(orient="records")
        
        import math
        for row in records:
            for k, v in row.items():
                if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                    row[k] = None
                elif pd.isna(v):
                    row[k] = None
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read data: {str(e)}")


@router.get("/api/download")
async def download_excel():
    path = Path(OUTPUT_FILE)
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="Excel file not found. Upload some documents first."
        )
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="extracted_document_data.xlsx"
    )


@router.post("/api/clear")
async def clear_data():
    path = Path(OUTPUT_FILE)
    if path.exists():
        try:
            path.unlink()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete Excel file: {str(e)}"
            )

    # Clean up uploaded files in uploads folder
    uploads_dir = Path("uploads")
    if uploads_dir.exists():
        for file in uploads_dir.iterdir():
            if file.is_file():
                try:
                    file.unlink()
                except Exception:
                    pass

    return {
        "status": "success",
        "message": "Excel file and uploads cleared"
    }