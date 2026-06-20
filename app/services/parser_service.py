import fitz
import pandas as pd
import docx


class ParserService:
    _reader = None

    @classmethod
    def get_reader(cls):
        if cls._reader is None:
            import easyocr
            cls._reader = easyocr.Reader(["en"])
        return cls._reader

    @staticmethod
    def parse_pdf(file_path):

        text = ""

        pdf = fitz.open(file_path)

        for page in pdf:
            text += page.get_text()

        return text

    @staticmethod
    def parse_docx(file_path):

        document = docx.Document(file_path)

        text = "\n".join(
            para.text
            for para in document.paragraphs
        )

        return text

    @staticmethod
    def parse_excel(file_path):
        if file_path.lower().endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        return df.to_string()

    @staticmethod
    def parse_image(file_path):
        reader = ParserService.get_reader()
        result = reader.readtext(
            file_path,
            detail=0
        )

        return "\n".join(result)

    @staticmethod
    def extract_text(file_path):

        file_path_lower = file_path.lower()
        if file_path_lower.endswith(".pdf"):
            return ParserService.parse_pdf(file_path)

        elif file_path_lower.endswith(".docx"):
            return ParserService.parse_docx(file_path)

        elif file_path_lower.endswith((".xlsx", ".xls", ".csv")):
            return ParserService.parse_excel(file_path)
        elif file_path_lower.endswith(
            (".jpg", ".jpeg", ".png")
        ):
            return ParserService.parse_image(file_path)

        raise Exception("Unsupported File Type")