import datetime
import email
import imaplib
import os
import shlex
from email.header import decode_header, make_header
from typing import NamedTuple

from pylovepdf.tools.compress import Compress

from .settings import PUBLIC_API_KEY1, PUBLIC_API_KEY2
from .imaputf7 import imaputf7decode, imaputf7encode


class File(NamedTuple):
    filename: str
    content: bytes


class MessageSubject(NamedTuple):
    theme: str
    uk: str
    date: datetime.datetime


class Message(NamedTuple):
    id: int
    subject: MessageSubject
    date: datetime.datetime
    from_user: str
    file: File


class MailWorker:
    auth_status: str

    def __init__(self, server, save_dir, menu_folder_name):
        self.server = server
        self.mail = imaplib.IMAP4_SSL(self.server)
        self.save_dir = save_dir
        self.menu_folder_name = menu_folder_name

    def authorize(self, login: str, password: str) -> bool:
        print(f'Authenticating into {login}...', end='\t')
        try:
            status, message = self.mail.login(login, password)
        except:
            print('Authentication failed')
            self.auth_status = message[0].decode()
            return False
        if status == 'OK':
            self.auth_status = message[0].decode()
            return True
        return False

    @staticmethod
    def get_message_subject(subject: str):
        return MessageSubject(
            theme=subject.split(' ')[0].upper(),
            uk='UK' + subject.split(' ')[1].split('УК')[-1],
            date=datetime.datetime.strptime(subject.split(' ')[-1], "%d.%m.%Y")
        )

    def get_folder_list(self) -> list[str]:
        status, folder_list = self.mail.list()
        if status == 'OK':
            return [shlex.split(imaputf7decode(folder.decode()))[-1] for folder in folder_list]
        else:
            return []

    def select_folder(self, folder_name) -> bool:
        status, data = self.mail.select(imaputf7encode(folder_name))
        if status == 'OK':
            return True
        else:
            return False

    def complete_message(self, id, message, part):
        return Message(
            id=id,
            subject=self.get_message_subject(str(make_header(decode_header(message['Subject'])))),
            date=datetime.datetime.strptime(
                str(make_header(decode_header(message['Date']))), '%a, %d %b %Y %H:%M:%S %z'
            ),
            from_user=str(make_header(decode_header(message['From']))),
            file=File(filename=part.get_filename(),
                      content=part.get_payload(decode=True))
        )

    def process_message(self, id):
        status, data = self.mail.fetch(id, "(RFC822)")
        messages = list()
        if status == 'OK':
            raw_message = (data[0][1]).decode('utf-8')
            message = email.message_from_string(raw_message)
            for part in message.walk():
                if 'application' in part.get_content_type().split('/'):
                    messages.append(self.complete_message(id=id,
                                                          message=message,
                                                          part=part))
            return messages
        return list()

    def get_messages_from_folder(self) -> list[Message]:
        status, data = self.mail.search(None, "ALL")
        if status == 'OK':
            messages = list()
            ids = data[0].split()
            for i in range(len(ids) - 1, -1, -1):
                messages += self.process_message(id=ids[i])
            return messages
        return list()

    def disconnect(self) -> None:
        self.get_folder_list()
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


def get_public_key(date=datetime.date.today()) -> str:
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
