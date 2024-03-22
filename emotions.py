import json
import os
import struct
import wave

import requests

from config import AUDIOS_FOLDER, SPLIT_AUDIOS, RESULT_EMOTIONS_FILE, EMOTIONS_API_KEY, EMOTIONS_API_KEY_PASSWORD, \
    API_EMOTIONS_URL


def split_audio(file):
    with wave.open(file, 'rb') as audio_file:
        sampwidth = audio_file.getsampwidth()
        channels = audio_file.getnchannels()
        framerate = audio_file.getframerate()
        nframes = audio_file.getnframes()
        samples = audio_file.readframes(nframes)
        basename = os.path.splitext(os.path.basename(file))[0]

    values = list(struct.unpack(f"<{nframes * channels}h", samples))
    left_channel = values[::2]  # client
    right_channel = values[1::2]  # operator

    def create_file(name_suffix, values):
        file_name = os.path.join(SPLIT_AUDIOS, f"{basename}_{name_suffix}.wav")
        with wave.open(file_name, 'wb') as out_file:
            out_file.setframerate(framerate)
            out_file.setsampwidth(sampwidth)
            out_file.setnchannels(1)
            audio_data = struct.pack(f"<{len(values)}h", *values)
            out_file.writeframes(audio_data)
        return file_name

    client_file = create_file('client', left_channel)
    operator_file = create_file('operator', right_channel)

    return [client_file, operator_file]


def get_emotions(file):
    params = {
        "outputType": "json",
        "sensitivity": "normal",
        "dummyResponse": "false",
        "apiKey": EMOTIONS_API_KEY,
        "apiKeyPassword": EMOTIONS_API_KEY_PASSWORD,
        "consentObtainedFromDataSubject": "true",
    }

    files = {"file": open(file, "rb")}

    response = requests.post(API_EMOTIONS_URL, files=files, data=params)
    if response.status_code == 200:
        data = response.json().get("data", {}).get("reports", {})
        for report in data.values():
            if 'profile' in report:
                return {emotion: details['averageLevel'] for emotion, details in report['profile'].items() if
                        'averageLevel' in details}

        return None

    else:
        print(f"Error: {response.status_code}")
        return None


if __name__ == '__main__':
    data = {"data": []}

    for file in os.listdir(AUDIOS_FOLDER):
        file_to_split = os.path.join(AUDIOS_FOLDER, file)

        client_filepath, operator_filepath = split_audio(file_to_split)

        client_emotion = get_emotions(client_filepath)
        operator_emotion = get_emotions(operator_filepath)

        data["data"].append({
            "dialog": file,
            "moods": {
                "client mood": client_emotion,
                "operator mood": operator_emotion
            }
        })

    with open(RESULT_EMOTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
