import os

from dotenv import load_dotenv

load_dotenv()

LOGIN = os.environ.get('LOGIN')
PASSWORD = os.environ.get('PASSWORD')

IMAP_SERVER = os.environ.get('IMAP_SERVER')

DIRECTORY_TO_SAVE_FILES = os.environ.get('DIRECTORY_TO_SAVE_FILES')

MENU_FOLDER_NAME = os.environ.get('MENU_FOLDER_NAME')

BASE_SCHOOL_SITE_ADDR = os.environ.get('BASE_SCHOOL_SITE_ADDR')
SITE_LOGIN = os.environ.get('SITE_LOGIN')
SITE_PASSWORD = os.environ.get('SITE_PASSWORD')

TOMORROW_MENU_FOLDER_ID = os.environ.get('TOMORROW_MENU_FOLDER_ID')
