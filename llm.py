import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def ask(prompt: str) -> str:
    resp = _client.models.generate_content(model=MODEL, contents=prompt)
    return (resp.text or "").strip()


def ask_json(prompt: str) -> dict:
    resp = _client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    try:
        return json.loads(resp.text)
    except Exception:
        return {}