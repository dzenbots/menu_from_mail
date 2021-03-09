import json
import os
import random
import string

import requests
from bs4 import BeautifulSoup
from requests_toolbelt import MultipartEncoder


class SiteWorker1(requests.Session):

    def __init__(self, base='https://dmitrovsky.mskobr.ru'):
        super().__init__()
        self.base = base
        self.files_path = self.base + '/files'
        self.connected = False
        while not self.connected:
            try:
                self.headers.update({'Content-Type': 'text/html; charset=UTF-8'})
                self.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36'})
                self.headers.update({
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'})
                response = self.get(self.base)
                if response.status_code == 200:
                    self.connected = True
            except requests.exceptions.RequestException:
                print('One more time...')

    def authorize(self, login, password):
        self.login = login
        self.password = password
        try:
            response = self.get(self.base + '/login')
            soup = BeautifulSoup(response.text, 'html.parser')
            csrftoken = soup.find('input', dict(name='_csrf_token'))['value']
            self.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
            response = self.post(self.base + '/login_check', data={
                '_csrf_token': csrftoken,
                '_username': self.login,
                '_password': self.password,
                '_submit': 'Войти'
            })
            if response.status_code == 200:
                print('Authorization is complete!')
                return True
        except requests.exceptions.RequestException:
            print('Authorization error')
            return False

    def search_folder_id(self, root_folder_id, folder_path):
        cur_path_id = root_folder_id
        path = folder_path.split('/')
        search_folder_name = 'files'
        for i in range(1, len(path)):
            search_folder_name = path[i]
            files = {item.get('name'): item.get('hash') for item in self.get_file_info(cur_path_id).get('files')}
            if search_folder_name not in files.keys():
                print(f'Path {folder_path} does not exist!')
                return None
            cur_path_id = files.get(search_folder_name)
        return {search_folder_name: files.get(search_folder_name)}

    def get_file_info(self, id):
        self.headers.update({'Accept': 'application/json, text/javascript, */*; q=0.01'})
        response = self.get(self.base + '/elfinder/files')
        if response.status_code != 200:
            print('Something is wrong!')
            return
        request_str = self.base + '/efconnect/files?mode='
        request_str += f'&cmd=open&target={id}'
        response = self.get(request_str)
        return response.json()

    def get_url(self, url):
        return BeautifulSoup(self.get(self.base + url).text, 'html.parser').prettify()

    def proccess_upload(self, folder_path, filename, binary_file, fsize):
        request_str = self.base + '/efconnect/files'
        request_str += f'?mode=&cmd=upload&target={folder_path}&name[]:{filename}'
        response = self.get(request_str)
        if response.status_code == 200:

            m = MultipartEncoder(fields={
                'cmd': 'upload',
                'target': folder_path,
                'suffix': '~',
                'upload[]': (f'{filename}', binary_file, 'application/pdf'),
                'uploading_path[]': ''
            }, boundary='----WebKitFormBoundary' + ''.join(
                random.sample(string.ascii_letters + string.digits, 16)))
            self.headers.update(
                {'Content-Type': m.content_type})

            response = self.post(self.base + '/efconnect/files?mode=',
                                 data=m)

            if response.status_code == 200:
                print(response.json())
                print('File is uploaded')
            else:
                print(response.json())
                print('File was not uploaded')

    def upload_file(self, folder_path, file_path, root_folder_id):
        folder_info = self.search_folder_id(root_folder_id=root_folder_id,
                                            folder_path=folder_path)
        if folder_info:
            filename = os.path.basename(file_path)
            print(filename)
            fsize = os.stat(file_path).st_size
            print(fsize)
            with open(file_path, 'rb') as fb:
                binary_file = fb.read()
                key, value = folder_info.popitem()
                self.proccess_upload(folder_path=value, filename=filename, binary_file=fb, fsize=fsize)
                fb.close()


class SiteWorker(requests.Session):

    def __init__(self, base_url, login, password):
        super(SiteWorker, self).__init__()
        self.base_url = base_url
        self.login = login
        self.password = password
        self.authorized = False
        self.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36'})
        while True:
            try:
                self.response = self.get(url=self.base_url)
                if self.response.status_code == 200:
                    print('Web-site is allowed')
                    break
            except requests.exceptions.RequestException:
                print('Trying one more time')
        print('Authorization...', end='')
        while not self.authorized:
            while True:
                try:
                    self.response = self.get(url=self.base_url + '/login')
                    break
                except requests.exceptions.RequestException:
                    print('.', end='')
            self.csrf_token = BeautifulSoup(self.response.text, 'html.parser'). \
                find('input', dict(name='_csrf_token'))['value']
            self.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
            try:
                self.response = self.post(url=self.base_url + '/login_check', data={
                    '_csrf_token': self.csrf_token,
                    '_username': self.login,
                    '_password': self.password,
                    '_submit': 'Войти'
                })
            except requests.exceptions.RequestException:
                print('.', end='')
            if self.response.status_code == 200:
                print(' OK')
                self.authorized = True

    def get_file_info(self, filename, file_id):
        print(f'Trying to get file info {filename}...', end='')
        self.headers.update({'Accept': 'application/json, text/javascript, */*; q=0.01'})
        while True:
            try:
                self.response = self.get(url=self.base_url + '/efconnect/files', params={
                    'cmd': 'open',
                    'target': file_id
                })
            except requests.exceptions.RequestException:
                print('.', end='')
            if self.response.status_code == 200:
                break
            print('.', end='')
        print(' OK')
        return self.response.json()

    def upload_file(self, folder_path, files, root_folder_id):
        folder_info = self.search_folder(root_folder_id=root_folder_id,
                                         folder_path=folder_path)
        if folder_info:
            key, value = folder_info.popitem()
            for file_path in files:
                self.process_uploading(folder_id=value, file_path=file_path)

    def search_folder(self, root_folder_id, folder_path):
        cur_path_id = root_folder_id
        path = folder_path.split('/')
        search_folder_name = 'files'
        files = {}
        for i in range(1, len(path)):
            search_folder_name = path[i]
            files = {item.get('name'): item.get('hash') for item in
                     self.get_file_info(filename=search_folder_name, file_id=cur_path_id).get('files')}
            if search_folder_name not in files.keys():
                print(f' NO Path {folder_path} does not exist!')
                return None
            cur_path_id = files.get(search_folder_name)
        return {search_folder_name: cur_path_id}

    def process_uploading(self, folder_id, file_path):
        filename = os.path.basename(file_path)
        print(f'Trying to upload file {filename}...', end='')
        while True:
            try:
                self.response = self.get(url=self.base_url + '/efconnect/files', params={
                    'cmd': 'upload',
                    'target': folder_id,
                    'name[]': filename
                })
            except requests.exceptions.RequestException:
                print('.', end='')
            if self.response.status_code == 200:
                break
        multipart = MultipartEncoder(fields={
            'cmd': 'upload',
            'target': folder_id,
            'suffix': '~',
            'upload[]': (f'{filename}', open(file_path, 'rb'), 'application/pdf'),
            'uploading_path[]': ''
        }, boundary='----WebKitFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16)))
        try:
            self.response = self.post(url=self.base_url + '/efconnect/files',
                                      data=multipart,
                                      headers={'Content-Type': multipart.content_type})
        except requests.exceptions.RequestException:
            print('.', end='')
        if self.response.status_code == 200:
            print(' OK')
            # print(json.dumps(self.response.json(), sort_keys=True, indent=4))
