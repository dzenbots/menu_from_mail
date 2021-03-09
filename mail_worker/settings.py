import os

from dotenv import load_dotenv

load_dotenv()

LOGIN = os.environ.get('LOGIN')
PASSWORD = os.environ.get('PASSWORD')

IMAP_SERVER = os.environ.get('IMAP_SERVER')

DIRECTORY_TO_SAVE_FILES = os.environ.get('DIRECTORY_TO_SAVE_FILES')

MENU_FOLDER_NAME = os.environ.get('MENU_FOLDER_NAME_IN_MAIL_BOX')

