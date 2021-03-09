import os

from dotenv import load_dotenv

load_dotenv()


BASE_SCHOOL_SITE_ADDR = os.environ.get('BASE_SCHOOL_SITE_ADDR')
SITE_LOGIN = os.environ.get('SITE_LOGIN')
SITE_PASSWORD = os.environ.get('SITE_PASSWORD')

ROOT_FOLDER = os.environ.get('ROOT_FOLDER')
MENU_FOLDER_PATH_IN_SITE_STORAGE = os.environ.get('MENU_FOLDER_PATH_IN_SITE_STORAGE')
