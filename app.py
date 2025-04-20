from flask import Flask, request, jsonify
from travel_planner import generate_itinerary
import os

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.form
    destination = data.get("destination")
    days = int(data.get("days", 0))
    interests = data.get("interests", "")
    budget = data.get("budget", "")
    num_people = int(data.get("num_people", 1))
    style = data.get("style", "")
    text_prompt = data.get("text_prompt", "")

    audio_file = request.files.get("audio")
    audio_path = None
    if audio_file:
        audio_path = f"/tmp/{audio_file.filename}"
        audio_file.save(audio_path)

    result = generate_itinerary(
        destination=destination,
        days=days,
        interests=interests,
        budget=budget,
        num_people=num_people,
        style=style,
        text_prompt=text_prompt,
        audio_file_path=audio_path
    )

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 7860)))
