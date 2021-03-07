from mail_worker import MailWorker, IMAP_SERVER, DIRECTORY_TO_SAVE_FILES, LOGIN, PASSWORD

mw = MailWorker(server=IMAP_SERVER, save_dir=DIRECTORY_TO_SAVE_FILES)
if mw.authorize(login=LOGIN, password=PASSWORD):
    print(mw.auth_status)
