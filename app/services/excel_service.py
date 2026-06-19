import pandas as pd
from pathlib import Path


OUTPUT_FILE = "outputs/extracted_data.xlsx"


class ExcelService:

    @staticmethod
    def append_data(data):

        Path("outputs").mkdir(
            exist_ok=True
        )

        try:

            existing = pd.read_excel(
                OUTPUT_FILE
            )

        except:

            existing = pd.DataFrame()

        new_row = pd.DataFrame([data])

        updated = pd.concat(
            [existing, new_row],
            ignore_index=True
        )

        updated.to_excel(
            OUTPUT_FILE,
            index=False
        )