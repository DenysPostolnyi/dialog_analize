import requests

from config import URL, workbook, CHAT_URL, FILE_NAME, client

prompt = """
        Ти асистент, який проводить семантичний аналіз діалогу за такими крітериями:
-	Чіткість та зрозумілість висловленої думки (оцінка від 0 до 10, якщо не 10 - чому)
-	Повнота (чи надалась уся необхідна інформація) (так або ні, якщо ні - чому)
-	Зрозумілість (наскільки легко зрозуміти вміст діалогу) (оцінка від 0 до 10, якщо не 10 - чому)
-	На скільки ефективне та швидке було вирішення проблеми (оцінка від 0 до 10, якщо не 10 - чому)
-	Активне слухання з боку оператора (оцінка від 0 до 10, якщо не 10 - чому)
-	Аналіз настрою оператора та абонента (оцінка від 0 до 10 для кожного, якщо не 10 - чому)
-	Перевірка чи сказав оператор необхідну інформацію. Обов' язково: привітання, спитати чи потрібна ще допомога, прощання.(Так чи ні, якщо не сказав щось, написати що саме)
-	Короткий опис діалогу та його результат (обов'язково)
-	Слова паразити оператора (перелік. Не включати сюди смайли)
-	Помилки оператора (перелік)
-	Класифікація: фінанси, обслуговування, відключення, ремонт, ПА - Повторна активація (перепідключення), підключення (обрати щось з цього)
-   Загальний рейтинг оператора (оцінка від 0 до 10)

Тобі надаватиметься діалог, ти маєш за цими параметрами провести аналіз та надати звіт Українською. Кожний пункт відокремити "-" напочатку строки, щоб краще читалося.

Також необхідно, щоб ти зібрав усі оцінки (Загальний рейтинг оператора, Чіткість та зрозумілість висловленої думки оператора, Повнота оператора, Зрозумілість оператора, На скільки ефективне та швидке було вирішення проблеми, Активне слухання з боку оператора, Аналіз настрою оператора, чи сказав оператор необхідну інформацію, Слова паразити оператора (відокремити []), класифікація). Для цього напиши останнім рядком "--" потім наступним рядком через кому повтори оцінки у такому порядку як я задав. Не забудь додати перелік слів паразитів та відокремити квадратними дужками список цих слів.
Наприклад (тільки у такій послідовності):
--10, 8, Так, 7, 7, 8, 7, Так, ["тоді", "якщо", "там", "для цього", "то"], обслуговування
        """


def api_request():
    response = requests.get(URL)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None


def generate_text(dialogue):
    text_for_call = ""
    for replica in dialogue['messages']:
        text_for_call += f"{replica['type']}: {replica['message']}\n"
    return text_for_call


def call_to_gpt(prompt_to_gpt, message_text):
    response = client.chat.completions.create(model="gpt-3.5-turbo-0125",
                                              messages=[
                                                  {"role": "system", "content": prompt_to_gpt},
                                                  {"role": "user", "content": message_text},
                                              ])
    print("Used to analyze tokens: ", response.usage.total_tokens)
    return [response.choices, response.usage.total_tokens]


def chats():
    response_data = api_request()

    if response_data:
        dialogs = 1
        counter = 2

        for item in response_data['data']:
            sheet = workbook.active

            text = generate_text(item)
            result, tokens = call_to_gpt(text, prompt)
            operator_name = ''
            for message in item['messages']:
                if message['type'] == 'Оператор':
                    operator_name = message['name']

            points = result[0].message.content.split('--')[1]
            try:
                bad_words = points.split('[')[1].split(']')[0]
            except IndexError:
                bad_words = " - "
            before_bad_words = points.split(', [')[0].split(', ')
            try:
                type_of_chat = points.split('], ')[1]
            except IndexError:
                all_items = points.split(', ')
                type_of_chat = all_items[len(all_items) - 1]

            chat_id = item['id']
            chat_url = CHAT_URL + str(chat_id)

            with open('result_chats.txt', 'a', encoding='utf-8') as file:
                file.write("<========================================>\n")
                file.write(f"Dialog {dialogs}\n")
                file.write(f"{text}\n")
                file.write(f"Analyze: \n")
                file.write(f"{result[0].message.content.split('--')[0]}\n")
                file.write("<========================================>\n")

            while True:
                if sheet[f'A{counter}'].value:
                    if sheet[f'A{counter}'].value == chat_url:
                        break
                    counter += 1
                else:
                    sheet.cell(row=counter, column=1, value=chat_url)
                    sheet.cell(row=counter, column=2, value=operator_name)
                    sheet.cell(row=counter, column=3, value=before_bad_words[0])
                    sheet.cell(row=counter, column=4, value=before_bad_words[1])
                    sheet.cell(row=counter, column=5, value=before_bad_words[2])
                    sheet.cell(row=counter, column=6, value=before_bad_words[3])
                    sheet.cell(row=counter, column=7, value=before_bad_words[4])
                    sheet.cell(row=counter, column=8, value=before_bad_words[5])
                    sheet.cell(row=counter, column=9, value=before_bad_words[6])
                    sheet.cell(row=counter, column=10, value=before_bad_words[7])
                    sheet.cell(row=counter, column=11, value=bad_words)
                    sheet.cell(row=counter, column=12, value=type_of_chat)
                    break

            workbook.save(FILE_NAME)

            dialogs += 1
        print("Success")
    else:
        print("Error during making call to API.")


if __name__ == '__main__':
    chats()
    # audios()
