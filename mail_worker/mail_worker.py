import imaplib
import shlex

from .imaputf7 import imaputf7decode, imaputf7encode


class MailWorker:
    auth_status: str
    folder_menu_status: str

    def __init__(self, server, save_dir):
        self.server = server
        self.mail = imaplib.IMAP4_SSL(self.server)
        self.save_dir = save_dir

    def authorize(self, login: str, password: str):
        print(f'Authenticating into {login}...', end='\t')
        status, message = self.mail.login(login, password)
        if status == 'OK':
            self.auth_status = message[0].decode()
            return True
        return False

    def get_folder_list(self):
        status, folder_list = self.mail.list()
        if status == 'OK':
            return [shlex.split(imaputf7decode(folder.decode()))[-1] for folder in folder_list]
        else:
            return None

    def select_folder(self, folder_name):
        status, data = self.mail.select(imaputf7encode(folder_name))
        if status == 'OK':
            return True
        else:
            return False

