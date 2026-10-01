import json
import os
from typing import Any, Dict, List

import requests


def _json_response_from_text(text: str) -> Any:
    text = text.strip()
    if not text:
        return {}
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw_response": text}


def call_gemini(prompt: str, response_schema: str = "json") -> Dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError("MISSING_API_KEY")

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
    }

    if response_schema == "json":
        payload["generationConfig"] = {"responseMimeType": "application/json"}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
    except requests.RequestException as exc:
        raise RuntimeError("API_TEMPORARY_FAILURE") from exc

    if response.status_code == 401:
        raise ValueError("INVALID_API_KEY")
    if response.status_code in {429, 500, 502, 503, 504}:
        raise RuntimeError("API_TEMPORARY_FAILURE")
    if response.status_code >= 400:
        raise RuntimeError("INVALID_AI_RESPONSE")

    data = response.json()
    text = ""
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("INVALID_AI_RESPONSE")

    result = _json_response_from_text(text)
    if isinstance(result, dict):
        return result
    return {"result": result}


def generate_with_fallback(prompt: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return call_gemini(prompt, response_schema="json")
    except ValueError as exc:
        error_code = str(exc)
        if error_code == "MISSING_API_KEY":
            return {"status": "warning", "message": "AI service is not configured. Please check the Gemini API configuration.", "fallback": fallback}
        if error_code == "INVALID_API_KEY":
            return {"status": "warning", "message": "The AI service could not authenticate. Please verify the API configuration.", "fallback": fallback}
        return {"status": "warning", "message": "AI service is not configured. Please check the Gemini API configuration.", "fallback": fallback}
    except RuntimeError as exc:
        code = str(exc)
        if code == "API_TEMPORARY_FAILURE":
            return {"status": "warning", "message": "The AI service is temporarily unavailable. Please try again later.", "fallback": fallback}
        return {"status": "warning", "message": "The AI response could not be processed. Please try again.", "fallback": fallback}
