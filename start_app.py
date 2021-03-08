import os

from prettytable import PrettyTable

from mail_worker import *


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
    sw = SiteWorker(base=BASE_SCHOOL_SITE_ADDR)
    if sw.connected:
        if not sw.authorize(login=SITE_LOGIN, password=SITE_PASSWORD):
            pass
        else:
            sw.get_tomorrow_menu_folder(id=TOMORROW_MENU_FOLDER_ID)
            # print(sw.get_url('/private_office/adverts'))
