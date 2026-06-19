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
            ]
        )

        content = response.choices[0].message.content

        try:
            return json.loads(content)

        except Exception:

            return {
                "document_type": "unknown",
                "summary": content,
                "entities": {},
                "important_dates": [],
                "important_numbers": []
            }