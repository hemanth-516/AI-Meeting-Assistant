import requests

GRANITE_API_KEY = "your_ibm_api_key"
BASE_URL = "https://your-region.watsonx.ai/api"

def transcribe_audio(audio_path):
    with open(audio_path, 'rb') as f:
        response = requests.post(
            f"{BASE_URL}/v1/speech-to-text",
            headers={"Authorization": f"Bearer {GRANITE_API_KEY}"},
            files={"audio": f}
        )
    return response.json()['text']

def analyze_transcript(transcript):
    prompt = f"""
    Summarize this meeting, extract action items, and generate a follow-up email.
    Meeting Transcript:
    {transcript}
    """
    response = requests.post(
        f"{BASE_URL}/v1/generate-text",
        headers={
            "Authorization": f"Bearer {GRANITE_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model_id": "granite-3-3-instruct",
            "input": prompt,
            "parameters": {"temperature": 0.7}
        }
    )
    result = response.json()['generated_text']
    # Basic splitting logic (or improve with regex)
    return {
        "summary": result.split("Action Items:")[0].strip(),
        "actions": result.split("Action Items:")[1].split("Follow-up Email:")[0].strip(),
        "email": result.split("Follow-up Email:")[1].strip()
    }
