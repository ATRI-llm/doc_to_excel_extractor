from pydantic import BaseModel


class ExtractionResponse(BaseModel):
    filename: str
    content: dict