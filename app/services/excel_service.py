import pandas as pd
from pathlib import Path


OUTPUT_FILE = "outputs/extracted_data.xlsx"


class ExcelService:

    @staticmethod
    def append_data(data):

        Path("outputs").mkdir(
            exist_ok=True
        )

        # Flatten the data structure for Excel
        flat_data = {
            "Filename": data.get("filename", ""),
            "Document Type": data.get("document_type", ""),
            "Summary": data.get("summary", ""),
        }

        # Format list fields as neat comma-separated strings
        dates = data.get("important_dates", [])
        if isinstance(dates, list):
            flat_data["Important Dates"] = ", ".join(map(str, dates))
        else:
            flat_data["Important Dates"] = str(dates)

        numbers = data.get("important_numbers", [])
        if isinstance(numbers, list):
            flat_data["Important Numbers"] = ", ".join(map(str, numbers))
        else:
            flat_data["Important Numbers"] = str(numbers)

        # Flatten the entities dictionary
        entities = data.get("entities", {})
        if isinstance(entities, dict):
            for k, v in entities.items():
                # Clean up display key
                clean_key = k.replace("_", " ").title()
                flat_data[f"Entity: {clean_key}"] = str(v)
        else:
            flat_data["Entities Raw"] = str(entities)

        try:
            existing = pd.read_excel(
                OUTPUT_FILE
            )
        except:
            existing = pd.DataFrame()

        new_row = pd.DataFrame([flat_data])

        # Concatenate keeping all columns, filling missing with NaN
        if not existing.empty:
            updated = pd.concat(
                [existing, new_row],
                ignore_index=True,
                sort=False
            )
        else:
            updated = new_row

        updated.to_excel(
            OUTPUT_FILE,
            index=False
        )