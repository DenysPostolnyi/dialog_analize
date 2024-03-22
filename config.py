import os
from dotenv import load_dotenv, find_dotenv
import openpyxl

load_dotenv(dotenv_path=find_dotenv('.env'))

FILE_NAME = str(os.getenv('EXCEL_FILE'))
workbook = openpyxl.load_workbook(FILE_NAME)
URL: str = os.getenv('API_URL')
API_KEY: str = os.getenv('API_KEY')
CHAT_URL: str = os.getenv('CHAT_URL')

AUDIOS_FOLDER = "audios/"

EMOTIONS_API_KEY: str = os.getenv('EMOTIONS_API_KEY')
EMOTIONS_API_KEY_PASSWORD: str = os.getenv('EMOTIONS_API_KEY_PASSWORD')
SPLIT_AUDIOS = "splits/"
RESULT_EMOTIONS_FILE = "emotions_results.json"
API_EMOTIONS_URL = "https://cloud.emlo.cloud/analysis/analyzeFile"
