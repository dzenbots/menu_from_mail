import imaplib


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




