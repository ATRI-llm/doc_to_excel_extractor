from pathlib import Path

from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File

from app.services.parser_service import (
    ParserService
)

from app.services.llm_service import (
    LLMService
)

from app.services.excel_service import (
    ExcelService
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

    text = ParserService.extract_text(
        file_path
    )

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