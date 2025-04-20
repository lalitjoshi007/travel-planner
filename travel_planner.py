import whisper
import requests
import logging
import re
from typing import Optional

# Use lightweight Whisper model
whisper_model = whisper.load_model("base")

# Hugging Face config
HF_API_TOKEN = "your_huggingface_token_here"
HF_MODEL = "google/flan-t5-small"

logging.basicConfig(level=logging.INFO)

def generate_itinerary(
    destination: Optional[str] = "",
    days: Optional[int] = 0,
    interests: Optional[str] = "",
    budget: Optional[str] = "",
    num_people: Optional[int] = 0,
    style: Optional[str] = "",
    text_prompt: Optional[str] = "",
    audio_file_path: Optional[str] = None
):
    if not destination or days <= 0:
        return {"error": "Please provide a valid destination and number of days."}

    destination = destination.strip()
    interests = interests.strip() if interests else ""
    budget = budget.strip() if budget else ""
    style = style.strip() if style else ""
    text_prompt = text_prompt.strip() if text_prompt else ""

    transcribed_text = ""
    if audio_file_path:
        try:
            result = whisper_model.transcribe(audio_file_path)
            transcribed_text = result["text"].strip()
        except Exception as e:
            logging.error(f"Whisper transcription failed: {e}")
            return {"error": "Audio transcription failed."}

    full_prompt = f"Plan a {days}-day trip to {destination}. " \
                  f"Interests: {interests}. Budget: {budget}. Style: {style}. " \
                  f"Audio notes: {transcribed_text}. User says: {text_prompt}"

    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": full_prompt,
        "parameters": {"max_new_tokens": 1024, "temperature": 0.75}
    }

    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_MODEL}",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            logging.error(f"Hugging Face Error: {response.text}")
            return {"error": "Itinerary generation failed.", "details": response.text}

        result = response.json()
        text = result[0]['generated_text'] if isinstance(result, list) else result.get("generated_text", "")
        return {"itinerary": text}

    except Exception as e:
        logging.exception("Unexpected error during itinerary generation")
        return {"error": "An unexpected error occurred while generating the itinerary."}
