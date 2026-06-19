import fitz
import pandas as pd
import docx
import easyocr


reader = easyocr.Reader(["en"])


class ParserService:

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

        df = pd.read_excel(file_path)

        return df.to_string()

    @staticmethod
    def parse_image(file_path):

        result = reader.readtext(
            file_path,
            detail=0
        )

        return "\n".join(result)

    @staticmethod
    def extract_text(file_path):

        if file_path.endswith(".pdf"):
            return ParserService.parse_pdf(file_path)

        elif file_path.endswith(".docx"):
            return ParserService.parse_docx(file_path)

        elif file_path.endswith(".xlsx"):
            return ParserService.parse_excel(file_path)

        elif file_path.endswith(
            (".jpg", ".jpeg", ".png")
        ):
            return ParserService.parse_image(file_path)

        raise Exception("Unsupported File Type")