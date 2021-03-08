import json

import requests
from bs4 import BeautifulSoup


class SiteWorker(requests.Session):

    def __init__(self, base='https://dmitrovsky.mskobr.ru'):
        super().__init__()
        self.base = base
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
            # print(soup.prettify())
            csrftoken = soup.find('input', dict(name='_csrf_token'))['value']
            # print('OK')
            self.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
            # self.headers.update({'Cookie': response.headers.get('Cookie')})
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

    def get_tomorrow_menu_folder(self, id):
        self.headers.update({'Accept': 'application/json, text/javascript, */*; q=0.01'})
        # self.headers.update({'Cookie': self.cooks})
        # print(self.headers)
        self.tomorrow_menu_folder_id = id
        response = self.get(self.base + '/elfinder/files')
        # print(BeautifulSoup(self.get(self.base + '/elfinder/files').text, 'html.parser').prettify())
        if response.status_code != 200:
            print('Something is wrong!')
            return
        # print(response.headers)
        # response = self.get(self.base + '/efconnect/files?mode=',
        #                     json={
        #                         # 'mode': '',
        #                         'cmd': 'open',
        #                         'target': 'l1_TWFpbg',
        #                         'init': '1',
        #                         'tree': '1',
        #                         '_': '1615205264856'
        #                     })
        request_str = self.base + '/efconnect/files?mode='
        request_str += f'&cmd=open&target={id}'
        response = self.get(request_str)
        # )
        # print(response.status_code)
        print(json.dumps(response.json(), sort_keys=True, indent=4))

    def get_url(self, url):
        return BeautifulSoup(self.get(self.base + url).text, 'html.parser').prettify()
