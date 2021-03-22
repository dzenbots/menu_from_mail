import datetime
import email
import imaplib
import os
import shlex
from collections import namedtuple
from email.header import decode_header, make_header

from pylovepdf.tools.compress import Compress

from . import PUBLIC_API_KEY1, PUBLIC_API_KEY2
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
        self.menu_folder_name = folder_name
        status, data = self.mail.select(imaputf7encode(folder_name))
        if status == 'OK':
            return True
        else:
            return False

    def get_messages_from_folder(self):
        status, data = self.mail.search(None, "ALL")
        if status == 'OK':
            messages = list()
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
                    # self.mail.copy(cur_id, imaputf7encode('Выложено'))
                    # self.mail.store(cur_id, '+FLAGS', '\Deleted')
            return messages
        return None

    def disconnect(self):
        folder_list = self.get_folder_list()
        self.select_folder(self.menu_folder_name)
        status, data = self.mail.search(None, "ALL")
        if status == 'OK':
            ids = data[0].split()
            for i in range(len(ids) - 1, -1, -1):
                cur_id = ids[i]
                self.mail.copy(cur_id, imaputf7encode('Выложено'))
                self.mail.store(cur_id, '+FLAGS', '\Deleted')
        self.mail.expunge()
        self.mail.close()
        self.mail.logout()


def get_public_key(date=datetime.date.today()):
    if int(str(date).split('-')[2]) % 2 == 0:
        return PUBLIC_API_KEY1
    else:
        return PUBLIC_API_KEY2


class PdfCompressor:

    def __init__(self, public_api_key=get_public_key()):
        self.compressor = Compress(public_api_key, verify_ssl=True, proxies=None)

    def compress_file(self, filepath, output_directory_path):
        self.compressor.add_file(filepath)
        self.compressor.compression_level = 'extreme'
        self.compressor.set_output_folder('./temp')
        self.compressor.execute()
        self.compressor.download()
        file_src = './temp/' + os.listdir('./temp')[0]
        file_destination = output_directory_path + '/' + os.path.basename(filepath)
        os.rename(file_src, file_destination)
        self.compressor.delete_current_task()

