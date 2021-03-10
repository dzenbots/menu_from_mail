import os

from prettytable import PrettyTable

from mail_worker import *
from site_worker import SiteWorker, BASE_SCHOOL_SITE_ADDR, SITE_LOGIN, SITE_PASSWORD, \
    MENU_FOLDER_PATH_IN_SITE_STORAGE, ROOT_FOLDER


def get_correct_filename(email_subject):
    return 'UK' + email_subject.split(' ')[1].split('УК')[-1] + '.pdf'


def start_process():
    mw = MailWorker(server=IMAP_SERVER, save_dir=DIRECTORY_TO_SAVE_FILES)
    if mw.authorize(login=LOGIN, password=PASSWORD):
        print(mw.auth_status)
    folder_list = mw.get_folder_list()
    if MENU_FOLDER_NAME not in folder_list:
        print('Папка с меню не найдена. Завешение работы')
        return
    if not mw.select_folder(MENU_FOLDER_NAME):
        print('Проблема с открытием папки ' + MENU_FOLDER_NAME)
        return
    messages = mw.get_messages_from_folder()
    if not messages:
        print('Нет сообщений с файлами меню')
        return
    table = PrettyTable(['ID', 'Тема письма', 'Дата получения письма', 'Отправитель'])
    for message in mw.get_messages_from_folder():
        with open(os.path.join(DIRECTORY_TO_SAVE_FILES, get_correct_filename(str(message.subject))), "wb") as fp:
            fp.write(message.file.content)
            fp.close()
        table.add_row([str(message.id), message.subject, message.date, message.from_user])

    print(table)
    mw.disconnect()


if __name__ == "__main__":
    # start_process()
    sw = SiteWorker(base_url=BASE_SCHOOL_SITE_ADDR, login=SITE_LOGIN, password=SITE_PASSWORD)
    if sw.authorized:
        sw.upload_file(folder_path=MENU_FOLDER_PATH_IN_SITE_STORAGE,
                       files=['./Menus/UK123456.pdf', './Menus/UK12345.pdf'],
                       root_folder_id=ROOT_FOLDER)
