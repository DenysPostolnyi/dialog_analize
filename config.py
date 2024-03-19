import os
from dotenv import load_dotenv, find_dotenv
import openpyxl


load_dotenv(dotenv_path=find_dotenv('.env'))

FILE_NAME = str(os.getenv('EXCEL_FILE'))
workbook = openpyxl.load_workbook(FILE_NAME)
URL: str = os.getenv('API_URL')
API_KEY: str = os.getenv('API_KEY')
CHAT_URL: str = os.getenv('CHAT_URL')
