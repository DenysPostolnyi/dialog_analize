import os
import time

import winsound

from api import call_to_gpt
from config import model, AUDIOS_QUESTIONNAIRE_FOLDER, workbook_questionnaire, FILE_QUESTIONNAIRE, DEVICE

prompt = """
        Ти асистент, який проводить семантичний аналіз діалогу та аналізує відповіді абонента. Це опросник на тему, де клієнт бачив рекламу.
        Потрібно відокремити за такими параметрами: 
        - абонент згадав сам, абонент згадав після нагадування, абонент не згадав взагалі
        - якщо абонент не згадав, просто прочерк, якщо згадав - такі параметри: У будинку - Наліпки, У будинку - Паперовий буклет, У будинку Таблички на під'їздах, На вулиці - Білборд, В інтернеті - Ютуб, На вулиці - Авто співробітника, На вулиці - Форма співробітника, В інтернеті - Окружний ТГ канал, В інтернеті - ФБ, На вулиці - Паперовий буклет
        
        Відповідь дай за таким прикладом:
        абонент згадав сам,У будинку - Наліпки|абонент згадав сам,У будинку - Паперовий буклет|абонент згадав після нагадування,В інтернеті - Ютуб
        
        або
        
        не згадав взагалі,-
        
        Якщо абонент каже, що не пам'ятає, або не бачив, не вигадуй нічого, просто став що не згадав, або не вписуй у перелік місць місце якого абонент не згадував. Якщо абоненту нагадують якісь місця, але він не згадує, став таку відповідь: "нагадали про (тут напиши про що саме нагадали, але пиши про те, що питав оператор),абонент не згадав".
        """


def get_text_from_audio(audio_file_name):
    result = model.transcribe(f"{AUDIOS_QUESTIONNAIRE_FOLDER}/{audio_file_name}", language="uk", fp16=False,
                              prompt="Зроби максимально якісну транскрибацію діалогу")

    segments = result['segments']
    tokens = 0
    for segment in segments:
        tokens += len(segment['tokens'])
    print("Tokens from audio: ", tokens)
    return [result["text"], tokens]


if __name__ == '__main__':
    dialogs = 1
    counter = 2
    start_time = time.time()
    total_tokens = 0
    print("Device: ", DEVICE)
    for audio in os.listdir(AUDIOS_QUESTIONNAIRE_FOLDER):
        tokens_per_request = 0
        try:
            # get text from audio
            print(f"Started extracting {dialogs} audio from file {audio}")
            result_text, tokens_from_audio = get_text_from_audio(audio)
            tokens_per_request += tokens_from_audio
            print("Result:")
            print(result_text)
            print("<>")

            # get info about questionnaire
            print("Started request to OpenAI")
            result, text_tokens = call_to_gpt(prompt, result_text)
            tokens_per_request += text_tokens
            print("Result:")
            print(result[0].message.content)
            formatted_result = result[0].message.content.split("|")
            print("Tokens per audio: ", tokens_per_request)
            print("<===================================================>")

            # save to excel
            sheet = workbook_questionnaire.active
            while True:
                if sheet[f'A{counter}'].value:
                    if sheet[f'A{counter}'].value == audio:
                        sheet.cell(row=counter, column=1, value=audio)
                        sheet.cell(row=counter, column=2, value=None)
                        for item in formatted_result:
                            text_to_paste = f"{item.split(',')[0]} - {item.split(',')[1]}\n"
                            sheet.cell(row=counter, column=2,
                                       value=sheet[f'B{counter}'].value + text_to_paste if sheet[
                                           f'B{counter}'].value else text_to_paste)
                        sheet.cell(row=counter, column=3, value=result_text)
                        sheet.cell(row=counter, column=4, value=tokens_per_request)
                        break
                    counter += 1
                else:
                    sheet.cell(row=counter, column=1, value=audio)
                    for item in formatted_result:
                        text_to_paste = f"{item.split(',')[0]} - {item.split(',')[1]}\n"
                        sheet.cell(row=counter, column=2,
                                   value=sheet[f'B{counter}'].value + text_to_paste if sheet[
                                       f'B{counter}'].value else text_to_paste)
                    sheet.cell(row=counter, column=3, value=result_text)
                    sheet.cell(row=counter, column=4, value=tokens_per_request)
                    break

            workbook_questionnaire.save(FILE_QUESTIONNAIRE)
            total_tokens += tokens_per_request
            dialogs += 1
        except RuntimeError as e:
            print(e)
            break

    end_time = time.time()
    print("Finish")
    print(f"Analysed {dialogs - 1} dialogs")
    print(f"Elapsed time: {end_time - start_time}")
    winsound.Beep(440, 1000)  # Проиграть звук частотой 440 Гц в течение 1 секунды
