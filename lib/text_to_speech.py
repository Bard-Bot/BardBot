import json
import base64
URL = "https://texttospeech.googleapis.com/v1/text:synthesize"


def make_headers(token):
    return {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "charset": "utf-8"
    }


def make_body(input_data, voice, audio_config) -> dict:
    return {
        "input": input_data,
        "voice": voice,
        "audioConfig": audio_config,
    }


def make_input_data(text) -> dict:
    return {
        "text": text,
    }


def make_voice(language_code, name) -> dict:
    return {
        "languageCode": language_code,
        "name": name,
    }


def make_audio_config(rate, pitch) -> dict:
    return {
        "audioEncoding": "LINEAR16",
        "speakingRate": rate,
        "sampleRateHertz": 48000,
        "pitch": pitch
    }


async def fetch_voice_json(session, body, headers) -> dict:
    async with session.post(URL, json=body, headers=headers) as r:
        text = await r.text()

    return json.loads(text)


def decode_content(base64_content) -> bytes:
    """decode base64 data."""
    return base64.b64decode(base64_content)


def remove_header(content) -> bytes:
    """Remove LINER16(WAVE) header. It's length is 44."""
    return content[44:]


async def fetch_voice_data(session, token, text,
                           language_code, name, rate, pitch):
    headers = make_headers(token)
    body = make_body(
        input_data=make_input_data(text),
        voice=make_voice(language_code, name),
        audio_config=make_audio_config(rate, pitch)
    )
    data = await fetch_voice_json(session, body, headers)

    return remove_header(decode_content(data['audioContent']))
