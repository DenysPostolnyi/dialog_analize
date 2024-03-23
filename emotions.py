import json
import os
import struct
import wave

import requests

from config import AUDIOS_FOLDER, SPLIT_AUDIOS, RESULT_EMOTIONS_FILE, EMOTIONS_API_KEY, EMOTIONS_API_KEY_PASSWORD, \
    API_EMOTIONS_URL, workbook_emotions, FILE_EMOTIONS


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
    row = 2
    sheet = workbook_emotions.active

    for file in os.listdir(AUDIOS_FOLDER):
        file_to_split = os.path.join(AUDIOS_FOLDER, file)

        client_filepath, operator_filepath = split_audio(file_to_split)

        client_emotion = get_emotions(client_filepath)
        operator_emotion = get_emotions(operator_filepath)

        sheet.cell(row=row, column=1, value=file)
        sheet.cell(row=row, column=2, value="Абонент")
        sheet.cell(row=row + 1, column=2, value="Оператор")

        sheet.cell(row=row, column=3, value=client_emotion['aggression'])
        sheet.cell(row=row + 1, column=3, value=operator_emotion['aggression'])

        sheet.cell(row=row, column=4, value=client_emotion['anticipation'])
        sheet.cell(row=row + 1, column=4, value=operator_emotion['anticipation'])

        sheet.cell(row=row, column=5, value=client_emotion['arousal'])
        sheet.cell(row=row + 1, column=5, value=operator_emotion['arousal'])

        sheet.cell(row=row, column=6, value=client_emotion['atmosphere'])
        sheet.cell(row=row + 1, column=6, value=operator_emotion['atmosphere'])

        sheet.cell(row=row, column=7, value=client_emotion['concentration'])
        sheet.cell(row=row + 1, column=7, value=operator_emotion['concentration'])

        sheet.cell(row=row, column=8, value=client_emotion['energy'])
        sheet.cell(row=row + 1, column=8, value=operator_emotion['energy'])

        sheet.cell(row=row, column=9, value=client_emotion['excitement'])
        sheet.cell(row=row + 1, column=9, value=operator_emotion['excitement'])

        sheet.cell(row=row, column=10, value=client_emotion['hesitation'])
        sheet.cell(row=row + 1, column=10, value=operator_emotion['hesitation'])

        sheet.cell(row=row, column=11, value=client_emotion['imagination'])
        sheet.cell(row=row + 1, column=11, value=operator_emotion['imagination'])

        sheet.cell(row=row, column=12, value=client_emotion['joy'])
        sheet.cell(row=row + 1, column=12, value=operator_emotion['joy'])

        sheet.cell(row=row, column=13, value=client_emotion['mentalEffort'])
        sheet.cell(row=row + 1, column=13, value=operator_emotion['mentalEffort'])

        sheet.cell(row=row, column=14, value=client_emotion['overallCognitiveActivity'])
        sheet.cell(row=row + 1, column=14, value=operator_emotion['overallCognitiveActivity'])

        sheet.cell(row=row, column=15, value=client_emotion['sad'])
        sheet.cell(row=row + 1, column=15, value=operator_emotion['sad'])

        sheet.cell(row=row, column=16, value=client_emotion['stress'])
        sheet.cell(row=row + 1, column=16, value=operator_emotion['stress'])

        sheet.cell(row=row, column=17, value=client_emotion['uncertainty'])
        sheet.cell(row=row + 1, column=17, value=operator_emotion['uncertainty'])

        sheet.cell(row=row, column=18, value=client_emotion['uneasy'])
        sheet.cell(row=row + 1, column=18, value=operator_emotion['uneasy'])

        row += 2
        workbook_emotions.save(FILE_EMOTIONS)

    print("Success")
