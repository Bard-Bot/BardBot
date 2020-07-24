import json
import base64
URL = "https://texttospeech.googleapis.com/v1/text:synthesize"


async def fetch_voice_json(session, body, headers) -> dict:
    async with session.post(URL, json=body, headers=headers) as r:
        text = await r.text()

    return json.loads(text)


async def fetch_voice_data(session, token, text,
                           language_code, name, rate, pitch):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "charset": "utf-8"
    }
    body = {
        "input": {
            "text": text,
        },
        "voice": {
            "languageCode": language_code,
            "name": name,
        },
        "audioConfig": {
            "audioEncoding": "LINEAR16",
            "speakingRate": rate,
            "sampleRateHertz": 48000,
            "pitch": pitch
        },
    }
    data = await fetch_voice_json(session, body, headers)

    return base64.b64decode(data['audioContent'])[44:]  # Remove LINER16(WAVE) header. It's length is 44.
