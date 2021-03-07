import datetime
import email
import imaplib
import shlex
from collections import namedtuple
from email.header import decode_header, make_header

from .imaputf7 import imaputf7decode, imaputf7encode

File = namedtuple("File", [
    'filename',
    'content'
])

Message = namedtuple('Message', [
    'id',
    'subject',
    'date',
    'from_user',
    'file'
])


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

    def get_messages_from_folder(self):
        status, data = self.mail.search(None, "ALL")
        if status == 'OK':
            messages = []
            ids = data[0].split()
            for i in range(len(ids) - 1, -1, -1):
                cur_id = ids[i]
                status, data = self.mail.fetch(cur_id, "(RFC822)")
                if status == 'OK':
                    raw_message = (data[0][1]).decode('utf-8')
                    message = email.message_from_string(raw_message)
                    for part in message.walk():
                        if 'application' in part.get_content_type().split('/'):
                            messages.append(Message(
                                id=cur_id,
                                subject=make_header(decode_header(message['Subject'])),
                                date=datetime.datetime.strptime(str(make_header(decode_header(message['Date']))),
                                                                '%a, %d %b %Y %H:%M:%S %z'),
                                from_user=make_header(decode_header(message['From'])),
                                file=File(filename=part.get_filename(),
                                          content=part.get_payload(decode=True)),

                            ))
                    self.mail.copy(cur_id, imaputf7encode('Выложено'))
                    self.mail.store(cur_id, '+FLAGS', '\Deleted')

                    self.mail.expunge()

            return messages
        return None

    def disconnect(self):
        self.mail.close()
        self.mail.logout()
