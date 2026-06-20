import os
import json

from dotenv import load_dotenv
from sarvamai import SarvamAI


load_dotenv()


class LLMService:

    client = SarvamAI(
        api_subscription_key=os.getenv(
            "SARVAM_API_KEY"
        )
    )

    @staticmethod
    def extract_information(text: str):

        prompt = f"""
You are a document understanding system.

Extract all important information from the document.

Return ONLY valid JSON.

JSON format:

{{
    "document_type": "",
    "summary": "",
    "entities": {{}},
    "important_dates": [],
    "important_numbers": []
}}

Document:

{text}
"""

        response = LLMService.client.chat.completions(
            model="sarvam-105b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            reasoning_effort=None
        )

        content = response.choices[0].message.content.strip()

        # Clean up markdown code block wrapping if present
        cleaned_content = content
        if cleaned_content.startswith("```"):
            lines = cleaned_content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned_content = "\n".join(lines).strip()

        try:
            return json.loads(cleaned_content)

        except Exception:
            # Last-resort fallback: attempt to extract JSON structure if surrounded by text
            try:
                start = cleaned_content.find('{')
                end = cleaned_content.rfind('}')
                if start != -1 and end != -1:
                    return json.loads(cleaned_content[start:end+1])
            except Exception:
                pass

            return {
                "document_type": "unknown",
                "summary": content,
                "entities": {},
                "important_dates": [],
                "important_numbers": []
            }