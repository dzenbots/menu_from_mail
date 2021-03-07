from mail_worker import *


def start_process():
    mw = MailWorker(server=IMAP_SERVER, save_dir=DIRECTORY_TO_SAVE_FILES)
    if mw.authorize(login=LOGIN, password=PASSWORD):
        print(mw.auth_status)
    folder_list = mw.get_folder_list()
    if MENU_FOLDER_NAME not in folder_list:
        print('Папка Меню не найдена. Завешение работы')
        return
    if not mw.select_folder(MENU_FOLDER_NAME):
        print('Проблема с открытием папки ' + MENU_FOLDER_NAME)
        return



if __name__ == "__main__":
    start_process()
